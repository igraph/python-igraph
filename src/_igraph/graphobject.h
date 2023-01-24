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

#ifndef PYTHON_GRAPHOBJECT_H
#define PYTHON_GRAPHOBJECT_H

#include "preamble.h"

#include <igraph.h>
#include "structmember.h"
#include "common.h"

extern PyTypeObject* igraphmodule_GraphType;

/**
 * \ingroup python_interface
 * \brief A structure containing all the fields required to access an igraph from Python
 */
typedef struct
{
  PyObject_HEAD
  // The graph object
  igraph_t g;
  // Python object to be called upon destruction
  PyObject* destructor;
  // Python object representing the sequence of vertices
  PyObject* vseq;
  // Python object representing the sequence of edges
  PyObject* eseq;
  // Python object of the weak reference list
  PyObject* weakreflist;
} igraphmodule_GraphObject;

int igraphmodule_Graph_register_type(void);

PyObject* igraphmodule_Graph_subclass_from_igraph_t(PyTypeObject* type, igraph_t *graph);
PyObject* igraphmodule_Graph_from_igraph_t(igraph_t *graph);

PyObject* igraphmodule_Graph_attributes(igraphmodule_GraphObject* self, PyObject* Py_UNUSED(_null));
PyObject* igraphmodule_Graph_vertex_attributes(igraphmodule_GraphObject* self, PyObject* Py_UNUSED(_null));
PyObject* igraphmodule_Graph_edge_attributes(igraphmodule_GraphObject* self, PyObject* Py_UNUSED(_null));

#endif
