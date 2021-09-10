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

#define Py_LIMITED_API 0x03060000

#include "convert.h"
#include "dfsiter.h"
#include "common.h"
#include "error.h"
#include "vertexobject.h"

/**
 * \ingroup python_interface
 * \defgroup python_interface_dfsiter DFS iterator object
 */

PyTypeObject* igraphmodule_DFSIterType;

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
  igraph_integer_t no_of_nodes, r;

  o = PyObject_GC_New(igraphmodule_DFSIterObject, igraphmodule_DFSIterType);
  Py_INCREF(g);
  o->gref = g;
  o->graph = &g->g;
  
  if (!PyLong_Check(root) && !igraphmodule_Vertex_Check(root)) {
    PyErr_SetString(PyExc_TypeError, "root must be integer or igraph.Vertex");
    return NULL;
  }
  
  no_of_nodes = igraph_vcount(&g->g);
  o->visited = (char*)calloc(no_of_nodes, sizeof(char));
  if (o->visited == 0) {
    PyErr_SetString(PyExc_MemoryError, "out of memory");
    return NULL;
  }
  
  if (igraph_stack_int_init(&o->stack, 100)) {
    PyErr_SetString(PyExc_MemoryError, "out of memory");
    return NULL;
  }

  if (igraph_vector_int_init(&o->neis, 0)) {
    PyErr_SetString(PyExc_MemoryError, "out of memory");
    igraph_stack_int_destroy(&o->stack);
    return NULL;
  }
  
  if (PyLong_Check(root)) {
    if (igraphmodule_PyObject_to_integer_t(root, &r)) {
      igraph_stack_int_destroy(&o->stack);
      igraph_vector_int_destroy(&o->neis);
      return NULL;
    }
  } else {
    r = ((igraphmodule_VertexObject*)root)->idx;
  }

  /* push the root onto the stack */
  if (igraph_stack_int_push(&o->stack, r) ||
      igraph_stack_int_push(&o->stack, 0) ||
      igraph_stack_int_push(&o->stack, -1)) {
    igraph_stack_int_destroy(&o->stack);
    igraph_vector_int_destroy(&o->neis);
    PyErr_SetString(PyExc_MemoryError, "out of memory");
    return NULL;
  }
  o->visited[r] = 1;
  
  if (!igraph_is_directed(&g->g)) {
    mode = IGRAPH_ALL;
  }

  o->mode = mode;
  o->advanced = advanced;
  
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
static int igraphmodule_DFSIter_traverse(igraphmodule_DFSIterObject *self,
				  visitproc visit, void *arg) {
  RC_TRAVERSE("DFSIter", self);
  Py_VISIT(self->gref);
  Py_VISIT(Py_TYPE(self));   /* needed because heap-allocated types are refcounted */
  return 0;
}

/**
 * \ingroup python_interface_dfsiter
 * \brief Clears the iterator's subobject (before deallocation)
 */
static int igraphmodule_DFSIter_clear(igraphmodule_DFSIterObject *self) {
  PyObject *tmp;

  PyObject_GC_UnTrack(self);
  
  tmp = (PyObject*)self->gref;
  self->gref = NULL;
  Py_XDECREF(tmp);

  igraph_stack_int_destroy(&self->stack);
  igraph_vector_int_destroy(&self->neis);
  free(self->visited);
  self->visited = 0;
  
  return 0;
}

/**
 * \ingroup python_interface_dfsiter
 * \brief Deallocates a Python representation of a given DFS iterator object
 */
static void igraphmodule_DFSIter_dealloc(igraphmodule_DFSIterObject* self) {
  PyTypeObject *tp = Py_TYPE(self);

  igraphmodule_DFSIter_clear(self);

  RC_DEALLOC("DFSIter", self);
  
  PyObject_GC_Del(self);
  Py_DECREF(tp);  /* needed because heap-allocated types are refcounted */
}

static PyObject* igraphmodule_DFSIter_iter(igraphmodule_DFSIterObject* self) {
  Py_INCREF(self);
  return (PyObject*)self;
}

static PyObject* igraphmodule_DFSIter_iternext(igraphmodule_DFSIterObject* self) {
  /* the design is to return the top of the stack and then proceed until
   * we have found an unvisited neighbor and push that on top */
  igraph_integer_t parent_out, dist_out, vid_out;
  igraph_bool_t any = 0;

  /* nothing on the stack, end of iterator */
  if (igraph_stack_int_empty(&self->stack)) {
    return NULL;
  }

  /* peek at the top element on the stack
   * because we save three things, pop 3 in inverse order and push them back */
  parent_out = igraph_stack_int_pop(&self->stack);
  dist_out = igraph_stack_int_pop(&self->stack);
  vid_out = igraph_stack_int_pop(&self->stack);
  igraph_stack_int_push(&self->stack, vid_out);
  igraph_stack_int_push(&self->stack, dist_out);
  igraph_stack_int_push(&self->stack, parent_out);

  /* look for neighbors until we find one or until we have exhausted the graph */
  while (!any && !igraph_stack_int_empty(&self->stack)) {
    igraph_integer_t parent = igraph_stack_int_pop(&self->stack);
    igraph_integer_t dist = igraph_stack_int_pop(&self->stack);
    igraph_integer_t vid = igraph_stack_int_pop(&self->stack);
    igraph_stack_int_push(&self->stack, vid);
    igraph_stack_int_push(&self->stack, dist);
    igraph_stack_int_push(&self->stack, parent);
    igraph_integer_t i, n;

    /* the values above are returned at at this stage. However, we must
     * prepare for the next iteration by putting the next unvisited
     * neighbor onto the stack */
    if (igraph_neighbors(self->graph, &self->neis, vid, self->mode)) {
      igraphmodule_handle_igraph_error();
      return NULL;
    }

    n = igraph_vector_int_size(&self->neis);
    for (i = 0; i < n; i++) {
      igraph_integer_t neighbor = VECTOR(self->neis)[i];
      /* new neighbor, push the next item onto the stack */
      if (self->visited[neighbor] == 0) {
        any = 1;
        self->visited[neighbor]=1;
        if (igraph_stack_int_push(&self->stack, neighbor) ||
            igraph_stack_int_push(&self->stack, dist+1) ||
            igraph_stack_int_push(&self->stack, vid)) {
          igraphmodule_handle_igraph_error();
          return NULL;
        }
        break;
      }
    }
    /* no new neighbors, end of subtree */
    if (!any) {
       igraph_stack_int_pop(&self->stack);
       igraph_stack_int_pop(&self->stack);
       igraph_stack_int_pop(&self->stack);
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
      parentobj = Py_None;
    }
    return Py_BuildValue("NnN", vertexobj, (Py_ssize_t) dist_out, parentobj);
  } else {
    return vertexobj;
  }
}

PyDoc_STRVAR(
  igraphmodule_DFSIter_doc,
  "igraph DFS iterator object"
);

int igraphmodule_DFSIter_register_type() {
  PyType_Slot slots[] = {
    { Py_tp_dealloc, igraphmodule_DFSIter_dealloc },
    { Py_tp_traverse, igraphmodule_DFSIter_traverse },
    { Py_tp_clear, igraphmodule_DFSIter_clear },
    { Py_tp_iter, igraphmodule_DFSIter_iter },
    { Py_tp_iternext, igraphmodule_DFSIter_iternext },
    { Py_tp_doc, (void*) igraphmodule_DFSIter_doc },
    { 0 }
  };

  PyType_Spec spec = {
    "igraph.DFSIter",                           /* name */
    sizeof(igraphmodule_DFSIterObject),         /* basicsize */
    0,                                          /* itemsize */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC,   /* flags */
    slots,                                      /* slots */
  };

  igraphmodule_DFSIterType = (PyTypeObject*) PyType_FromSpec(&spec);
  return igraphmodule_DFSIterType == 0;
}
