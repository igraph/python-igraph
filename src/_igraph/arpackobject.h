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

#ifndef PYTHON_ARPACKOBJECT_H
#define PYTHON_ARPACKOBJECT_H

#define Py_LIMITED_API 0x03060000
#include "preamble.h"

#include <igraph_arpack.h>
#include "graphobject.h"

/**
 * \ingroup python_interface
 * \defgroup python_interface_arpack ARPACK parameters object
 */

/**
 * \ingroup python_interface_arpack
 * \brief A structure representing ARPACK parameters
 */
typedef struct {
  PyObject_HEAD
  igraph_arpack_options_t params;
  igraph_arpack_options_t params_out;
} igraphmodule_ARPACKOptionsObject;

extern PyTypeObject* igraphmodule_ARPACKOptionsType;
extern PyObject* igraphmodule_arpack_options_default;

int igraphmodule_ARPACKOptions_register_type();

PyObject* igraphmodule_ARPACKOptions_new(void);
igraph_arpack_options_t *igraphmodule_ARPACKOptions_get(igraphmodule_ARPACKOptionsObject *self);

#endif
