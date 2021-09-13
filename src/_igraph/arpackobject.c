/* vim:set ts=4 sw=2 sts=2 et:  */
/* 
   IGraph library.
   Copyright (C) 2007-2012  Tamas Nepusz <ntamas@gmail.com>
   
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

#include "arpackobject.h"
#include "graphobject.h"
#include "error.h"

PyTypeObject* igraphmodule_ARPACKOptionsType;
PyObject* igraphmodule_arpack_options_default;

/**
 * \ingroup python_interface_arpack
 * \brief Allocates a new ARPACK parameters object
 */
PyObject* igraphmodule_ARPACKOptions_new() {
  igraphmodule_ARPACKOptionsObject* self;
  self = PyObject_New(igraphmodule_ARPACKOptionsObject, igraphmodule_ARPACKOptionsType);
  if (self) {
    igraph_arpack_options_init(&self->params);
    igraph_arpack_options_init(&self->params_out);
  }
  return (PyObject*)self;
}

/**
 * \ingroup python_interface_arpack
 * \brief Deallocates a Python representation of a given ARPACK parameters object
 */
static void igraphmodule_ARPACKOptions_dealloc(igraphmodule_ARPACKOptionsObject* self) {
  PyTypeObject *tp = Py_TYPE(self);
  PyObject_Del((PyObject*)self);
  Py_DECREF(tp);  /* needed because heap-allocated types are refcounted */
}

/** \ingroup python_interface_arpack
 * \brief Returns one of the attributes of a given ARPACK parameters object
 */
static PyObject* igraphmodule_ARPACKOptions_getattr(
  igraphmodule_ARPACKOptionsObject* self, char* attrname) {
  PyObject *result = NULL;

  if (strcmp(attrname, "bmat") == 0) {
    char buf[2] = { self->params_out.bmat[0], 0 };
    result=PyUnicode_FromString(buf);
  } else if (strcmp(attrname, "n") == 0) {
    result=PyLong_FromLong(self->params_out.n);
  } else if (strcmp(attrname, "which") == 0) {
    char buf[3] = { self->params.which[0], self->params.which[1], 0 };
    result=PyUnicode_FromString(buf);
  } else if (strcmp(attrname, "nev") == 0) {
    result=PyLong_FromLong(self->params.nev);
  } else if (strcmp(attrname, "tol") == 0) {
    result=PyFloat_FromDouble((double)self->params.tol);
  } else if (strcmp(attrname, "ncv") == 0) {
    result=PyLong_FromLong(self->params.ncv);
  } else if (strcmp(attrname, "ldv") == 0) {
    result=PyLong_FromLong(self->params.ldv);
  } else if (strcmp(attrname, "ishift") == 0) {
    result=PyLong_FromLong(self->params.ishift);
  } else if (strcmp(attrname, "maxiter") == 0 ||
		     strcmp(attrname, "mxiter") == 0) {
    result=PyLong_FromLong(self->params.mxiter);
  } else if (strcmp(attrname, "nb") == 0) {
    result=PyLong_FromLong(self->params.nb);
  } else if (strcmp(attrname, "mode") == 0) {
    result=PyLong_FromLong(self->params.mode);
  } else if (strcmp(attrname, "start") == 0) {
    result=PyLong_FromLong(self->params.start);
  } else if (strcmp(attrname, "sigma") == 0) {
    result=PyFloat_FromDouble((double)self->params.sigma);
  } else if (strcmp(attrname, "info") == 0) {
    result=PyLong_FromLong(self->params_out.info);
  } else if (strcmp(attrname, "iter") == 0) {
    result=PyLong_FromLong(self->params_out.iparam[2]);
  } else if (strcmp(attrname, "nconv") == 0) {
    result=PyLong_FromLong(self->params_out.iparam[4]);
  } else if (strcmp(attrname, "numop") == 0) {
    result=PyLong_FromLong(self->params_out.iparam[8]);
  } else if (strcmp(attrname, "numopb") == 0) {
    result=PyLong_FromLong(self->params_out.iparam[9]);
  } else if (strcmp(attrname, "numreo") == 0) {
    result=PyLong_FromLong(self->params_out.iparam[10]);
  } else {
    PyErr_SetString(PyExc_AttributeError, attrname);
  }
  return result;
}

/** \ingroup python_interface_arpack
 * \brief Sets one of the attributes of a given ARPACK parameters object
 */
static int igraphmodule_ARPACKOptions_setattr(
  igraphmodule_ARPACKOptionsObject* self, char* attrname,
  PyObject* value) {
  if (value == 0) {
    PyErr_SetString(PyExc_TypeError, "attribute can not be deleted");
    return -1;
  }
  if (strcmp(attrname, "maxiter") == 0 ||
      strcmp(attrname, "mxiter") == 0) {
    if (PyLong_Check(value)) {
      long int n=PyLong_AsLong(value);
      if (n>0)
          self->params.mxiter=(igraph_integer_t)n;
      else {
        PyErr_SetString(PyExc_ValueError, "maxiter must be positive");
        return -1;
      }
    } else {
      PyErr_SetString(PyExc_ValueError, "integer expected");
      return -1;
    }
  } else if (strcmp(attrname, "tol") == 0) {
    if (PyLong_Check(value)) {
      self->params.tol = (igraph_real_t) PyLong_AsLong(value);
    } else if (PyFloat_Check(value)) {
      self->params.tol = (igraph_real_t) PyFloat_AsDouble(value);
    } else {
      PyErr_SetString(PyExc_ValueError, "integer or float expected");
      return -1;
    }
  } else {
    PyErr_SetString(PyExc_AttributeError, attrname);
    return -1;
  }

  return 0;
}

/** \ingroup python_interface_arpack */
igraph_arpack_options_t *igraphmodule_ARPACKOptions_get(
  igraphmodule_ARPACKOptionsObject *self) {
  self->params_out = self->params;
  self->params_out.iparam[0] = self->params.ishift;
  self->params_out.iparam[2] = self->params.mxiter;
  self->params_out.iparam[3] = self->params.nb;
  self->params_out.iparam[6] = self->params.mode;
  self->params_out.lworkl = 0;
  self->params_out.info = self->params.start;

  return &self->params_out;
}

/** \ingroup python_interface_arpack
 * \brief Formats an \c igraph.ARPACKOptions object in a
 * human-consumable format.
 * 
 * \return the formatted textual representation as a \c PyObject
 */
PyObject* igraphmodule_ARPACKOptions_str(igraphmodule_ARPACKOptionsObject *self) {
  return PyUnicode_FromString("ARPACK parameters");
}

PyDoc_STRVAR(
  igraphmodule_ARPACKOptions_doc,
  "Class representing the parameters of the ARPACK module.\n\n"
  "ARPACK is a Fortran implementation of the implicitly restarted\n"
  "Arnoldi method, an algorithm for calculating some of the\n"
  "eigenvalues and eigenvectors of a given matrix. igraph uses this\n"
  "package occasionally, and this class can be used to fine-tune the\n"
  "behaviour of ARPACK in such cases.\n\n"
  "The class has several attributes which are not documented here,\n"
  "since they are usually of marginal use to the ordinary user.\n"
  "See the source code of the original ARPACK Fortran package\n"
  "(especially the file C{dsaupd.f}) for a detailed explanation of the\n"
  "parameters. Only the most basic attributes are explained here. Most\n"
  "of them are read only unless stated otherwise.\n\n"
  " - C{bmat}: type of the eigenproblem solved. C{'I'} means standard\n"
  "   eigenproblem (A*x = lambda*x), C{'G'} means generalized\n"
  "   eigenproblem (A*x = lambda*B*x).\n\n"
  " - C{n}: dimension of the eigenproblem\n\n"
  " - C{tol}: precision. If less than or equal to zero, the standard\n"
  "   machine precision is used as computed by the LAPACK utility\n"
  "   called C{dlamch}. This can be modified.\n\n"
  " - C{mxiter}: maximum number of update iterations to take. This\n"
  "   can be modified. You can also use C{maxiter}.\n\n"
  " - C{iter}: actual number of update iterations taken\n\n"
  " - C{numop}: total number of OP*x operations\n\n"
  " - C{numopb}: total number of B*x operations if C{bmat} is C{'G'}\n\n"
  " - C{numreo}: total number of steps of re-orthogonalization\n\n"
);

PyType_Slot igraphmodule_ARPACKOptions_slots[] = {
  { Py_tp_new, igraphmodule_ARPACKOptions_new },
  { Py_tp_dealloc, igraphmodule_ARPACKOptions_dealloc },
  { Py_tp_getattr, igraphmodule_ARPACKOptions_getattr },
  { Py_tp_setattr, igraphmodule_ARPACKOptions_setattr },
  { Py_tp_str, igraphmodule_ARPACKOptions_str },
  { Py_tp_doc, (void*) igraphmodule_ARPACKOptions_doc },
  { 0 }
};

/** \ingroup python_interface_arpack
 * Python type specification for \c igraph.ARPACKOptions
 */
PyType_Spec igraphmodule_ARPACKOptions_spec = {
  "igraph.ARPACKOptions",                     /* name */
  sizeof(igraphmodule_ARPACKOptionsObject),   /* basicsize */
  0,                                          /* itemsize */
  Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,   /* flags */
  igraphmodule_ARPACKOptions_slots,           /* slots */
};

int igraphmodule_ARPACKOptions_register_type() {
  igraphmodule_ARPACKOptionsType = (PyTypeObject*) PyType_FromSpec(&igraphmodule_ARPACKOptions_spec);
  return igraphmodule_ARPACKOptionsType == 0;
}
