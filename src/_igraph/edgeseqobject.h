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

#ifndef PYTHON_EDGESEQOBJECT_H
#define PYTHON_EDGESEQOBJECT_H

#include "preamble.h"

#include "graphobject.h"

/**
 * \ingroup python_interface_edgeseq
 * \brief A structure representing the edge sequence of a graph
 */
typedef struct
{
  PyObject_HEAD
  igraphmodule_GraphObject* gref;
  igraph_es_t es;
  PyObject* weakreflist;
} igraphmodule_EdgeSeqObject;

extern PyTypeObject* igraphmodule_EdgeSeqType;

int igraphmodule_EdgeSeq_Check(PyObject* obj);
int igraphmodule_EdgeSeq_register_type(void);

#endif
