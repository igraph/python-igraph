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

#ifndef IGRAPHMODULE_EDGEOBJECT_H
#define IGRAPHMODULE_EDGEOBJECT_H

#include "preamble.h"

#include "graphobject.h"

/**
 * \ingroup python_interface_edge
 * \brief A structure representing an edge of a graph
 */
typedef struct {
  PyObject_HEAD
  igraphmodule_GraphObject* gref;
  igraph_int_t idx;
  long hash;
} igraphmodule_EdgeObject;

extern PyTypeObject* igraphmodule_EdgeType;

int igraphmodule_Edge_register_type(void);

int igraphmodule_Edge_Check(PyObject* obj);
PyObject* igraphmodule_Edge_New(igraphmodule_GraphObject *gref, igraph_int_t idx);
igraph_int_t igraphmodule_Edge_get_index_as_igraph_integer(igraphmodule_EdgeObject* self);

#endif
