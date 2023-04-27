/* vim:set ts=2 sw=2 sts=2 et: */
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

#include "preamble.h"

#include <igraph.h>
#include "arpackobject.h"
#include "attributes.h"
#include "bfsiter.h"
#include "dfsiter.h"
#include "common.h"
#include "convert.h"
#include "edgeobject.h"
#include "edgeseqobject.h"
#include "error.h"
#include "graphobject.h"
#include "pyhelpers.h"
#include "random.h"
#include "vertexobject.h"
#include "vertexseqobject.h"
#include "operators.h"

#define IGRAPH_MODULE
#include "igraphmodule_api.h"

/**
 * \defgroup python_interface Python module implementation
 * \brief Functions implementing a Python interface to \a igraph
 * 
 * These functions provide a way to access \a igraph functions from Python.
 * It should be of interest of \a igraph developers only. Classes, functions
 * and methods exposed to Python are still to be documented. Until it is done,
 * just type the following to get help about \a igraph functions in Python
 * (assuming you have \c igraph.so somewhere in your Python library path):
 * 
 * \verbatim
import igraph
help(igraph)
help(igraph.Graph)
\endverbatim
 * 
 * Most of the functions provided here share the same calling conventions
 * (which are determined by the Python/C API). Since the role of the
 * arguments are the same across many functions, I won't explain them
 * everywhere, just give a quick overview of the common argument names here.
 * 
 * \param self the Python igraph.Graph object the method is working on
 * \param args pointer to the Python tuple containing the arguments
 * \param kwds pointer to the Python hash containing the keyword parameters
 * \param type the type object of a Python igraph.Graph object. Used usually
 * in constructors and class methods.
 * 
 * Any arguments not documented here should be mentioned at the documentation
 * of the appropriate method.
 * 
 * The functions which implement a Python method always return a pointer to
 * a \c PyObject. According to Python conventions, this is \c NULL if and
 * only if an exception was thrown by the method (or any of the functions
 * it has called). When I explain the return value of a function which
 * provides interface to an \a igraph function, I won't cover the case of
 * returning a \c NULL value, because this is the same for every such method.
 * The conclusion is that a method can return \c NULL even if I don't state
 * it explicitly.
 * 
 * Also please take into consideration that I'm documenting the C calls
 * with the abovementioned parameters here, and \em not the Python methods
 * which are presented to the user using the Python interface of \a igraph.
 * If you are looking for the documentation of the classes, methods and
 * functions exposed to Python, please use the \c help calls from Python
 * or use \c pydoc to generate a formatted version.
 *
 * \section weakrefs The usage of weak references in the Python interface
 * 
 * Many classes implemented in the Python interface (e.g. VertexSeq, Vertex...)
 * use weak references to keep track of the graph they are referencing to.
 * The use of weak references is twofold:
 * 
 * -# If we assign a VertexSeq or a Vertex of a given graph to a local
 *    variable and then destroy the graph, real references keep the graph
 *    alive and do not return the memory back to Python.
 * -# If we use real references, a Graph object will hold a reference
 *    to its VertexSeq (because we don't want to allocate a new VertexSeq
 *    object for the same graph every time it is requested), and the
 *    VertexSeq will also hold a reference to the Graph. This is a circular
 *    reference. Python does not reclaim the memory occupied by the Graph
 *    back when the Graph is destroyed, because the VertexSeq is holding a
 *    reference to it. Similarly, VertexSeq doesn't get freed because the
 *    Graph is holding a reference to it. These situations can only be
 *    resolved by the Python garbage collector which is invoked at regular
 *    intervals. Unfortunately, the garbage collector refuses to break
 *    circular references and free the objects participating in the circle
 *    when any of the objects has a \c __del__ method. In this case,
 *    \c igraph.Graph has one (which frees the underlying \c igraph_t
 *    graph), therefore our graphs never get freed when we use real
 *    references.
 */

/**
 * Whether the module was initialized already
 */
static igraph_bool_t igraphmodule_initialized = false;

/**
 * Module-specific global variables
 */
struct module_state {
  PyObject* progress_handler;
  PyObject* status_handler;
};
static struct module_state _state = { 0, 0 };

#define GETSTATE(m) (&_state)

static int igraphmodule_traverse(PyObject *m, visitproc visit, void* arg) {
  Py_VISIT(GETSTATE(m)->progress_handler);
  Py_VISIT(GETSTATE(m)->status_handler);
  return 0;
}

static int igraphmodule_clear(PyObject *m) {
  Py_CLEAR(GETSTATE(m)->progress_handler);
  Py_CLEAR(GETSTATE(m)->status_handler);
  return 0;
}

static igraph_error_t igraphmodule_igraph_interrupt_hook(void* data) {
  if (PyErr_CheckSignals()) {
    IGRAPH_FINALLY_FREE();
    return IGRAPH_INTERRUPTED;
  }
  return IGRAPH_SUCCESS;
}

igraph_error_t igraphmodule_igraph_progress_hook(const char* message, igraph_real_t percent,
				       void* data) {
  PyObject* progress_handler = GETSTATE(0)->progress_handler;
  PyObject *result;

  if (progress_handler) {
    if (PyCallable_Check(progress_handler)) {
      result = PyObject_CallFunction(progress_handler, "sd", message, (double)percent);
      if (result) {
        Py_DECREF(result);
      } else {
        return IGRAPH_INTERRUPTED;
      }
    }
  }
  
  return IGRAPH_SUCCESS;
}

igraph_error_t igraphmodule_igraph_status_hook(const char* message, void*data) {
  PyObject* status_handler = GETSTATE(0)->status_handler;

  if (status_handler) {
    PyObject *result;
    if (PyCallable_Check(status_handler)) {
      result = PyObject_CallFunction(status_handler, "s", message);
      if (result)
        Py_DECREF(result);
      else
        return IGRAPH_INTERRUPTED;
    }
  }
  
  return IGRAPH_SUCCESS;
}

PyObject* igraphmodule_set_progress_handler(PyObject* self, PyObject* o) {
  PyObject* progress_handler;

  if (!PyCallable_Check(o) && o != Py_None) {
    PyErr_SetString(PyExc_TypeError, "Progress handler must be callable.");
    return NULL;
  }

  progress_handler = GETSTATE(self)->progress_handler;
  if (o == progress_handler)
    Py_RETURN_NONE;

  Py_XDECREF(progress_handler);
  if (o == Py_None)
    o = NULL;

  Py_XINCREF(o);
  GETSTATE(self)->progress_handler=o;

  Py_RETURN_NONE;
}

PyObject* igraphmodule_set_status_handler(PyObject* self, PyObject* o) {
  PyObject* status_handler;

  if (!PyCallable_Check(o) && o != Py_None) {
    PyErr_SetString(PyExc_TypeError, "Status handler must be callable.");
    return NULL;
  }

  status_handler = GETSTATE(self)->status_handler;
  if (o == status_handler)
    Py_RETURN_NONE;

  Py_XDECREF(status_handler);
  if (o == Py_None) {
    o = NULL;
  }

  Py_XINCREF(o);
  GETSTATE(self)->status_handler = o;

  Py_RETURN_NONE;
}

PyObject* igraphmodule_convex_hull(PyObject* self, PyObject* args, PyObject* kwds) {
  static char* kwlist[] = {"vs", "coords", NULL};
  PyObject *vs, *o, *o1 = 0, *o2 = 0, *o1_float, *o2_float, *coords = Py_False;
  igraph_matrix_t mtrx;
  igraph_vector_int_t result;
  igraph_matrix_t resmat;
  Py_ssize_t no_of_nodes, i;
  
  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O!|O", kwlist, &PyList_Type, &vs, &coords))
    return NULL;
  
  no_of_nodes = PyList_Size(vs);
  if (igraph_matrix_init(&mtrx, no_of_nodes, 2)) {
    igraphmodule_handle_igraph_error();
    return NULL;
  }

  for (i = 0; i < no_of_nodes; i++) {
    o = PyList_GetItem(vs, i);

    if (PySequence_Check(o)) {
      if (PySequence_Size(o) >= 2) {
        o1 = PySequence_GetItem(o, 0);
        if (!o1) {
          igraph_matrix_destroy(&mtrx);
          return NULL;
        }

        o2 = PySequence_GetItem(o, 1);
        if (!o2) {
          Py_DECREF(o1);
          igraph_matrix_destroy(&mtrx);
          return NULL;
        }

        if (PySequence_Size(o) > 2) {
          PY_IGRAPH_WARN("vertex with more than 2 coordinates found, considering only the first 2");
        }
      } else {
        PyErr_SetString(PyExc_TypeError, "vertex with less than 2 coordinates found");
        igraph_matrix_destroy(&mtrx);
        return NULL;
      }
    } else {
      PyErr_SetString(PyExc_TypeError, "convex_hull() must receive a list of indexable sequences");
      igraph_matrix_destroy(&mtrx);
      return NULL;
    }
    
    if (!PyNumber_Check(o1) || !PyNumber_Check(o2)) {
      PyErr_SetString(PyExc_TypeError, "vertex coordinates must be numeric");
      Py_DECREF(o2);
      Py_DECREF(o1);
      igraph_matrix_destroy(&mtrx);
      return NULL;
    }

    o1_float = PyNumber_Float(o1);
    if (!o1_float) {
      Py_DECREF(o2);
      Py_DECREF(o1);
      igraph_matrix_destroy(&mtrx);
      return NULL;
    }
    Py_DECREF(o1);

    o2_float = PyNumber_Float(o2);
    if (!o2_float) {
      Py_DECREF(o2);
      igraph_matrix_destroy(&mtrx);
      return NULL;
    }
    Py_DECREF(o2);

    MATRIX(mtrx, i, 0) = PyFloat_AsDouble(o1_float);
    MATRIX(mtrx, i, 1) = PyFloat_AsDouble(o2_float);
    Py_DECREF(o1_float);
    Py_DECREF(o2_float);
  }

  if (!PyObject_IsTrue(coords)) {
    if (igraph_vector_int_init(&result, 0)) {
      igraphmodule_handle_igraph_error();
      igraph_matrix_destroy(&mtrx);
      return NULL;
    }
    if (igraph_convex_hull(&mtrx, &result, 0)) {
      igraphmodule_handle_igraph_error();
      igraph_matrix_destroy(&mtrx);
      igraph_vector_int_destroy(&result);
      return NULL;
    }    
    o = igraphmodule_vector_int_t_to_PyList(&result);
    igraph_vector_int_destroy(&result);
  } else {
    if (igraph_matrix_init(&resmat, 0, 0)) {
      igraphmodule_handle_igraph_error();
      igraph_matrix_destroy(&mtrx);
      return NULL;
    }
    if (igraph_convex_hull(&mtrx, 0, &resmat)) {
      igraphmodule_handle_igraph_error();
      igraph_matrix_destroy(&mtrx);
      igraph_matrix_destroy(&resmat);
      return NULL;
    }        
    o = igraphmodule_matrix_t_to_PyList(&resmat, IGRAPHMODULE_TYPE_FLOAT);
    igraph_matrix_destroy(&resmat);
  }
  
  igraph_matrix_destroy(&mtrx);

  return o;
}


PyObject* igraphmodule_community_to_membership(PyObject *self,
  PyObject *args, PyObject *kwds) {
  static char* kwlist[] = { "merges", "nodes", "steps", "return_csize", NULL };
  PyObject *merges_o, *return_csize = Py_False, *result_o;
  igraph_matrix_int_t merges;
  igraph_vector_int_t result, csize, *csize_p = 0;
  Py_ssize_t nodes, steps;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O!nn|O", kwlist,
      &PyList_Type, &merges_o, &nodes, &steps, &return_csize)) return NULL;

  if (igraphmodule_PyList_to_matrix_int_t_with_minimum_column_count(merges_o, &merges, 2, "merges")) {
    return NULL;
  }

  CHECK_SSIZE_T_RANGE(nodes, "number of nodes");
  CHECK_SSIZE_T_RANGE(steps, "number of steps");

  if (igraph_vector_int_init(&result, nodes)) {
    igraphmodule_handle_igraph_error();
    igraph_matrix_int_destroy(&merges);
    return NULL;
  }

  if (PyObject_IsTrue(return_csize)) {
    igraph_vector_int_init(&csize, 0);
    csize_p = &csize;
  }

  if (igraph_community_to_membership(&merges, nodes, steps, &result, csize_p)) {
    igraphmodule_handle_igraph_error();
    igraph_vector_int_destroy(&result);
    if (csize_p) igraph_vector_int_destroy(csize_p);
    igraph_matrix_int_destroy(&merges);
    return NULL;
  }
  igraph_matrix_int_destroy(&merges);

  result_o = igraphmodule_vector_int_t_to_PyList(&result);
  igraph_vector_int_destroy(&result);

  if (csize_p) {
	PyObject* csize_o = igraphmodule_vector_int_t_to_PyList(csize_p);
	igraph_vector_int_destroy(csize_p);
	if (csize_o) return Py_BuildValue("NN", result_o, csize_o);
	Py_DECREF(result_o);
	return NULL;
  }

  return result_o;
}


PyObject* igraphmodule_compare_communities(PyObject *self,
  PyObject *args, PyObject *kwds) {
  static char* kwlist[] = { "comm1", "comm2", "method", NULL };
  PyObject *comm1_o, *comm2_o, *method_o = Py_None;
  igraph_vector_int_t comm1, comm2;
  igraph_community_comparison_t method = IGRAPH_COMMCMP_VI;
  igraph_real_t result;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "OO|O", kwlist,
      &comm1_o, &comm2_o, &method_o)) {
    return NULL;
  }

  if (igraphmodule_PyObject_to_community_comparison_t(method_o, &method)) {
    return NULL;
  }

  if (igraphmodule_PyObject_to_vector_int_t(comm1_o, &comm1)) {
    return NULL;
  }

  if (igraphmodule_PyObject_to_vector_int_t(comm2_o, &comm2)) {
    igraph_vector_int_destroy(&comm1);
    return NULL;
  }

  if (igraph_compare_communities(&comm1, &comm2, &result, method)) {
    igraphmodule_handle_igraph_error();
    igraph_vector_int_destroy(&comm1);
    igraph_vector_int_destroy(&comm2);
    return NULL;
  }

  igraph_vector_int_destroy(&comm1);
  igraph_vector_int_destroy(&comm2);

  return igraphmodule_real_t_to_PyObject(result, IGRAPHMODULE_TYPE_FLOAT);
}


PyObject* igraphmodule_is_degree_sequence(PyObject *self,
  PyObject *args, PyObject *kwds) {
  static char* kwlist[] = { "out_deg", "in_deg", NULL };
  PyObject *out_deg_o = 0, *in_deg_o = 0;
  igraph_vector_int_t out_deg, in_deg;
  igraph_bool_t is_directed, result;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O|O", kwlist,
      &out_deg_o, &in_deg_o))
    return NULL;

  is_directed = (in_deg_o != 0 && in_deg_o != Py_None);

  if (igraphmodule_PyObject_to_vector_int_t(out_deg_o, &out_deg))
    return NULL;

  if (is_directed && igraphmodule_PyObject_to_vector_int_t(in_deg_o, &in_deg)) {
    igraph_vector_int_destroy(&out_deg);
    return NULL;
  }

  if (igraph_is_graphical(&out_deg, is_directed ? &in_deg : 0, IGRAPH_LOOPS_SW | IGRAPH_MULTI_SW, &result)) {
    igraphmodule_handle_igraph_error();
    igraph_vector_int_destroy(&out_deg);
    if (is_directed)
      igraph_vector_int_destroy(&in_deg);
    return NULL;
  }

  igraph_vector_int_destroy(&out_deg);
  if (is_directed)
    igraph_vector_int_destroy(&in_deg);

  if (result)
    Py_RETURN_TRUE;
  else
    Py_RETURN_FALSE;
}


PyObject* igraphmodule_is_graphical_degree_sequence(PyObject *self,
  PyObject *args, PyObject *kwds) {
  static char* kwlist[] = { "out_deg", "in_deg", NULL };
  PyObject *out_deg_o = 0, *in_deg_o = 0;
  igraph_vector_int_t out_deg, in_deg;
  igraph_bool_t is_directed, result;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O|O", kwlist,
      &out_deg_o, &in_deg_o))
    return NULL;

  is_directed = (in_deg_o != 0 && in_deg_o != Py_None);

  if (igraphmodule_PyObject_to_vector_int_t(out_deg_o, &out_deg))
    return NULL;

  if (is_directed && igraphmodule_PyObject_to_vector_int_t(in_deg_o, &in_deg)) {
    igraph_vector_int_destroy(&out_deg);
    return NULL;
  }

  if (igraph_is_graphical(&out_deg, is_directed ? &in_deg : 0, IGRAPH_SIMPLE_SW, &result)) {
    igraphmodule_handle_igraph_error();
    igraph_vector_int_destroy(&out_deg);
    if (is_directed)
      igraph_vector_int_destroy(&in_deg);
    return NULL;
  }

  igraph_vector_int_destroy(&out_deg);
  if (is_directed)
    igraph_vector_int_destroy(&in_deg);

  if (result)
    Py_RETURN_TRUE;
  else
    Py_RETURN_FALSE;
}


PyObject* igraphmodule_is_graphical(PyObject *self, PyObject *args, PyObject *kwds) {
  static char* kwlist[] = { "out_deg", "in_deg", "loops", "multiple", NULL };
  PyObject *out_deg_o = 0, *in_deg_o = 0;
  PyObject *loops = Py_False, *multiple = Py_False;
  igraph_vector_int_t out_deg, in_deg;
  igraph_bool_t is_directed, result;
  int allowed_edge_types;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O|OOO", kwlist,
      &out_deg_o, &in_deg_o, &loops, &multiple))
    return NULL;

  is_directed = (in_deg_o != 0 && in_deg_o != Py_None);

  if (igraphmodule_PyObject_to_vector_int_t(out_deg_o, &out_deg))
    return NULL;

  if (is_directed && igraphmodule_PyObject_to_vector_int_t(in_deg_o, &in_deg)) {
    igraph_vector_int_destroy(&out_deg);
    return NULL;
  }

  allowed_edge_types = IGRAPH_SIMPLE_SW;
  if (PyObject_IsTrue(loops)) {
    allowed_edge_types |= IGRAPH_LOOPS_SW;
  }
  if (PyObject_IsTrue(multiple)) {
    allowed_edge_types |= IGRAPH_MULTI_SW;
  }

  if (igraph_is_graphical(&out_deg, is_directed ? &in_deg : 0, allowed_edge_types, &result)) {
    igraphmodule_handle_igraph_error();
    igraph_vector_int_destroy(&out_deg);
    if (is_directed) {
      igraph_vector_int_destroy(&in_deg);
    }
    return NULL;
  }

  igraph_vector_int_destroy(&out_deg);
  if (is_directed) {
    igraph_vector_int_destroy(&in_deg);
  }

  if (result)
    Py_RETURN_TRUE;
  else
    Py_RETURN_FALSE;
}


PyObject* igraphmodule_power_law_fit(PyObject *self, PyObject *args, PyObject *kwds) {
  static char* kwlist[] = { "data", "xmin", "force_continuous", "p_precision", NULL };
  PyObject *data_o, *force_continuous_o = Py_False;
  igraph_vector_t data;
  igraph_plfit_result_t result;
  double xmin = -1, p_precision = 0.01;
  igraph_real_t p;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O|dOd", kwlist, &data_o,
        &xmin, &force_continuous_o, &p_precision))
    return NULL;

  if (igraphmodule_PyObject_float_to_vector_t(data_o, &data))
    return NULL;

  if (igraph_power_law_fit(&data, &result, xmin, PyObject_IsTrue(force_continuous_o))) {
    igraphmodule_handle_igraph_error();
    igraph_vector_destroy(&data);
    return NULL;
  }

  if (igraph_plfit_result_calculate_p_value(&result, &p, p_precision)) {
    igraphmodule_handle_igraph_error();
    igraph_vector_destroy(&data);
    return NULL;
  }

  igraph_vector_destroy(&data);

  return Py_BuildValue("Oddddd", result.continuous ? Py_True : Py_False,
      result.alpha, result.xmin, result.L, result.D, (double) p);
}

PyObject* igraphmodule_split_join_distance(PyObject *self,
  PyObject *args, PyObject *kwds) {
  static char* kwlist[] = { "comm1", "comm2", NULL };
  PyObject *comm1_o, *comm2_o;
  igraph_vector_int_t comm1, comm2;
  igraph_integer_t distance12, distance21;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "OO", kwlist,
      &comm1_o, &comm2_o))
    return NULL;

  if (igraphmodule_PyObject_to_vector_int_t(comm1_o, &comm1)) {
    return NULL;
  }

  if (igraphmodule_PyObject_to_vector_int_t(comm2_o, &comm2)) {
    igraph_vector_int_destroy(&comm1);
    return NULL;
  }

  if (igraph_split_join_distance(&comm1, &comm2, &distance12, &distance21)) {
    igraphmodule_handle_igraph_error();
    igraph_vector_int_destroy(&comm1);
    igraph_vector_int_destroy(&comm2);
    return NULL;
  }

  igraph_vector_int_destroy(&comm1);
  igraph_vector_int_destroy(&comm2);

  /* sizeof(Py_ssize_t) is most likely the same as sizeof(igraph_integer_t),
   * but even if it isn't, we cast explicitly so we are safe */
  return Py_BuildValue("nn", (Py_ssize_t)distance12, (Py_ssize_t)distance21);
}


/** \ingroup python_interface_graph
 * \brief Compute weights for Uniform Manifold Approximation and Projection (UMAP)
 * \return the weights given that graph
 * \sa igraph_umap_compute_weights
 */
PyObject *igraphmodule_umap_compute_weights(
    PyObject *self, PyObject * args, PyObject * kwds)
{
  static char *kwlist[] = { "graph", "dist", NULL };
  igraph_vector_t *dist = 0;
  igraph_vector_t weights;
  PyObject *dist_o = Py_None, *graph_o = Py_None;
  PyObject *result_o;
  igraphmodule_GraphObject * graph;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "OO", kwlist, &graph_o, &dist_o))
    return NULL;

  /* Initialize distances */
  if (dist_o != Py_None) {
    dist = (igraph_vector_t*)malloc(sizeof(igraph_vector_t));
    if (!dist) {
      PyErr_NoMemory();
      return NULL;
    }
    if (igraphmodule_PyObject_to_vector_t(dist_o, dist, 0)) {
      free(dist);
      return NULL;
    }
  }

  /* Extract graph from Python object */
  graph = (igraphmodule_GraphObject*)graph_o;

  /* Initialize weights */
  if (igraph_vector_init(&weights, 0)) {
      igraph_vector_destroy(dist); free(dist);
      PyErr_NoMemory();
      return NULL;
  }

  /* Call the function */
  if (igraph_layout_umap_compute_weights(&graph->g, dist, &weights)) {
      igraph_vector_destroy(&weights);
      igraph_vector_destroy(dist); free(dist);
      PyErr_NoMemory();
      return NULL;
  }
  igraph_vector_destroy(dist); free(dist);

  /* Convert output to Python list */
  result_o = igraphmodule_vector_t_to_PyList(&weights, IGRAPHMODULE_TYPE_FLOAT);
  igraph_vector_destroy(&weights);
  return (PyObject *) result_o;
}


#define LOCALE_CAPSULE_TYPE "igraph._igraph.locale_capsule"

void igraphmodule__destroy_locale_capsule(PyObject *capsule) {
  igraph_safelocale_t* loc = (igraph_safelocale_t*) PyCapsule_GetPointer(capsule, LOCALE_CAPSULE_TYPE);
  if (loc) {
    PyMem_Free(loc);
  }
}

PyObject* igraphmodule__enter_safelocale(PyObject* self, PyObject* Py_UNUSED(_null)) {
  igraph_safelocale_t* loc;
  PyObject* capsule;

  loc = PyMem_Malloc(sizeof(loc));
  if (loc == NULL) {
    PyErr_NoMemory();
    return NULL;
  }

  capsule = PyCapsule_New(loc, LOCALE_CAPSULE_TYPE, igraphmodule__destroy_locale_capsule);
  if (capsule == NULL) {
    return NULL;
  }

  if (igraph_enter_safelocale(loc)) {
    Py_DECREF(capsule);
    igraphmodule_handle_igraph_error();
  }

  return capsule;
}

PyObject* igraphmodule__exit_safelocale(PyObject *self, PyObject *capsule) {
  igraph_safelocale_t* loc;

  if (!PyCapsule_IsValid(capsule, LOCALE_CAPSULE_TYPE)) {
    PyErr_SetString(PyExc_TypeError, "expected locale capsule");
    return NULL;
  }

  loc = (igraph_safelocale_t*) PyCapsule_GetPointer(capsule, LOCALE_CAPSULE_TYPE);
  if (loc != NULL) {
    igraph_exit_safelocale(loc);
  }

  Py_RETURN_NONE;
}

/** \ingroup python_interface
 * \brief Method table for the igraph Python module
 */
static PyMethodDef igraphmodule_methods[] = 
{
  {"community_to_membership", (PyCFunction)igraphmodule_community_to_membership,
    METH_VARARGS | METH_KEYWORDS,
    "community_to_membership(merges, nodes, steps, return_csize=False)\n--\n\n"
  },
  {"_compare_communities", (PyCFunction)igraphmodule_compare_communities,
    METH_VARARGS | METH_KEYWORDS,
    "_compare_communities(comm1, comm2, method=\"vi\")\n--\n\n"
  },
  {"_power_law_fit", (PyCFunction)igraphmodule_power_law_fit,
    METH_VARARGS | METH_KEYWORDS,
    "_power_law_fit(data, xmin=-1, force_continuous=False, p_precision=0.01)\n--\n\n"
  },
  {"convex_hull", (PyCFunction)igraphmodule_convex_hull,
    METH_VARARGS | METH_KEYWORDS,
    "convex_hull(vs, coords=False)\n--\n\n"
    "Calculates the convex hull of a given point set.\n\n"
    "@param vs: the point set as a list of lists\n"
    "@param coords: if C{True}, the function returns the\n"
    "  coordinates of the corners of the convex hull polygon,\n"
    "  otherwise returns the corner indices.\n"
    "@return: either the hull's corner coordinates or the point\n"
    "  indices corresponding to them, depending on the C{coords}\n"
    "  parameter."
  },
  {"is_degree_sequence", (PyCFunction)igraphmodule_is_degree_sequence,
    METH_VARARGS | METH_KEYWORDS,
    "is_degree_sequence(out_deg, in_deg=None)\n--\n\n"
    "Deprecated since 0.9 in favour of L{is_graphical()}.\n\n"
    "Returns whether a list of degrees can be a degree sequence of some graph.\n\n"
    "Note that it is not required for the graph to be simple; in other words,\n"
    "this function may return C{True} for degree sequences that can be realized\n"
    "using one or more multiple or loop edges only.\n\n"
    "In particular, this function checks whether\n\n"
    "  - all the degrees are non-negative\n"
    "  - for undirected graphs, the sum of degrees are even\n"
    "  - for directed graphs, the two degree sequences are of the same length and\n"
    "    equal sums\n\n"
    "@param out_deg: the list of degrees. For directed graphs, this list must\n"
    "  contain the out-degrees of the vertices.\n"
    "@param in_deg: the list of in-degrees for directed graphs. This parameter\n"
    "  must be C{None} for undirected graphs.\n"
    "@return: C{True} if there exists some graph that can realize the given degree\n"
    "  sequence, C{False} otherwise.\n"
  },
  {"is_graphical", (PyCFunction)igraphmodule_is_graphical,
    METH_VARARGS | METH_KEYWORDS,
    "is_graphical(out_deg, in_deg=None, loops=False, multiple=False)\n--\n\n"
    "Returns whether a list of degrees can be a degree sequence of some graph,\n"
    "with or without multiple and loop edges, depending on the allowed edge types\n"
    "in the remaining arguments.\n\n"
    "@param out_deg: the list of degrees. For directed graphs, this list must\n"
    "  contain the out-degrees of the vertices.\n"
    "@param in_deg: the list of in-degrees for directed graphs. This parameter\n"
    "  must be C{None} for undirected graphs.\n"
    "@param loops: whether loop edges are allowed.\n"
    "@param multiple: whether multiple edges are allowed.\n"
    "@return: C{True} if there exists some graph that can realize the given\n"
    "  degree sequence with the given edge types, C{False} otherwise.\n"
  },
  {"is_graphical_degree_sequence", (PyCFunction)igraphmodule_is_graphical_degree_sequence,
    METH_VARARGS | METH_KEYWORDS,
    "is_graphical_degree_sequence(out_deg, in_deg=None)\n--\n\n"
    "Deprecated since 0.9 in favour of L{is_graphical()}.\n\n"
    "Returns whether a list of degrees can be a degree sequence of some simple graph.\n\n"
    "Note that it is required for the graph to be simple; in other words,\n"
    "this function will return C{False} for degree sequences that cannot be realized\n"
    "without using one or more multiple or loop edges.\n\n"
    "@param out_deg: the list of degrees. For directed graphs, this list must\n"
    "  contain the out-degrees of the vertices.\n"
    "@param in_deg: the list of in-degrees for directed graphs. This parameter\n"
    "  must be C{None} for undirected graphs.\n"
    "@return: C{True} if there exists some simple graph that can realize the given\n"
    "  degree sequence, C{False} otherwise.\n"
  },
  {"umap_compute_weights", (PyCFunction)igraphmodule_umap_compute_weights,
   METH_VARARGS | METH_KEYWORDS,
   "umap_compute_weights(graph, dist)\n--\n\n"
   "Compute undirected UMAP weights from directed distance graph.\n"
   "UMAP is a layout algorithm that usually takes as input a directed\n"
   "distance graph, for instance a k nearest neighbor graph based on Euclidean\n"
   "distance between points in a vector space. The graph is directed\n"
   "because vertex v1 might consider vertex v2 a close neighbor, but v2\n"
   "itself might have many neighbors that are closer than v1.\n"
   "This function computes the symmetrized weights from the distance graph\n"
   "using union as the symmetry operator. In simple terms, if either vertex\n"
   "considers the other a close neighbor, they will be treated as close\n"
   "neighbors.\n\n"
   "This function can be used as a separate preprocessing step to\n"
   "Graph.layout_umap(). For efficiency reasons, the returned weights have the\n"
   "same length as the input distances, however because of the symmetryzation\n"
   "some information is lost. Therefore, the weight of one of the edges is set\n"
   "to zero whenever edges in opposite directions are found in the input\n"
   "distance graph. You can pipe the output of this function directly into\n"
   "Graph.layout_umap() as follows:\n"
   "C{weights = igraph.umap_compute_weights(graph, dist)}\n"
   "C{layout = graph.layout_umap(weights=weights)}\n\n"
   "@param graph: directed graph to compute weights for.\n"
   "@param dist: distances associated with the graph edges.\n"
   "@return: Symmetrized weights associated with each edge. If the distance\n"
   "  graph has both directed edges between a pair of vertices, one of the\n"
   "  returned weights will be set to zero.\n\n"
   "@see: Graph.layout_umap()\n"
  },
  {"set_progress_handler", igraphmodule_set_progress_handler, METH_O,
      "set_progress_handler(handler)\n--\n\n"
      "Sets the handler to be called when igraph is performing a long operation.\n"
      "@param handler: the progress handler function. It must accept two\n"
      "  arguments, the first is the message informing the user about\n"
      "  what igraph is doing right now, the second is the actual\n"
      "  progress information (a percentage).\n"
  },
  {"set_random_number_generator", igraph_rng_Python_set_generator, METH_O,
      "set_random_number_generator(generator)\n--\n\n"
      "Sets the random number generator used by igraph.\n"
      "@param generator: the generator to be used. It must be a Python object\n"
      "  with at least three attributes: C{random}, C{randint} and C{gauss}.\n"
      "  Each of them must be callable and their signature and behaviour\n"
      "  must be identical to C{random.random}, C{random.randint} and\n"
      "  C{random.gauss}. Optionally, the object can provide a function named\n"
      "  C{getrandbits} with a signature identical to C{randpm.getrandbits}\n"
      "  that provides a given number of random bits on demand. By default,\n"
      "  igraph uses the C{random} module for random number generation, but\n"
      "  you can supply your alternative implementation here. If the given\n"
      "  generator is C{None}, igraph reverts to the default PCG32 generator\n"
      "  implemented in the C layer, which might be slightly faster than\n"
      "  calling back to Python for random numbers, but you cannot set its\n"
      "  seed or save its state.\n"
  },
  {"set_status_handler", igraphmodule_set_status_handler, METH_O,
      "set_status_handler(handler)\n--\n\n"
      "Sets the handler to be called when igraph tries to display a status\n"
      "message.\n\n"
      "This is used to communicate the progress of some calculations where\n"
      "no reasonable progress percentage can be given (so it is not possible\n"
      "to use the progress handler).\n\n"
      "@param handler: the status handler function. It must accept a single\n"
      "  argument, the message that informs the user about what igraph is\n"
      "  doing right now.\n"
  },
  {"_split_join_distance", (PyCFunction)igraphmodule_split_join_distance,
    METH_VARARGS | METH_KEYWORDS,
    "_split_join_distance(comm1, comm2)\n--\n\n"
  },
  {"_disjoint_union", (PyCFunction)igraphmodule__disjoint_union,
    METH_VARARGS | METH_KEYWORDS,
    "_disjoint_union(graphs)\n--\n\n"
  },
  {"_union", (PyCFunction)igraphmodule__union,
    METH_VARARGS | METH_KEYWORDS,
    "_union(graphs, edgemaps)\n--\n\n"
  },
  {"_intersection", (PyCFunction)igraphmodule__intersection,
    METH_VARARGS | METH_KEYWORDS,
    "_intersection(graphs, edgemaps)\n--\n\n"
  },
  {"_enter_safelocale", (PyCFunction)igraphmodule__enter_safelocale,
    METH_NOARGS,
    "_enter_safelocale()\n--\n\n"
    "Helper function for the L{safe_locale()} context manager. Do not use\n"
    "directly in your own code."
  },
  {"_exit_safelocale", (PyCFunction)igraphmodule__exit_safelocale,
    METH_O,
    "_exit_safelocale(locale)\n--\n\n"
    "Helper function for the L{safe_locale()} context manager. Do not use\n"
    "directly in your own code."
  },
  {NULL, NULL, 0, NULL}
};

#define MODULE_DOCS \
  "Low-level Python interface for the igraph library. " \
  "Should not be used directly.\n"

/**
 * Module definition table
 */
static struct PyModuleDef moduledef = {
  PyModuleDef_HEAD_INIT,
  "igraph._igraph",                   /* m_name */
  MODULE_DOCS,                        /* m_doc */
  sizeof(struct module_state),        /* m_size */
  igraphmodule_methods,               /* m_methods */
  0,                                  /* m_reload */
  igraphmodule_traverse,              /* m_traverse */
  igraphmodule_clear,                 /* m_clear */
  0                                   /* m_free */
};

/****************** Exported API functions *******************/

/**
 * \brief Constructs a new Python Graph object from an existing igraph_t
 *
 * The newly created Graph object will take ownership of igraph_t and
 * it will destroy it when the Python object is destructed.
 *
 * Returns a null pointer in case of an error and sets the appropriate
 * Python exception.
 */
PyObject* PyIGraph_FromCGraph(igraph_t* g) {
  return igraphmodule_Graph_from_igraph_t(g);
}

/**
 * \brief Extracts the pointer to the \c igraph_t held by a Graph instance
 *
 * The ownership of the \c igraph_t object remains with the Graph instance,
 * so make sure you don't call \c igraph_destroy() on the extracted pointer.
 *
 * Returns a null pointer in case of an error and sets the appropriate
 * Python exception.
 */
igraph_t* PyIGraph_ToCGraph(PyObject* graph) {
  igraph_t *result = 0;

  if (graph == Py_None) {
    PyErr_SetString(PyExc_TypeError, "expected Graph, got None");
    return 0;
  }

  if (igraphmodule_PyObject_to_igraph_t(graph, &result))
    return 0;

  if (result == 0)
    PyErr_SetString(PyExc_ValueError, "null pointer stored inside a Graph "
                                      "object. Probably a bug.");

  return result;
}

extern PyObject* igraphmodule_InternalError;
extern PyObject* igraphmodule_arpack_options_default;

#define INITERROR return NULL
PyObject* PyInit__igraph(void)
{
  PyObject* m;
  static void *PyIGraph_API[PyIGraph_API_pointers];
  PyObject *c_api_object;

  /* Prevent linking 64-bit igraph to 32-bit Python */
  PY_IGRAPH_ASSERT_AT_BUILD_TIME(sizeof(igraph_integer_t) >= sizeof(Py_ssize_t));

  /* Check if the module is already initialized (possibly in another Python
   * interpreter. If so, bail out as we don't support this. */
  if (igraphmodule_initialized) {
    PyErr_SetString(PyExc_RuntimeError, "igraph module is already initialized "
        "in a different Python interpreter");
    INITERROR;
  }

  /* Run basic initialization of the pyhelpers.c module */
  if (igraphmodule_helpers_init()) {
    INITERROR;
  }

  /* Initialize types */
  if (
    igraphmodule_ARPACKOptions_register_type() ||
    igraphmodule_BFSIter_register_type() ||
    igraphmodule_DFSIter_register_type() ||
    igraphmodule_Edge_register_type() ||
    igraphmodule_EdgeSeq_register_type() ||
    igraphmodule_Graph_register_type() ||
    igraphmodule_Vertex_register_type() ||
    igraphmodule_VertexSeq_register_type()
  ) {
    INITERROR;
  }

  /* Initialize the core module */
  m = PyModule_Create(&moduledef);
  if (m == NULL)
    INITERROR;

  /* Initialize random number generator */
  igraphmodule_init_rng(m);

  /* Add the types to the core module */
  PyModule_AddObject(m, "GraphBase", (PyObject*)igraphmodule_GraphType);
  PyModule_AddObject(m, "BFSIter", (PyObject*)igraphmodule_BFSIterType);
  PyModule_AddObject(m, "DFSIter", (PyObject*)igraphmodule_DFSIterType);
  PyModule_AddObject(m, "ARPACKOptions", (PyObject*)igraphmodule_ARPACKOptionsType);
  PyModule_AddObject(m, "Edge", (PyObject*)igraphmodule_EdgeType);
  PyModule_AddObject(m, "EdgeSeq", (PyObject*)igraphmodule_EdgeSeqType);
  PyModule_AddObject(m, "Vertex", (PyObject*)igraphmodule_VertexType);
  PyModule_AddObject(m, "VertexSeq", (PyObject*)igraphmodule_VertexSeqType);
 
  /* Internal error exception type */
  igraphmodule_InternalError =
    PyErr_NewException("igraph._igraph.InternalError", PyExc_Exception, NULL);
  PyModule_AddObject(m, "InternalError", igraphmodule_InternalError);

  /* ARPACK default options variable */
  igraphmodule_arpack_options_default = PyObject_CallFunction((PyObject*) igraphmodule_ARPACKOptionsType, 0);
  if (igraphmodule_arpack_options_default == NULL)
    INITERROR;

  PyModule_AddObject(m, "arpack_options", igraphmodule_arpack_options_default);

  /* Useful constants */
  PyModule_AddIntConstant(m, "OUT", IGRAPH_OUT);
  PyModule_AddIntConstant(m, "IN", IGRAPH_IN);
  PyModule_AddIntConstant(m, "ALL", IGRAPH_ALL);

  PyModule_AddIntConstant(m, "STAR_OUT", IGRAPH_STAR_OUT);
  PyModule_AddIntConstant(m, "STAR_IN", IGRAPH_STAR_IN);
  PyModule_AddIntConstant(m, "STAR_MUTUAL", IGRAPH_STAR_MUTUAL);
  PyModule_AddIntConstant(m, "STAR_UNDIRECTED", IGRAPH_STAR_UNDIRECTED);

  PyModule_AddIntConstant(m, "TREE_OUT", IGRAPH_TREE_OUT);
  PyModule_AddIntConstant(m, "TREE_IN", IGRAPH_TREE_IN);
  PyModule_AddIntConstant(m, "TREE_UNDIRECTED", IGRAPH_TREE_UNDIRECTED);

  PyModule_AddIntConstant(m, "STRONG", IGRAPH_STRONG);
  PyModule_AddIntConstant(m, "WEAK", IGRAPH_WEAK);

  PyModule_AddIntConstant(m, "GET_ADJACENCY_UPPER", IGRAPH_GET_ADJACENCY_UPPER);
  PyModule_AddIntConstant(m, "GET_ADJACENCY_LOWER", IGRAPH_GET_ADJACENCY_LOWER);
  PyModule_AddIntConstant(m, "GET_ADJACENCY_BOTH", IGRAPH_GET_ADJACENCY_BOTH);

  PyModule_AddIntConstant(m, "REWIRING_SIMPLE", IGRAPH_REWIRING_SIMPLE);
  PyModule_AddIntConstant(m, "REWIRING_SIMPLE_LOOPS", IGRAPH_REWIRING_SIMPLE_LOOPS);

  PyModule_AddIntConstant(m, "ADJ_DIRECTED", IGRAPH_ADJ_DIRECTED);
  PyModule_AddIntConstant(m, "ADJ_UNDIRECTED", IGRAPH_ADJ_UNDIRECTED);
  PyModule_AddIntConstant(m, "ADJ_MAX", IGRAPH_ADJ_MAX);
  PyModule_AddIntConstant(m, "ADJ_MIN", IGRAPH_ADJ_MIN);
  PyModule_AddIntConstant(m, "ADJ_PLUS", IGRAPH_ADJ_PLUS);
  PyModule_AddIntConstant(m, "ADJ_UPPER", IGRAPH_ADJ_UPPER);
  PyModule_AddIntConstant(m, "ADJ_LOWER", IGRAPH_ADJ_LOWER);

  PyModule_AddIntConstant(m, "BLISS_F", IGRAPH_BLISS_F);
  PyModule_AddIntConstant(m, "BLISS_FL", IGRAPH_BLISS_FL);
  PyModule_AddIntConstant(m, "BLISS_FS", IGRAPH_BLISS_FS);
  PyModule_AddIntConstant(m, "BLISS_FM", IGRAPH_BLISS_FM);
  PyModule_AddIntConstant(m, "BLISS_FLM", IGRAPH_BLISS_FLM);
  PyModule_AddIntConstant(m, "BLISS_FSM", IGRAPH_BLISS_FSM);

  PyModule_AddIntConstant(m, "TRANSITIVITY_NAN", IGRAPH_TRANSITIVITY_NAN);
  PyModule_AddIntConstant(m, "TRANSITIVITY_ZERO", IGRAPH_TRANSITIVITY_ZERO);

  PyModule_AddIntConstant(m, "SIMPLE_SW", IGRAPH_SIMPLE_SW);
  PyModule_AddIntConstant(m, "LOOPS_SW", IGRAPH_LOOPS_SW);
  PyModule_AddIntConstant(m, "MULTI_SW", IGRAPH_MULTI_SW);

  PyModule_AddIntConstant(m, "INTEGER_SIZE", IGRAPH_INTEGER_SIZE);

  /* More useful constants */
  {
    const char* version;
    igraph_version(&version, 0, 0, 0);
    PyModule_AddStringConstant(m, "__igraph_version__", version);
  }
  PyModule_AddStringConstant(m, "__build_date__", __DATE__);

  /* initialize error, progress, warning and interruption handler */
  igraph_set_error_handler(igraphmodule_igraph_error_hook);
  igraph_set_progress_handler(igraphmodule_igraph_progress_hook);
  igraph_set_status_handler(igraphmodule_igraph_status_hook);
  igraph_set_warning_handler(igraphmodule_igraph_warning_hook);
  igraph_set_interruption_handler(igraphmodule_igraph_interrupt_hook);
  
  /* initialize attribute handlers */
  igraphmodule_initialize_attribute_handler();

  /* Initialize the C API pointer array */
  PyIGraph_API[PyIGraph_FromCGraph_NUM] = (void *)PyIGraph_FromCGraph;
  PyIGraph_API[PyIGraph_ToCGraph_NUM]   = (void *)PyIGraph_ToCGraph;

  /* Create a CObject containing the API pointer array's address */
  c_api_object = PyCapsule_New((void*)PyIGraph_API, "igraph._igraph._C_API", 0);
  if (c_api_object != 0) {
    PyModule_AddObject(m, "_C_API", c_api_object);
  }

  igraphmodule_initialized = 1;

  return m;
}
