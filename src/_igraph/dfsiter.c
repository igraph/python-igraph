/* -*- mode: C -*-  */
/* 
   IGraph library.
   Copyright (C) 2020  The igraph development team
   
   This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 2 of the License, or
   (at your option) any later version.
   
   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.
   
   You should have received a copy of the GNU General Public License
   along with this program; if not, write to the Free Software
   Foundation, Inc.,  51 Franklin Street, Fifth Floor, Boston, MA 
   02110-1301 USA

*/

#include "dfsiter.h"
#include "common.h"
#include "error.h"
#include "vertexobject.h"

/**
 * \ingroup python_interface
 * \defgroup python_interface_dfsiter DFS iterator object
 */

PyTypeObject igraphmodule_DFSIterType;

/**
 * \ingroup python_interface_dfsiter
 * \brief Allocate a new DFS iterator object for a given graph and a given root
 * \param g the graph object being referenced
 * \param vid the root vertex index
 * \param advanced whether the iterator should be advanced (returning distance and parent as well)
 * \return the allocated PyObject
 */
PyObject* igraphmodule_DFSIter_new(igraphmodule_GraphObject *g, PyObject *root, igraph_neimode_t mode, igraph_bool_t advanced) {
  igraphmodule_DFSIterObject* o;
  long int no_of_nodes, r;

  o=PyObject_GC_New(igraphmodule_DFSIterObject, &igraphmodule_DFSIterType);
  Py_INCREF(g);
  o->gref=g;
  o->graph=&g->g;
  
  if (!PyLong_Check(root) && !PyObject_IsInstance(root, (PyObject*)&igraphmodule_VertexType)) {
    PyErr_SetString(PyExc_TypeError, "root must be integer or igraph.Vertex");
    return NULL;
  }
  
  no_of_nodes=igraph_vcount(&g->g);
  o->visited=(char*)calloc(no_of_nodes, sizeof(char));
  if (o->visited == 0) {
    PyErr_SetString(PyExc_MemoryError, "out of memory");
    return NULL;
  }
  
  if (igraph_stack_init(&o->stack, 100)) {
    PyErr_SetString(PyExc_MemoryError, "out of memory");
    return NULL;
  }
  if (igraph_vector_init(&o->neis, 0)) {
    PyErr_SetString(PyExc_MemoryError, "out of memory");
    igraph_stack_destroy(&o->stack);
    return NULL;
  }
  
  if (PyLong_Check(root)) {
    r=PyLong_AsLong(root);
  } else {
    r = ((igraphmodule_VertexObject*)root)->idx;
  }
  /* push the root onto the stack */
  if (igraph_stack_push(&o->stack, r) ||
      igraph_stack_push(&o->stack, 0) ||
      igraph_stack_push(&o->stack, -1)) {
    igraph_stack_destroy(&o->stack);
    igraph_vector_destroy(&o->neis);
    PyErr_SetString(PyExc_MemoryError, "out of memory");
    return NULL;
  }
  o->visited[r] = 1;
  
  if (!igraph_is_directed(&g->g)) mode=IGRAPH_ALL;
  o->mode=mode;
  o->advanced=advanced;
  
  PyObject_GC_Track(o);
  
  RC_ALLOC("DFSIter", o);
  
  return (PyObject*)o;
}

/**
 * \ingroup python_interface_dfsiter
 * \brief Support for cyclic garbage collection in Python
 * 
 * This is necessary because the \c igraph.DFSIter object contains several
 * other \c PyObject pointers and they might point back to itself.
 */
int igraphmodule_DFSIter_traverse(igraphmodule_DFSIterObject *self,
				  visitproc visit, void *arg) {
  int vret;

  RC_TRAVERSE("DFSIter", self);
  
  if (self->gref) {
    vret=visit((PyObject*)self->gref, arg);
    if (vret != 0) return vret;
  }
  
  return 0;
}

/**
 * \ingroup python_interface_dfsiter
 * \brief Clears the iterator's subobject (before deallocation)
 */
int igraphmodule_DFSIter_clear(igraphmodule_DFSIterObject *self) {
  PyObject *tmp;

  PyObject_GC_UnTrack(self);
  
  tmp=(PyObject*)self->gref;
  self->gref = NULL;
  Py_XDECREF(tmp);

  igraph_stack_destroy(&self->stack);
  igraph_vector_destroy(&self->neis);
  free(self->visited);
  self->visited = 0;
  
  return 0;
}

/**
 * \ingroup python_interface_dfsiter
 * \brief Deallocates a Python representation of a given DFS iterator object
 */
void igraphmodule_DFSIter_dealloc(igraphmodule_DFSIterObject* self) {
  igraphmodule_DFSIter_clear(self);

  RC_DEALLOC("DFSIter", self);
  
  PyObject_GC_Del(self);
}

PyObject* igraphmodule_DFSIter_iter(igraphmodule_DFSIterObject* self) {
  Py_INCREF(self);
  return (PyObject*)self;
}

PyObject* igraphmodule_DFSIter_iternext(igraphmodule_DFSIterObject* self) {
  /* the design is to return the top of the stack and then proceed until
   * we have found an unvisited neighbor and push that on top */
  igraph_integer_t parent_out, dist_out, vid_out;
  igraph_bool_t any = 0;

  /* nothing on the stack, end of iterator */
  if(igraph_stack_empty(&self->stack)) {
    return NULL;
  }

  /* peek at the top element on the stack
   * because we save three things, pop 3 in inverse order and push them back */
  parent_out = (igraph_integer_t)igraph_stack_pop(&self->stack);
  dist_out = (igraph_integer_t)igraph_stack_pop(&self->stack);
  vid_out = (igraph_integer_t)igraph_stack_pop(&self->stack);
  igraph_stack_push(&self->stack, (long int) vid_out);
  igraph_stack_push(&self->stack, (long int) dist_out);
  igraph_stack_push(&self->stack, (long int) parent_out);

  /* look for neighbors until you found one or until you have exausted the graph */
  while (!any && !igraph_stack_empty(&self->stack)) {
    igraph_integer_t parent = (igraph_integer_t)igraph_stack_pop(&self->stack);
    igraph_integer_t dist = (igraph_integer_t)igraph_stack_pop(&self->stack);
    igraph_integer_t vid = (igraph_integer_t)igraph_stack_pop(&self->stack);
    igraph_stack_push(&self->stack, (long int) vid);
    igraph_stack_push(&self->stack, (long int) dist);
    igraph_stack_push(&self->stack, (long int) parent);
    long int i;
    /* the values above are returned at at this stage. However, we must
     * prepare for the next iteration by putting the next unvisited
     * neighbor onto the stack */
    if (igraph_neighbors(self->graph, &self->neis, vid, self->mode)) {
      igraphmodule_handle_igraph_error();
      return NULL;
    }
    for (i=0; i<igraph_vector_size(&self->neis); i++) {
      igraph_integer_t neighbor = (igraph_integer_t)VECTOR(self->neis)[i];
      /* new neighbor, push the next item onto the stack */
      if (self->visited[neighbor] == 0) {
        any = 1;
        self->visited[neighbor]=1;
        if (igraph_stack_push(&self->stack, neighbor) ||
            igraph_stack_push(&self->stack, dist+1) ||
            igraph_stack_push(&self->stack, vid)) {
          igraphmodule_handle_igraph_error();
          return NULL;
        }
        break;
      }
    }
    /* no new neighbors, end of subtree */
    if (!any) {
       igraph_stack_pop(&self->stack);
       igraph_stack_pop(&self->stack);
       igraph_stack_pop(&self->stack);
    }
  }

  /* no matter what the stack situation is: that is a worry for the next cycle
   * now just return the top of the stack as it was at the function entry */
  PyObject *vertexobj = igraphmodule_Vertex_New(self->gref, vid_out);
  if (self->advanced) {
    PyObject *parentobj;
    if (!vertexobj)
      return NULL;
    if (parent_out >= 0) {
      parentobj = igraphmodule_Vertex_New(self->gref, parent_out);
      if (!parentobj)
          return NULL;
    } else {
      Py_INCREF(Py_None);
      parentobj=Py_None;
    }
    return Py_BuildValue("NlN", vertexobj, (long int)dist_out, parentobj);
  } else {
    return vertexobj;
  }
}

/**
 * \ingroup python_interface_dfsiter
 * Method table for the \c igraph.DFSIter object
 */
PyMethodDef igraphmodule_DFSIter_methods[] = {
  {NULL}
};

/** \ingroup python_interface_dfsiter
 * Python type object referencing the methods Python calls when it performs various operations on
 * a DFS iterator of a graph
 */
PyTypeObject igraphmodule_DFSIterType =
{
  PyVarObject_HEAD_INIT(0, 0)
  "igraph.DFSIter",                         // tp_name
  sizeof(igraphmodule_DFSIterObject),       // tp_basicsize
  0,                                        // tp_itemsize
  (destructor)igraphmodule_DFSIter_dealloc, // tp_dealloc
  0,                                        // tp_print
  0,                                        // tp_getattr
  0,                                        // tp_setattr
  0,                                        /* tp_compare (2.x) / tp_reserved (3.x) */
  0,                                        // tp_repr
  0,                                        // tp_as_number
  0,                                        // tp_as_sequence
  0,                                        // tp_as_mapping
  0,                                        // tp_hash
  0,                                        // tp_call
  0,                                        // tp_str
  0,                                        // tp_getattro
  0,                                        // tp_setattro
  0,                                        // tp_as_buffer
  Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC, // tp_flags
  "igraph DFS iterator object",             // tp_doc
  (traverseproc) igraphmodule_DFSIter_traverse, /* tp_traverse */
  (inquiry) igraphmodule_DFSIter_clear,     /* tp_clear */
  0,                                        // tp_richcompare
  0,                                        // tp_weaklistoffset
  (getiterfunc)igraphmodule_DFSIter_iter,   /* tp_iter */
  (iternextfunc)igraphmodule_DFSIter_iternext, /* tp_iternext */
  0,                                        /* tp_methods */
  0,                                        /* tp_members */
  0,                                        /* tp_getset */
  0,                                        /* tp_base */
  0,                                        /* tp_dict */
  0,                                        /* tp_descr_get */
  0,                                        /* tp_descr_set */
  0,                                        /* tp_dictoffset */
  0,                                        /* tp_init */
  0,                                        /* tp_alloc */
  0,                                        /* tp_new */
  0,                                        /* tp_free */
};

