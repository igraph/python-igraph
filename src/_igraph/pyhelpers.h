/* vim:set ts=4 sw=2 sts=2 et:  */
/*
   IGraph library - Python interface.
   Copyright (C) 2006-2011  Tamas Nepusz <ntamas@gmail.com>
   5 Avenue Road, Staines, Middlesex, TW18 3AW, United Kingdom

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

#ifndef IGRAPHMODULE_HELPERS_H
#define IGRAPHMODULE_HELPERS_H

#include "preamble.h"

int igraphmodule_helpers_init();

int igraphmodule_PyFile_Close(PyObject* fileObj);
PyObject* igraphmodule_PyFile_FromObject(PyObject* filename, const char* mode);
PyObject* igraphmodule_PyList_NewFill(Py_ssize_t len, PyObject* item);
PyObject* igraphmodule_PyList_Zeroes(Py_ssize_t len);
char* igraphmodule_PyObject_ConvertToCString(PyObject* string);
PyObject* igraphmodule_PyRange_create(Py_ssize_t start, Py_ssize_t stop, Py_ssize_t step);
int PyUnicode_IsEqualToUTF8String(PyObject* py_string, const char* c_string);
long igraphmodule_Py_HashPointer(void *p);

#define PyBaseString_Check(o) (PyUnicode_Check(o) || PyBytes_Check(o))
#define PyUnicode_IsEqualToASCIIString(uni, string) \
        (PyUnicode_CompareWithASCIIString(uni, string) == 0)
char* PyUnicode_CopyAsString(PyObject* string);

#define PY_IGRAPH_ASSERT_AT_BUILD_TIME(condition) \
  ((void)sizeof(char[1 - 2*!(condition)]))
#define PY_IGRAPH_DEPRECATED(msg) \
  PyErr_WarnEx(PyExc_DeprecationWarning, (msg), 1)
#define PY_IGRAPH_WARN(msg) \
  PyErr_WarnEx(PyExc_RuntimeWarning, (msg), 1)

/* Calling Py_DECREF() on heap-allocated types in tp_dealloc was not needed
 * before Python 3.8 (see Python issue 35810) */
#define PY_FREE_AND_DECREF_TYPE(obj, base_type) {    \
  PyTypeObject* _tp = Py_TYPE(obj);       \
  ((freefunc)PyType_GetSlot(_tp, Py_tp_free))(obj); \
  Py_DECREF(_tp); \
}

#define CHECK_SSIZE_T_RANGE(value, message) {   \
  if ((value) < 0) {                             \
    PyErr_SetString(PyExc_ValueError, message " must be non-negative"); \
    return NULL;                                 \
  }                                              \
  if ((value) > IGRAPH_INTEGER_MAX) {            \
    PyErr_SetString(PyExc_OverflowError, message " too large"); \
    return NULL;                                 \
  } \
}

#define CHECK_SSIZE_T_RANGE_POSITIVE(value, message) {   \
  if ((value) <= 0) {                             \
    PyErr_SetString(PyExc_ValueError, message " must be positive"); \
    return NULL;                                 \
  }                                              \
  if ((value) > IGRAPH_INTEGER_MAX) {            \
    PyErr_SetString(PyExc_OverflowError, message " too large"); \
    return NULL;                                 \
  } \
}

#ifndef Py_None
/* This happens on PyPy where Py_None is not part of the public API. Let's
 * provide a replacement ourselves. */
#define PY_IGRAPH_PROVIDES_PY_NONE
#endif

#ifndef Py_True
/* It is unclear whether Py_True is part of the public API or not, so let's
 * prepare for the case when it is not. If Py_True is not part of the public
 * API, we assume that Py_False is not part of it either */
#define PY_IGRAPH_PROVIDES_BOOL_CONSTANTS
#endif

#ifdef PY_IGRAPH_PROVIDES_PY_NONE
extern PyObject* Py_None;
#endif

#ifdef PY_IGRAPH_PROVIDES_BOOL_CONSTANTS
extern PyObject* Py_True;
extern PyObject* Py_False;
#endif

#endif
