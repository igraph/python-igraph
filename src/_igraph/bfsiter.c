/* -*- mode: C -*-  */
/* 
   IGraph library.
   Copyright (C) 2006-2012  Tamas Nepusz <ntamas@gmail.com>
   
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

#include "bfsiter.h"
#include "common.h"
#include "convert.h"
#include "error.h"
#include "pyhelpers.h"
#include "vertexobject.h"

/**
 * \ingroup python_interface
 * \defgroup python_interface_bfsiter BFS iterator object
 */

PyTypeObject* igraphmodule_BFSIterType;

/**
 * \ingroup python_interface_bfsiter
 * \brief Allocate a new BFS iterator object for a given graph and a given root
 * \param g the graph object being referenced
 * \param vid the root vertex index
 * \param advanced whether the iterator should be advanced (returning distance and parent as well)
 * \return the allocated PyObject
 */
PyObject* igraphmodule_BFSIter_new(igraphmodule_GraphObject *g, PyObject *root, igraph_neimode_t mode, igraph_bool_t advanced) {
  igraphmodule_BFSIterObject* self;
  igraph_integer_t no_of_nodes, r;
  
  self = (igraphmodule_BFSIterObject*) PyType_GenericNew(igraphmodule_BFSIterType, 0, 0);
  if (!self) {
    return NULL;
  }

  Py_INCREF(g);
  self->gref = g;
  self->graph = &g->g;
  
  if (!PyLong_Check(root) && !igraphmodule_Vertex_Check(root)) {
    PyErr_SetString(PyExc_TypeError, "root must be integer or igraph.Vertex");
    return NULL;
  }
  
  no_of_nodes = igraph_vcount(&g->g);
  self->visited = (char*)calloc(no_of_nodes, sizeof(char));
  if (self->visited == 0) {
    PyErr_SetString(PyExc_MemoryError, "out of memory");
    return NULL;
  }
  
  if (igraph_dqueue_int_init(&self->queue, 100)) {
    PyErr_SetString(PyExc_MemoryError, "out of memory");
    return NULL;
  }

  if (igraph_vector_int_init(&self->neis, 0)) {
    PyErr_SetString(PyExc_MemoryError, "out of memory");
    igraph_dqueue_int_destroy(&self->queue);
    return NULL;
  }
  
  if (PyLong_Check(root)) {
    if (igraphmodule_PyObject_to_integer_t(root, &r)) {
      igraph_dqueue_int_destroy(&self->queue);
      igraph_vector_int_destroy(&self->neis);
      return NULL;
    }
  } else {
    r = ((igraphmodule_VertexObject*)root)->idx;
  }

  if (igraph_dqueue_int_push(&self->queue, r) ||
      igraph_dqueue_int_push(&self->queue, 0) ||
      igraph_dqueue_int_push(&self->queue, -1)) {
    igraph_dqueue_int_destroy(&self->queue);
    igraph_vector_int_destroy(&self->neis);
    PyErr_SetString(PyExc_MemoryError, "out of memory");
    return NULL;
  }
  self->visited[r] = 1;
  
  if (!igraph_is_directed(&g->g)) {
    mode=IGRAPH_ALL;
  }

  self->mode = mode;
  self->advanced = advanced;
  
  RC_ALLOC("BFSIter", self);
  
  return (PyObject*)self;
}

/**
 * \ingroup python_interface_bfsiter
 * \brief Support for cyclic garbage collection in Python
 * 
 * This is necessary because the \c igraph.BFSIter object contains several
 * other \c PyObject pointers and they might point back to itself.
 */
static int igraphmodule_BFSIter_traverse(igraphmodule_BFSIterObject *self,
				  visitproc visit, void *arg) {
  RC_TRAVERSE("BFSIter", self);
  Py_VISIT(self->gref);
#if PY_VERSION_HEX >= 0x03090000
  // This was not needed before Python 3.9 (Python issue 35810 and 40217)
  Py_VISIT(Py_TYPE(self));
#endif
  return 0;
}

/**
 * \ingroup python_interface_bfsiter
 * \brief Clears the iterator's subobject (before deallocation)
 */
int igraphmodule_BFSIter_clear(igraphmodule_BFSIterObject *self) {
  PyObject_GC_UnTrack(self);

  Py_CLEAR(self->gref);  

  igraph_dqueue_int_destroy(&self->queue);
  igraph_vector_int_destroy(&self->neis);

  free(self->visited);
  self->visited=0;
  
  return 0;
}

/**
 * \ingroup python_interface_bfsiter
 * \brief Deallocates a Python representation of a given BFS iterator object
 */
static void igraphmodule_BFSIter_dealloc(igraphmodule_BFSIterObject* self) {
  RC_DEALLOC("BFSIter", self);

  igraphmodule_BFSIter_clear(self);

  PY_FREE_AND_DECREF_TYPE(self, igraphmodule_BFSIterType);
}

static PyObject* igraphmodule_BFSIter_iter(igraphmodule_BFSIterObject* self) {
  Py_INCREF(self);
  return (PyObject*)self;
}

static PyObject* igraphmodule_BFSIter_iternext(igraphmodule_BFSIterObject* self) {
  if (!igraph_dqueue_int_empty(&self->queue)) {
    igraph_integer_t vid = igraph_dqueue_int_pop(&self->queue);
    igraph_integer_t dist = igraph_dqueue_int_pop(&self->queue);
    igraph_integer_t parent = igraph_dqueue_int_pop(&self->queue);
    igraph_integer_t i, n;
    
    if (igraph_neighbors(self->graph, &self->neis, vid, self->mode)) {
      igraphmodule_handle_igraph_error();
      return NULL;
    }

    n = igraph_vector_int_size(&self->neis);
    for (i = 0; i < n; i++) {
      igraph_integer_t neighbor = VECTOR(self->neis)[i];
      if (self->visited[neighbor] == 0) {
        self->visited[neighbor] = 1;
        if (igraph_dqueue_int_push(&self->queue, neighbor) ||
            igraph_dqueue_int_push(&self->queue, dist+1) ||
            igraph_dqueue_int_push(&self->queue, vid)) {
          igraphmodule_handle_igraph_error();
          return NULL;
        }
      }
    }

    if (self->advanced) {
      PyObject *vertexobj, *parentobj;
      vertexobj = igraphmodule_Vertex_New(self->gref, vid);
      if (!vertexobj)
        return NULL;
      if (parent >= 0) {
        parentobj = igraphmodule_Vertex_New(self->gref, parent);
        if (!parentobj)
            return NULL;
      } else {
        Py_INCREF(Py_None);
        parentobj=Py_None;
      }
      return Py_BuildValue("NnN", vertexobj, (Py_ssize_t)dist, parentobj);
    } else {
      return igraphmodule_Vertex_New(self->gref, vid);
    }
  } else {
    return NULL;
  }
}

PyDoc_STRVAR(
  igraphmodule_BFSIter_doc,
  "igraph BFS iterator object"
);

int igraphmodule_BFSIter_register_type() {
  PyType_Slot slots[] = {
    { Py_tp_dealloc, igraphmodule_BFSIter_dealloc },
    { Py_tp_traverse, igraphmodule_BFSIter_traverse },
    { Py_tp_clear, igraphmodule_BFSIter_clear },
    { Py_tp_iter, igraphmodule_BFSIter_iter },
    { Py_tp_iternext, igraphmodule_BFSIter_iternext },
    { Py_tp_doc, (void*) igraphmodule_BFSIter_doc },
    { 0 }
  };

  PyType_Spec spec = {
    "igraph.BFSIter",                           /* name */
    sizeof(igraphmodule_BFSIterObject),         /* basicsize */
    0,                                          /* itemsize */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC,   /* flags */
    slots,                                      /* slots */
  };

  igraphmodule_BFSIterType = (PyTypeObject*) PyType_FromSpec(&spec);
  return igraphmodule_BFSIterType == 0;
}
