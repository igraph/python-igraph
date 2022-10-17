/* vim:set ts=4 sw=2 sts=2 et:  */
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

#include "common.h"
#include "convert.h"
#include "error.h"
#include "graphobject.h"


/** \ingroup python_interface_graph
 * \brief Creates the disjoint union of two or more graphs
 */
PyObject *igraphmodule__disjoint_union(PyObject *self,
		PyObject *args, PyObject *kwds)
{
  static char* kwlist[] = { "graphs", NULL };
  PyObject *it, *graphs;
  Py_ssize_t no_of_graphs;
  igraph_vector_ptr_t gs;
  PyObject *result;
  PyTypeObject *result_type;
  igraph_t g;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O", kwlist,
      &graphs))
    return NULL;

  /* Needs to be an iterable */
  it = PyObject_GetIter(graphs);
  if (!it) {
      return igraphmodule_handle_igraph_error();
  }

  /* Get all elements, store the graphs in an igraph_vector_ptr */
  if (igraph_vector_ptr_init(&gs, 0)) {
    Py_DECREF(it);
    return igraphmodule_handle_igraph_error();
  }
  if (igraphmodule_append_PyIter_of_graphs_to_vector_ptr_t_with_type(it, &gs, &result_type)) {
    Py_DECREF(it);
    igraph_vector_ptr_destroy(&gs);
    return NULL;
  }
  Py_DECREF(it);
  no_of_graphs = igraph_vector_ptr_size(&gs);

  /* Create disjoint union */
  if (igraph_disjoint_union_many(&g, &gs)) {
    igraph_vector_ptr_destroy(&gs);
    return igraphmodule_handle_igraph_error();
  }

  igraph_vector_ptr_destroy(&gs);

  /* this is correct as long as attributes are not copied by the
   * operator. if they are copied, the initialization should not empty
   * the attribute hashes */
  if (no_of_graphs > 0) {
    result = igraphmodule_Graph_subclass_from_igraph_t(
        result_type,
        &g);
  } else {
    result = igraphmodule_Graph_from_igraph_t(&g);
  }

  return result;
}


/** \ingroup python_interface_graph
 * \brief Creates the union of two or more graphs
 */
PyObject *igraphmodule__union(PyObject *self,
		PyObject *args, PyObject *kwds)
{
  static char* kwlist[] = { "graphs", "edgemaps", NULL };
  PyObject *it, *em_list = 0, *graphs, *with_edgemaps_o;
  int with_edgemaps = 0;
  Py_ssize_t i, j, no_of_graphs;
  igraph_vector_ptr_t gs;
  igraphmodule_GraphObject *o;
  PyObject *result;
  PyTypeObject *result_type;
  igraph_t g;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O|O", kwlist,
      &graphs, &with_edgemaps_o))
    return NULL;

  if (PyObject_IsTrue(with_edgemaps_o))
    with_edgemaps = 1;

  /* Needs to be an iterable */
  it = PyObject_GetIter(graphs);
  if (!it) {
      return igraphmodule_handle_igraph_error();
  }

  /* Get all elements, store the graphs in an igraph_vector_ptr */
  if (igraph_vector_ptr_init(&gs, 0)) {
    Py_DECREF(it);
    return igraphmodule_handle_igraph_error();
  }
  if (igraphmodule_append_PyIter_of_graphs_to_vector_ptr_t_with_type(it, &gs, &result_type)) {
    Py_DECREF(it);
    igraph_vector_ptr_destroy(&gs);
    return NULL;
  }
  Py_DECREF(it);

  no_of_graphs = igraph_vector_ptr_size(&gs);

  if (with_edgemaps) {
    /* prepare edgemaps */
    igraph_vector_int_list_t edgemaps;
    if (igraph_vector_int_list_init(&edgemaps, 0)) {
      igraph_vector_ptr_destroy(&gs);
      return igraphmodule_handle_igraph_error();
    }

    /* Create union */
    if (igraph_union_many(&g, &gs, &edgemaps)) {
      igraph_vector_ptr_destroy(&gs);
      igraph_vector_int_list_destroy(&edgemaps);
      return igraphmodule_handle_igraph_error();
    }

    /* extract edgemaps */
    em_list = PyList_New(no_of_graphs);
    for (i = 0; i < no_of_graphs; i++) {
      Py_ssize_t no_of_edges = igraph_ecount(VECTOR(gs)[i]);
      igraph_vector_int_t *map = igraph_vector_int_list_get_ptr(&edgemaps, i);
      PyObject *emi = PyList_New(no_of_edges);
      if (emi) {
        for (j = 0; j < no_of_edges; j++) {
          PyObject *dest = igraphmodule_integer_t_to_PyObject(VECTOR(*map)[j]);
          if (!dest || PyList_SetItem(emi, j, dest)) {
            igraph_vector_ptr_destroy(&gs);
            igraph_vector_int_list_destroy(&edgemaps);
            Py_XDECREF(dest);
            Py_DECREF(emi);
            Py_DECREF(em_list);
            return NULL;
          }
          /* reference to 'dest' stolen by PyList_SetItem */
        }
      }
      if (!emi || PyList_SetItem(em_list, i, emi)) {
        igraph_vector_ptr_destroy(&gs);
        igraph_vector_int_list_destroy(&edgemaps);
        Py_XDECREF(emi);
        Py_DECREF(em_list);
        return NULL;
      }
      /* reference to 'emi' stolen by PyList_SetItem */
    }
    igraph_vector_int_list_destroy(&edgemaps);
  } else {
    /* Create union */
    if (igraph_union_many(&g, &gs, /* edgemaps */ 0)) {
      igraph_vector_ptr_destroy(&gs);
      return igraphmodule_handle_igraph_error();
    }
  }

  igraph_vector_ptr_destroy(&gs);

  /* this is correct as long as attributes are not copied by the
   * operator. if they are copied, the initialization should not empty
   * the attribute hashes */
  if (no_of_graphs > 0) {
    o = (igraphmodule_GraphObject*) igraphmodule_Graph_subclass_from_igraph_t(
        result_type,
        &g);
  } else {
    o = (igraphmodule_GraphObject*) igraphmodule_Graph_from_igraph_t(&g);
  }

  if (o != NULL) {
    if (with_edgemaps) {
      /* wrap in a dictionary */
      result = PyDict_New();
      PyDict_SetItemString(result, "graph", (PyObject *) o);
      Py_DECREF(o);
      PyDict_SetItemString(result, "edgemaps", em_list);
      Py_DECREF(em_list);
    } else {
      result = (PyObject *) o;
    }
  } else {
    result = (PyObject *) o;
  }

  return result;
}

/** \ingroup python_interface_graph
 * \brief Creates the intersection of two or more graphs
 */
PyObject *igraphmodule__intersection(PyObject *self,
		PyObject *args, PyObject *kwds)
{
  static char* kwlist[] = { "graphs", "edgemaps", NULL };
  PyObject *it, *em_list = 0, *graphs, *with_edgemaps_o;
  int with_edgemaps = 0;
  Py_ssize_t i, j, no_of_graphs;
  igraph_vector_ptr_t gs;
  igraphmodule_GraphObject *o;
  PyObject *result;
  PyTypeObject *result_type;
  igraph_t g;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O|O", kwlist,
      &graphs, &with_edgemaps_o))
    return NULL;

  if (PyObject_IsTrue(with_edgemaps_o))
    with_edgemaps = 1;

  /* Needs to be an iterable */
  it = PyObject_GetIter(graphs);
  if (!it) {
      return igraphmodule_handle_igraph_error();
  }

  /* Get all elements, store the graphs in an igraph_vector_ptr */
  if (igraph_vector_ptr_init(&gs, 0)) {
    Py_DECREF(it);
    return igraphmodule_handle_igraph_error();
  }
  if (igraphmodule_append_PyIter_of_graphs_to_vector_ptr_t_with_type(it, &gs, &result_type)) {
    Py_DECREF(it);
    igraph_vector_ptr_destroy(&gs);
    return NULL;
  }
  Py_DECREF(it);
  no_of_graphs = igraph_vector_ptr_size(&gs);

  if (with_edgemaps) {
    /* prepare edgemaps */
    igraph_vector_int_list_t edgemaps;
    if (igraph_vector_int_list_init(&edgemaps, 0)) {
      igraph_vector_ptr_destroy(&gs);
      return igraphmodule_handle_igraph_error();
    }

    /* Create intersection */
    if (igraph_intersection_many(&g, &gs, &edgemaps)) {
      igraph_vector_ptr_destroy(&gs);
      igraph_vector_int_list_destroy(&edgemaps);
      return igraphmodule_handle_igraph_error();
    }

    em_list = PyList_New((Py_ssize_t) no_of_graphs);
    for (i = 0; i < no_of_graphs; i++) {
      Py_ssize_t no_of_edges = igraph_ecount(VECTOR(gs)[i]);
      igraph_vector_int_t *map = igraph_vector_int_list_get_ptr(&edgemaps, i);
      PyObject *emi = PyList_New(no_of_edges);
      if (emi) {
        for (j = 0; j < no_of_edges; j++) {
          PyObject *dest = igraphmodule_integer_t_to_PyObject(VECTOR(*map)[j]);
          if (!dest || PyList_SetItem(emi, j, dest)) {
            igraph_vector_ptr_destroy(&gs);
            igraph_vector_int_list_destroy(&edgemaps);
            Py_XDECREF(dest);
            Py_DECREF(emi);
            Py_DECREF(em_list);
            return NULL;
          }
          /* reference to 'dest' stolen by PyList_SetItem */
        }
      }
      if (!emi || PyList_SetItem(em_list, i, emi)) {
        igraph_vector_ptr_destroy(&gs);
        igraph_vector_int_list_destroy(&edgemaps);
        Py_XDECREF(emi);
        Py_DECREF(em_list);
        return NULL;
      }
      /* reference to 'emi' stolen by PyList_SetItem */
    }
    igraph_vector_int_list_destroy(&edgemaps);
  } else {
    /* Create intersection */
    if (igraph_intersection_many(&g, &gs, /* edgemaps */ 0)) {
      igraph_vector_ptr_destroy(&gs);
      return igraphmodule_handle_igraph_error();
    }
  }

  igraph_vector_ptr_destroy(&gs);

  /* this is correct as long as attributes are not copied by the
   * operator. if they are copied, the initialization should not empty
   * the attribute hashes */
  if (no_of_graphs > 0) {
    o = (igraphmodule_GraphObject*) igraphmodule_Graph_subclass_from_igraph_t(
        result_type,
        &g);
  } else {
    o = (igraphmodule_GraphObject*) igraphmodule_Graph_from_igraph_t(&g);
  }

  if (o != NULL) {
    if (with_edgemaps) {
      /* wrap in a dictionary */
      result = PyDict_New();
      PyDict_SetItemString(result, "graph", (PyObject *) o);
      Py_DECREF(o);
      PyDict_SetItemString(result, "edgemaps", em_list);
      Py_DECREF(em_list);
    } else {
      result = (PyObject *) o;
    }
  } else {
    result = (PyObject *) o;
  }

  return result;
}


