/* -*- mode: C -*-  */
/*
   IGraph library.
   Copyright (C) 2006-2023  Tamas Nepusz <ntamas@gmail.com>

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

#ifndef IGRAPHMODULE_VERTEXOBJECT_H
#define IGRAPHMODULE_VERTEXOBJECT_H

#include "preamble.h"

#include "graphobject.h"

/**
 * \ingroup python_interface_vertex
 * \brief A structure representing a vertex of a graph
 */
typedef struct
{
  PyObject_HEAD
  igraphmodule_GraphObject* gref;
  igraph_int_t idx;
  long hash;
} igraphmodule_VertexObject;

extern PyTypeObject* igraphmodule_VertexType;

int igraphmodule_Vertex_register_type(void);

int igraphmodule_Vertex_Check(PyObject* obj);
PyObject* igraphmodule_Vertex_New(igraphmodule_GraphObject *gref, igraph_int_t idx);
igraph_int_t igraphmodule_Vertex_get_index_igraph_integer(igraphmodule_VertexObject* self);
PyObject* igraphmodule_Vertex_update_attributes(PyObject* self, PyObject* args, PyObject* kwds);

#endif
