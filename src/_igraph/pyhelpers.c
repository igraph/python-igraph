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

#include "pyhelpers.h"

/**
 * Closes a Python file-like object by calling its close() method.
 */
int igraphmodule_PyFile_Close(PyObject* fileObj) {
  PyObject *result;

  result = PyObject_CallMethod(fileObj, "close", 0);
  if (result) {
    Py_DECREF(result);
    return 0;
  } else {
    /* Exception raised already */
    return 1;
  }
}

/**
 * Creates a Python file-like object from a Python object storing a string and
 * an ordinary C string storing the mode to open the file in.
 */
PyObject* igraphmodule_PyFile_FromObject(PyObject* filename, const char* mode) {
  PyObject *ioModule, *fileObj;

  ioModule = PyImport_ImportModule("io");
  if (ioModule == 0)
    return 0;

  fileObj = PyObject_CallMethod(ioModule, "open", "Os", filename, mode);
  Py_DECREF(ioModule);

  return fileObj;
}

/**
 * Creates a Python list and fills it with a pre-defined item.
 * 
 * \param  len   the length of the list to be created
 * \param  item  the item with which the list will be filled
 */
PyObject* igraphmodule_PyList_NewFill(Py_ssize_t len, PyObject* item) {
	Py_ssize_t i;
	PyObject* result = PyList_New(len);

	if (result == 0)
		return 0;

	for (i = 0; i < len; i++) {
		Py_INCREF(item);
		PyList_SET_ITEM(result, i, item);  /* reference to item stolen */
	}

	return result;
}

/**
 * Creates a Python list and fills it with zeroes.
 * 
 * \param  len   the length of the list to be created
 */
PyObject* igraphmodule_PyList_Zeroes(Py_ssize_t len) {
	PyObject* zero = PyLong_FromLong(0);
	PyObject* result;

	if (zero == 0)
		return 0;

	result = igraphmodule_PyList_NewFill(len, zero);
	Py_DECREF(zero);
	return result;
}

/**
 * Converts a Python object to its string representation and returns it as
 * a C string.
 *
 * It is the responsibility of the caller to release the C string.
 */
char* igraphmodule_PyObject_ConvertToCString(PyObject* string) {
  char* result;

  if (string == 0)
    return 0;

  if (!PyBaseString_Check(string)) {
    string = PyObject_Str(string);
    if (string == 0)
      return 0;
  } else {
    Py_INCREF(string);
  }

  result = PyUnicode_CopyAsString(string);
  Py_DECREF(string);

  return result;
}

/**
 * Creates a Python range object with the given start and stop indices and step
 * size.
 *
 * The function returns a new reference. It is the responsibility of the caller
 * to release it. Returns \c NULL in case of an error.
 */
PyObject* igraphmodule_PyRange_create(Py_ssize_t start, Py_ssize_t stop, Py_ssize_t step) {
  static PyObject* builtin_module = 0;
  static PyObject* range_func = 0;
  PyObject* result;

  if (builtin_module == 0) {
    builtin_module = PyImport_ImportModule("builtins");
    if (builtin_module == 0) {
      return 0;
    }
  }

  if (range_func == 0) {
    range_func = PyObject_GetAttrString(builtin_module, "range");
    if (range_func == 0) {
      return 0;
    }
  }

  result = PyObject_CallFunction(range_func, "lll", start, stop, step);
  return result;
}

char* PyUnicode_CopyAsString(PyObject* string) {
  PyObject* bytes;
  char* result;

  if (PyBytes_Check(string)) {
    bytes = string;
    Py_INCREF(bytes);
  } else {
    bytes = PyUnicode_AsUTF8String(string);
  }

  if (bytes == 0)
    return 0;
  
  result = strdup(PyBytes_AS_STRING(bytes));
  Py_DECREF(bytes);

  if (result == 0)
    PyErr_NoMemory();

  return result;
}

int PyUnicode_IsEqualToUTF8String(PyObject* py_string,
		const char* c_string) {
	PyObject* c_string_conv;
	int result;

	if (!PyUnicode_Check(py_string))
		return 0;

	c_string_conv = PyUnicode_FromString(c_string);
	if (c_string_conv == 0)
		return 0;

	result = (PyUnicode_Compare(py_string, c_string_conv) == 0);
	Py_DECREF(c_string_conv);

	return result;
}

/**
 * Generates a hash value for a plain C pointer.
 *
 * This function is a copy of \c _Py_HashPointer from \c Objects/object.c in
 * the source code of Python's C implementation.
 */
long igraphmodule_Py_HashPointer(void *p) {
  long x;
  size_t y = (size_t)p;

  /* bottom 3 or 4 bits are likely to be 0; rotate y by 4 to avoid
   * excessive hash collisions for dicts and sets */
  y = (y >> 4) | (y << (8 * sizeof(p) - 4));
  x = (long)y;
  if (x == -1)
    x = -2;
  return x;
}
