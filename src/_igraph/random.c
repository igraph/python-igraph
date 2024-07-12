/* -*- mode: C -*-  */
/* vim:set ts=2 sw=2 sts=2 et: */
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

#include "random.h"
#include "pyhelpers.h"
#include <limits.h>
#include <igraph/igraph_random.h>

/**
 * \ingroup python_interface_rng
 * \brief Internal data structure for storing references to the
 *        functions and arguments used from Python's random number generator.
 */
typedef struct {
  PyObject* getrandbits_func;
  PyObject* randint_func;
  PyObject* random_func;
  PyObject* gauss_func;

  PyObject* rng_bits_as_pyobject;
  PyObject* zero_as_pyobject;
  PyObject* one_as_pyobject;
  PyObject* rng_max_as_pyobject;
} igraph_i_rng_Python_state_t;

#define RNG_BITS 32
#ifdef __wasm32__
  /* size_t is 32-bit on wasm32 so we cannot use the shift trick */
  #define RNG_MAX 0xFFFFFFFF
#else
  #define RNG_MAX ((((size_t) 1) << RNG_BITS) - 1)
#endif

static igraph_i_rng_Python_state_t igraph_rng_Python_state = {0};
static igraph_rng_t igraph_rng_Python = {
  /* type = */ 0, /* state = */ 0, /* is_seeded = */ 1
};
static igraph_rng_t igraph_rng_default_saved = {0};

igraph_error_t igraph_rng_Python_init(void **state) {
  IGRAPH_ERROR("Python RNG error, unsupported function called",
      IGRAPH_EINTERNAL);
  return IGRAPH_SUCCESS;
}

void igraph_rng_Python_destroy(void *state) {
  igraph_error("Python RNG error, unsupported function called",
      __FILE__, __LINE__, IGRAPH_EINTERNAL);
}

/**
 * \ingroup python_interface_rng
 * \brief Sets the random number generator used by igraph.
 */
PyObject* igraph_rng_Python_set_generator(PyObject* self, PyObject* object) {
  igraph_i_rng_Python_state_t new_state, old_state;
  PyObject* func;

  if (object == Py_None) {
    /* Reverting to the default igraph random number generator instead
     * of the Python-based one */
    igraph_rng_set_default(&igraph_rng_default_saved);
    Py_RETURN_NONE;
  }

#define GET_FUNC(name) { \
  func = PyObject_GetAttrString(object, name); \
  if (func == 0) {\
    return 0; \
  } else if (!PyCallable_Check(func)) { \
    PyErr_SetString(PyExc_TypeError, "'" name "' attribute must be callable"); \
    return 0; \
  } \
}

#define GET_OPTIONAL_FUNC(name) { \
  if (PyObject_HasAttrString(object, name)) { \
    func = PyObject_GetAttrString(object, name); \
    if (func == 0) { \
      return 0; \
    } else if (!PyCallable_Check(func)) { \
      PyErr_SetString(PyExc_TypeError, "'" name "' attribute must be callable"); \
      return 0; \
    } \
  } else { \
    func = 0; \
  } \
}

  GET_OPTIONAL_FUNC("getrandbits"); new_state.getrandbits_func = func;
  GET_FUNC("randint"); new_state.randint_func = func;
  GET_FUNC("random"); new_state.random_func = func;
  GET_FUNC("gauss"); new_state.gauss_func = func;

  /* construct the arguments of getrandbits(RNG_BITS) and randint(0, 2 ^ RNG_BITS-1)
   * in advance */
  new_state.rng_bits_as_pyobject = PyLong_FromLong(RNG_BITS);
  if (new_state.rng_bits_as_pyobject == 0) {
    return 0;
  }
  new_state.zero_as_pyobject = PyLong_FromLong(0);
  if (new_state.zero_as_pyobject == 0) {
    return 0;
  }
  new_state.one_as_pyobject = PyLong_FromLong(1);
  if (new_state.one_as_pyobject == 0) {
    return 0;
  }
  new_state.rng_max_as_pyobject = PyLong_FromSize_t(RNG_MAX);
  if (new_state.rng_max_as_pyobject == 0) {
    return 0;
  }

#undef GET_FUNC
#undef GET_OPTIONAL_FUNC

  old_state = igraph_rng_Python_state;
  igraph_rng_Python_state = new_state;
  Py_XDECREF(old_state.getrandbits_func);
  Py_XDECREF(old_state.randint_func);
  Py_XDECREF(old_state.random_func);
  Py_XDECREF(old_state.gauss_func);
  Py_XDECREF(old_state.rng_bits_as_pyobject);
  Py_XDECREF(old_state.zero_as_pyobject);
  Py_XDECREF(old_state.one_as_pyobject);
  Py_XDECREF(old_state.rng_max_as_pyobject);

  igraph_rng_set_default(&igraph_rng_Python);

  Py_RETURN_NONE;
}

/**
 * \ingroup python_interface_rng
 * \brief Sets the seed of the random generator.
 */
igraph_error_t igraph_rng_Python_seed(void *state, igraph_uint_t seed) {
  IGRAPH_ERROR("Python RNG error, unsupported function called",
      IGRAPH_EINTERNAL);
  return IGRAPH_SUCCESS;
}

/**
 * \ingroup python_interface_rng
 * \brief Generates an unsigned long integer using the Python random number generator.
 */
igraph_uint_t igraph_rng_Python_get(void *state) {
  PyObject* result;
  PyObject* exc_type;
  igraph_uint_t retval;

  if (igraph_rng_Python_state.getrandbits_func) {
    /* This is the preferred code path if the random module given by the user
     * supports getrandbits(); it is faster than randint() but still slower
     * than simply calling random() */
    result = PyObject_CallFunctionObjArgs(
      igraph_rng_Python_state.getrandbits_func,
      igraph_rng_Python_state.rng_bits_as_pyobject,
      0
    );
  } else {
    /* We want to avoid hitting this path at all costs because randint() is
     * very costly in the Python layer */
    result = PyObject_CallFunctionObjArgs(
      igraph_rng_Python_state.randint_func,
      igraph_rng_Python_state.zero_as_pyobject,
      igraph_rng_Python_state.rng_max_as_pyobject,
      0
    );
  }

  if (result == 0) {
    exc_type = PyErr_Occurred();
    if (exc_type == PyExc_KeyboardInterrupt) {
      /* KeyboardInterrupt is okay, we don't report it, just store it and let
       * the caller handler it at the earliest convenience */
    } else {
      /* All other exceptions are reported and cleared */
      PyErr_WriteUnraisable(exc_type);
      PyErr_Clear();
    }
    /* Fallback to the C random generator -- this should not happen */
    return rand() * RNG_MAX;
  } else {
    retval = PyLong_AsUnsignedLong(result);
    Py_DECREF(result);
    return retval;
  }
}

/**
 * \ingroup python_interface_rng
 * \brief Generates a real number between 0 and 1 using the Python random number generator.
 */
igraph_real_t igraph_rng_Python_get_real(void *state) {
  PyObject* exc_type;
  double retval;
  PyObject* result = PyObject_CallObject(igraph_rng_Python_state.random_func, 0);

  if (result == 0) {
    exc_type = PyErr_Occurred();
    if (exc_type == PyExc_KeyboardInterrupt) {
      /* KeyboardInterrupt is okay, we don't report it, just store it and let
       * the caller handler it at the earliest convenience */
    } else {
      /* All other exceptions are reported and cleared */
      PyErr_WriteUnraisable(exc_type);
      PyErr_Clear();
    }
    /* Fallback to the C random generator -- this should not happen */
    return rand();
  } else {
    retval = PyFloat_AsDouble(result);
    Py_DECREF(result);
    return retval;
  }
}

/**
 * \ingroup python_interface_rng
 * \brief Generates a real number distributed according to the normal distribution
 *        around zero with unit variance.
 */
igraph_real_t igraph_rng_Python_get_norm(void *state) {
  PyObject* exc_type;
  double retval;
  PyObject* result = PyObject_CallFunctionObjArgs(
    igraph_rng_Python_state.gauss_func,
    igraph_rng_Python_state.zero_as_pyobject,
    igraph_rng_Python_state.one_as_pyobject,
    0
  );

  if (result == 0) {
    exc_type = PyErr_Occurred();
    if (exc_type == PyExc_KeyboardInterrupt) {
      /* KeyboardInterrupt is okay, we don't report it, just store it and let
       * the caller handler it at the earliest convenience */
    } else {
      /* All other exceptions are reported and cleared */
      PyErr_WriteUnraisable(exc_type);
      PyErr_Clear();
    }
    /* Fallback -- this should not happen */
    return 0;
  } else {
    retval = PyFloat_AsDouble(result);
    Py_DECREF(result);
    return retval;
  }
}

/**
 * \ingroup python_interface_rng
 * \brief Specification table for Python's random number generator.
 *        This tells igraph which functions to call to obtain random numbers.
 */
igraph_rng_type_t igraph_rngtype_Python = {
  /* name= */      "Python random generator",
  /* bits= */      RNG_BITS,
  /* init= */      igraph_rng_Python_init,
  /* destroy= */   igraph_rng_Python_destroy,
  /* seed= */      igraph_rng_Python_seed,
  /* get= */       igraph_rng_Python_get,
  /* get_int= */   0,
  /* get_real= */  igraph_rng_Python_get_real,
  /* get_norm= */  igraph_rng_Python_get_norm,
  /* get_geom= */  0,
  /* get_binom= */ 0,
  /* get_exp= */   0,
  /* get_gamma= */ 0,
  /* get_pois= */  0,
};

void igraphmodule_init_rng(PyObject* igraph_module) {
  PyObject* random_module;

  if (igraph_rng_default_saved.type == 0) {
    igraph_rng_default_saved = *igraph_rng_default();
  }

  if (igraph_rng_Python.state != 0) {
    return;
  }

  random_module = PyImport_ImportModule("random");
  if (random_module == 0) {
    PyErr_WriteUnraisable(PyErr_Occurred());
    PyErr_Clear();
    return;
  }

  igraph_rng_Python.type = &igraph_rngtype_Python;
  igraph_rng_Python.state = &igraph_rng_Python_state;

  if (igraph_rng_Python_set_generator(igraph_module, random_module) == 0) {
    PyErr_WriteUnraisable(PyErr_Occurred());
    PyErr_Clear();
    return;
  }

  Py_DECREF(random_module);
}
