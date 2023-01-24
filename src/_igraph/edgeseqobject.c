/* -*- mode: C -*-  */
/* vim: set ts=2 sts=2 sw=2 et: */

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

#include "attributes.h"
#include "common.h"
#include "convert.h"
#include "edgeseqobject.h"
#include "edgeobject.h"
#include "error.h"
#include "pyhelpers.h"

#define GET_GRAPH(obj) (((igraphmodule_GraphObject*)obj->gref)->g)

/**
 * \ingroup python_interface
 * \defgroup python_interface_edgeseq Edge sequence object
 */

PyTypeObject* igraphmodule_EdgeSeqType;

PyObject* igraphmodule_EdgeSeq_select(igraphmodule_EdgeSeqObject *self, PyObject *args);

/**
 * \ingroup python_interface_edgeseq
 * \brief Checks whether the given Python object is an edge sequence
 */
int igraphmodule_EdgeSeq_Check(PyObject* obj) {
  return obj ? PyObject_IsInstance(obj, (PyObject*)igraphmodule_EdgeSeqType) : 0;
}

/**
 * \ingroup python_interface_edgeseq
 * \brief Copies an edge sequence object
 * \return the copied PyObject
 */
igraphmodule_EdgeSeqObject*
igraphmodule_EdgeSeq_copy(igraphmodule_EdgeSeqObject* o) {
  igraphmodule_EdgeSeqObject *copy;

  copy = (igraphmodule_EdgeSeqObject*) PyType_GenericNew(Py_TYPE(o), 0, 0);
  if (copy == NULL) {
    return NULL;
  }

  if (igraph_es_type(&o->es) == IGRAPH_ES_VECTOR) {
    igraph_vector_int_t v;
    if (igraph_vector_int_init_copy(&v, o->es.data.vecptr)) {
      igraphmodule_handle_igraph_error();
      return 0;
    }
    if (igraph_es_vector_copy(&copy->es, &v)) {
      igraphmodule_handle_igraph_error();
      igraph_vector_int_destroy(&v);
      return 0;
    }
    igraph_vector_int_destroy(&v);
  } else {
    copy->es = o->es;
  }

  copy->gref = o->gref;
  if (o->gref) {
    Py_INCREF(o->gref);
  }

  RC_ALLOC("EdgeSeq(copy)", copy);

  return copy;
}

/**
 * \ingroup python_interface_edgeseq
 * \brief Initialize a new edge sequence object for a given graph
 * \return the initialized PyObject
 */
int igraphmodule_EdgeSeq_init(igraphmodule_EdgeSeqObject *self, PyObject *args, PyObject *kwds) {
  static char *kwlist[] = { "graph", "edges", NULL };
  PyObject *g, *esobj = Py_None;
  igraph_es_t es;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O!|O", kwlist,
    igraphmodule_GraphType, &g, &esobj)) {
    return -1;
  }

  if (esobj == Py_None) {
    /* If es is None, we are selecting all the edges */
    igraph_es_all(&es, IGRAPH_EDGEORDER_ID);
  } else if (PyLong_Check(esobj)) {
    /* We selected a single edge */
    igraph_integer_t idx;
    
    if (igraphmodule_PyObject_to_integer_t(esobj, &idx)) {
      return -1;
    }

    if (idx < 0 || idx >= igraph_ecount(&((igraphmodule_GraphObject*)g)->g)) {
      PyErr_SetString(PyExc_ValueError, "edge index out of range");
      return -1;
    }

    igraph_es_1(&es, idx);
  } else {
   /* We selected multiple edges */
    igraph_vector_int_t v;
    igraph_integer_t n = igraph_ecount(&((igraphmodule_GraphObject*)g)->g);
    if (igraphmodule_PyObject_to_vector_int_t(esobj, &v)) {
      return -1;
    }
    if (!igraph_vector_int_isininterval(&v, 0, n-1)) {
      igraph_vector_int_destroy(&v);
      PyErr_SetString(PyExc_ValueError, "edge index out of range");
      return -1;
    }
    if (igraph_es_vector_copy(&es, &v)) {
      igraphmodule_handle_igraph_error();
      igraph_vector_int_destroy(&v);
      return -1;
    }
    igraph_vector_int_destroy(&v);
  }

  self->es = es;
  Py_INCREF(g);
  self->gref = (igraphmodule_GraphObject*)g;

  return 0;
}

/**
 * \ingroup python_interface_edgeseq
 * \brief Deallocates a Python representation of a given edge sequence object
 */
void igraphmodule_EdgeSeq_dealloc(igraphmodule_EdgeSeqObject* self) {
  RC_DEALLOC("EdgeSeq", self);

  if (self->weakreflist != NULL) {
    PyObject_ClearWeakRefs((PyObject *)self);
  }

  if (self->gref) {
    igraph_es_destroy(&self->es);
  }

  Py_CLEAR(self->gref);
  PY_FREE_AND_DECREF_TYPE(self, igraphmodule_EdgeSeqType);
}

/**
 * \ingroup python_interface_edgeseq
 * \brief Returns the length of the sequence (i.e. the number of edges in the graph)
 */
Py_ssize_t igraphmodule_EdgeSeq_sq_length(igraphmodule_EdgeSeqObject* self) {
  igraph_t *g;
  igraph_integer_t result;

  g = &GET_GRAPH(self);

  if (igraph_es_size(g, &self->es, &result)) {
    igraphmodule_handle_igraph_error();
    return -1;
  }

  return result;
}

/**
 * \ingroup python_interface_edgeseq
 * \brief Returns the item at the given index in the sequence
 */
PyObject* igraphmodule_EdgeSeq_sq_item(igraphmodule_EdgeSeqObject* self,
                       Py_ssize_t i) {
  igraph_t *g;
  igraph_integer_t idx = -1;

  if (!self->gref) {
    return NULL;
  }

  g = &GET_GRAPH(self);

  switch (igraph_es_type(&self->es)) {
    case IGRAPH_ES_ALL:
      if (i < 0) {
        i = igraph_ecount(g) + i;
      }
      if (i >= 0 && i < igraph_ecount(g)) {
        idx = i;
      }
      break;

    case IGRAPH_ES_VECTOR:
    case IGRAPH_ES_VECTORPTR:
      if (i < 0) {
        i = igraph_vector_int_size(self->es.data.vecptr) + i;
      }
      if (i >= 0 && i < igraph_vector_int_size(self->es.data.vecptr)) {
        idx = VECTOR(*self->es.data.vecptr)[i];
      }
      break;

    case IGRAPH_ES_1:
      if (i == 0 || i == -1) {
        idx = self->es.data.eid;
      }
      break;

    case IGRAPH_ES_RANGE:
      if (i < 0) {
        i = self->es.data.range.end - self->es.data.range.start + i;
      }
      if (i >= 0 && i < self->es.data.range.end - self->es.data.range.start) {
        idx = self->es.data.range.start + i;
      }
      break;

    case IGRAPH_ES_NONE:
      break;

    /* TODO: IGRAPH_ES_PAIRS, IGRAPH_ES_ADJ, IGRAPH_ES_PATH,
       IGRAPH_ES_MULTIPATH - someday :) They are unused yet in the Python
       interface */

    default:
      return PyErr_Format(
        igraphmodule_InternalError, "unsupported edge selector type: %d", igraph_es_type(&self->es)
      );
  }

  if (idx < 0) {
    PyErr_SetString(PyExc_IndexError, "edge index out of range");
    return NULL;
  }

  return igraphmodule_Edge_New(self->gref, idx);
}

/** \ingroup python_interface_edgeseq
 * \brief Returns the list of attribute names
 */
PyObject* igraphmodule_EdgeSeq_attribute_names(igraphmodule_EdgeSeqObject* self, PyObject* Py_UNUSED(_null)) {
  return igraphmodule_Graph_edge_attributes(self->gref, NULL);
}

/** \ingroup python_interface_edgeseq
 * \brief Returns the list of values for a given attribute
 */
PyObject* igraphmodule_EdgeSeq_get_attribute_values(igraphmodule_EdgeSeqObject* self, PyObject* o) {
  igraphmodule_GraphObject *gr = self->gref;
  PyObject *result=0, *values, *item;
  Py_ssize_t i, n;

  if (!igraphmodule_attribute_name_check(o)) {
    return 0;
  }

  PyErr_Clear();
  values = PyDict_GetItem(ATTR_STRUCT_DICT(&gr->g)[ATTRHASH_IDX_EDGE], o);
  if (!values) {
    PyErr_SetString(PyExc_KeyError, "Attribute does not exist");
    return NULL;
  } else if (PyErr_Occurred()) {
    return NULL;
  }

  switch (igraph_es_type(&self->es)) {
    case IGRAPH_ES_NONE:
      n = 0;
      result = PyList_New(0);
      if (!result) {
        return 0;
      }
      break;

    case IGRAPH_ES_ALL:
      n = PyList_Size(values);
      result = PyList_New(n);
      if (!result) {
        return 0;
      }

      for (i = 0; i < n; i++) {
        item = PyList_GetItem(values, i);
        if (!item) {
          Py_DECREF(result);
          return 0;
        }

        Py_INCREF(item);

        if (PyList_SetItem(result, i, item)) {
          Py_DECREF(item);
          Py_DECREF(result);
          return 0;
        }
      }
      break;

    case IGRAPH_ES_VECTOR:
    case IGRAPH_ES_VECTORPTR:
      n = igraph_vector_int_size(self->es.data.vecptr);
      result = PyList_New(n);
      if (!result) {
        return 0;
      }

      for (i = 0; i < n; i++) {
        item = PyList_GetItem(values, VECTOR(*self->es.data.vecptr)[i]);
        if (!item) {
          Py_DECREF(result);
          return 0;
        }

        Py_INCREF(item);

        if (PyList_SetItem(result, i, item)) {
          Py_DECREF(item);
          Py_DECREF(result);
          return 0;
        }
      }
      break;

    case IGRAPH_ES_RANGE:
      n = self->es.data.range.end - self->es.data.range.start;
      result = PyList_New(n);
      if (!result) {
        return 0;
      }

      for (i = 0; i < n; i++) {
        item = PyList_GetItem(values, self->es.data.range.start + i);
        if (!item) {
          Py_DECREF(result);
          return 0;
        }
        
        Py_INCREF(item);

        if (PyList_SetItem(result, i, item)) {
          Py_DECREF(item);
          Py_DECREF(result);
          return 0;
        }
      }
      break;

    default:
      PyErr_SetString(PyExc_RuntimeError, "invalid edge selector");
  }

  return result;
}

PyObject* igraphmodule_EdgeSeq_is_all(igraphmodule_EdgeSeqObject* self, PyObject* Py_UNUSED(_null)) {
  if (igraph_es_is_all(&self->es)) {
    Py_RETURN_TRUE;
  } else {
    Py_RETURN_FALSE;
  }
}

PyObject* igraphmodule_EdgeSeq_get_attribute_values_mapping(igraphmodule_EdgeSeqObject *self, PyObject *o) {
  Py_ssize_t index;
  PyObject *index_o;

  /* Handle strings according to the mapping protocol */
  if (PyBaseString_Check(o)) {
    return igraphmodule_EdgeSeq_get_attribute_values(self, o);
  }

  /* Handle iterables and slices by calling the select() method */
  if (PySlice_Check(o) || PyObject_HasAttrString(o, "__iter__")) {
    PyObject *result, *args;
    args = PyTuple_Pack(1, o);

    if (!args) {
      return NULL;
    }

    result = igraphmodule_EdgeSeq_select(self, args);
    Py_DECREF(args);

    return result;
  }

  /* Handle integer indices according to the sequence protocol */
  index_o = PyNumber_Index(o);
  if (index_o) {
    index = PyLong_AsSsize_t(index_o);
    if (PyErr_Occurred()) {
      Py_DECREF(index_o);
      return NULL;
    } else {
      Py_DECREF(index_o);
      return igraphmodule_EdgeSeq_sq_item(self, index);
    }
  } else {
    /* clear TypeError raised by PyNumber_Index() */
    PyErr_Clear();
  }

  /* Handle everything else according to the mapping protocol */
  return igraphmodule_EdgeSeq_get_attribute_values(self, o);
}

/** \ingroup python_interface_edgeseq
 * \brief Sets the list of values for a given attribute
 */
int igraphmodule_EdgeSeq_set_attribute_values_mapping(igraphmodule_EdgeSeqObject* self, PyObject* attrname, PyObject* values) {
  PyObject *dict, *list, *item;
  igraphmodule_GraphObject *gr;
  igraph_vector_int_t es;
  Py_ssize_t i, j, n;
  igraph_integer_t no_of_edges;

  gr = self->gref;
  dict = ATTR_STRUCT_DICT(&gr->g)[ATTRHASH_IDX_EDGE];

  if (!igraphmodule_attribute_name_check(attrname)) {
    return -1;
  }

  if (values == 0) {
    if (igraph_es_type(&self->es) == IGRAPH_ES_ALL) {
      return PyDict_DelItem(dict, attrname);
    }
    PyErr_SetString(PyExc_TypeError, "can't delete attribute from an edge sequence not representing the whole graph");
    return -1;
  }

 if (PyUnicode_Check(values) || !PySequence_Check(values)) {
    /* If values is a string or not a sequence, we construct a list with a
     * single element (the value itself) and then call ourselves again */
    int result;
    PyObject *newList = PyList_New(1);
    if (newList == 0) {
      return -1;
    }
    Py_INCREF(values);

    if (PyList_SetItem(newList, 0, values)) {  /* reference stolen here */
      return -1;
    }

    result = igraphmodule_EdgeSeq_set_attribute_values_mapping(self, attrname, newList);
    Py_DECREF(newList);
    return result;
  }

  n = PySequence_Size(values);
  if (n < 0) {
    return -1;
  }

  if (igraph_es_type(&self->es) == IGRAPH_ES_ALL) {
    no_of_edges = igraph_ecount(&gr->g);
    if (n == 0 && no_of_edges > 0) {
      PyErr_SetString(PyExc_ValueError, "sequence must not be empty");
      return -1;
    }

    /* Check if we already have attributes with the given name */
    list = PyDict_GetItem(dict, attrname);
    if (list != 0) {
      /* Yes, we have. Modify its items to the items found in values */
      for (i = 0, j = 0; i < no_of_edges; i++, j++) {
        if (j == n) {
          j = 0;
        }
        item = PySequence_GetItem(values, j);
        if (item == 0) {
          return -1;
        }
        /* No need to Py_INCREF(item), PySequence_GetItem returns a new reference */
        if (PyList_SetItem(list, i, item)) {
          Py_DECREF(item);
          return -1;
        } /* PyList_SetItem stole a reference to the item automatically */
      }
    } else if (values != 0) {
      /* We don't have attributes with the given name yet. Create an entry
       * in the dict, create a new list and copy everything */
      list = PyList_New(no_of_edges);
      if (list == 0) {
        return -1;
      }
      for (i = 0, j = 0; i < no_of_edges; i++, j++) {
        if (j == n) {
          j = 0;
        }
        item = PySequence_GetItem(values, j);
        if (item == 0) {
          Py_DECREF(list); return -1;
        }
        /* No need to Py_INCREF(item), PySequence_GetItem returns a new reference */
        if (PyList_SetItem(list, i, item)) {
          Py_DECREF(item);
          Py_DECREF(list);
          return -1;
        }
        /* PyList_SET_ITEM stole a reference to the item automatically */
      }
      if (PyDict_SetItem(dict, attrname, list)) {
        Py_DECREF(list);
        return -1;
      }
      Py_DECREF(list);   /* compensating for PyDict_SetItem */
    }
  } else {
    /* We are working with a subset of the graph. Convert the sequence to a
     * vector and loop through it */
    if (igraph_vector_int_init(&es, 0)) {
      igraphmodule_handle_igraph_error();
      return -1;
    }
    if (igraph_es_as_vector(&gr->g, self->es, &es)) {
      igraphmodule_handle_igraph_error();
      igraph_vector_int_destroy(&es);
      return -1;
    }
    no_of_edges = igraph_vector_int_size(&es);
    if (n == 0 && no_of_edges > 0) {
      PyErr_SetString(PyExc_ValueError, "sequence must not be empty");
      igraph_vector_int_destroy(&es);
      return -1;
    }
    /* Check if we already have attributes with the given name */
    list = PyDict_GetItem(dict, attrname);
    if (list != 0) {
      /* Yes, we have. Modify its items to the items found in values */
      for (i = 0, j = 0; i < no_of_edges; i++, j++) {
        if (j == n) {
          j = 0;
        }
        item = PySequence_GetItem(values, j);
        if (item == 0) {
          igraph_vector_int_destroy(&es); return -1;
        }
        /* No need to Py_INCREF(item), PySequence_GetItem returns a new reference */
        if (PyList_SetItem(list, VECTOR(es)[i], item)) {
          Py_DECREF(item);
          igraph_vector_int_destroy(&es);
          return -1;
        } /* PyList_SetItem stole a reference to the item automatically */
      }
      igraph_vector_int_destroy(&es);
    } else if (values != 0) {
      /* We don't have attributes with the given name yet. Create an entry
       * in the dict, create a new list, fill with None for vertices not in the
       * sequence and copy the rest */
      igraph_integer_t n2 = igraph_ecount(&gr->g);
      list = PyList_New(n2);
      if (list == 0) {
        igraph_vector_int_destroy(&es);
        return -1;
      }
      for (i = 0; i < n2; i++) {
        Py_INCREF(Py_None);
        if (PyList_SetItem(list, i, Py_None)) {
          Py_DECREF(Py_None);
          Py_DECREF(list);
          return -1;
        }
      }
      for (i = 0, j = 0; i < no_of_edges; i++, j++) {
        if (j == n) {
          j = 0;
        }
        item = PySequence_GetItem(values, j);
        if (item == 0) {
          igraph_vector_int_destroy(&es);
          Py_DECREF(list);
          return -1;
        }
        /* No need to Py_INCREF(item), PySequence_GetItem returns a new reference */
        if (PyList_SetItem(list, VECTOR(es)[i], item)) {
          Py_DECREF(item);
          Py_DECREF(list);
          return -1;
        }
        /* PyList_SET_ITEM stole a reference to the item automatically */
      }
      igraph_vector_int_destroy(&es);
      if (PyDict_SetItem(dict, attrname, list)) {
        Py_DECREF(list);
        return -1;
      }
      Py_DECREF(list);   /* compensating for PyDict_SetItem */
    }
  }
  return 0;
}

PyObject* igraphmodule_EdgeSeq_set_attribute_values(igraphmodule_EdgeSeqObject *self,
    PyObject *args, PyObject *kwds) {
  static char* kwlist[] = { "attrname", "values", NULL };
  PyObject *attrname, *values;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "OO", kwlist,
                   &attrname, &values))
    return NULL;

  if (igraphmodule_EdgeSeq_set_attribute_values_mapping(self, attrname, values))
    return NULL;

  Py_RETURN_NONE;
}

/**
 * \ingroup python_interface_edgqseq
 * \brief Selects a single edge from the edge sequence based on some criteria
 */
PyObject* igraphmodule_EdgeSeq_find(igraphmodule_EdgeSeqObject *self, PyObject *args) {
  PyObject *item;
  Py_ssize_t i, n;

  if (!PyArg_ParseTuple(args, "O", &item))
    return NULL;

  if (PyCallable_Check(item)) {
    /* Call the callable for every edge in the current sequence and return
     * the first one for which it evaluates to True */
    n = PySequence_Size((PyObject*)self);
    for (i = 0; i < n; i++) {
      PyObject *edge = PySequence_GetItem((PyObject*)self, i);
      PyObject *call_result;
      if (edge == 0)
        return NULL;
      call_result = PyObject_CallFunctionObjArgs(item, edge, NULL);
      if (call_result == 0) {
        Py_DECREF(edge);
        return NULL;
      }
      if (PyObject_IsTrue(call_result)) {
        Py_DECREF(call_result);
        return edge;  /* reference passed to caller */
      }
      Py_DECREF(call_result);
      Py_DECREF(edge);
    }
  } else if (PyLong_Check(item)) {
    /* Integers are interpreted as indices on the edge set and NOT on the
     * original, untouched edge sequence of the graph */
    Py_ssize_t index = PyLong_AsSsize_t(item);
    if (PyErr_Occurred()) {
      return NULL;
    } else {
      return PySequence_GetItem((PyObject*)self, index);
    }
  }

  PyErr_SetString(PyExc_IndexError, "no such edge");
  return NULL;
}

/**
 * \ingroup python_interface_edgeseq
 * \brief Selects a subset of the edge sequence based on some criteria
 */
PyObject* igraphmodule_EdgeSeq_select(igraphmodule_EdgeSeqObject *self, PyObject *args) {
  igraphmodule_EdgeSeqObject *result;
  igraphmodule_GraphObject *gr;
  igraph_integer_t igraph_idx;
  igraph_bool_t working_on_whole_graph = igraph_es_is_all(&self->es);
  igraph_vector_int_t v, v2;
  Py_ssize_t i, j, n, m;

  gr = self->gref;
  result = igraphmodule_EdgeSeq_copy(self);
  if (result == 0) {
    return NULL;
  }

  /* First, filter by positional arguments */
  n = PyTuple_Size(args);
  for (i = 0; i < n; i++) {
    PyObject *item = PyTuple_GetItem(args, i);
    if (item == 0) {
      Py_DECREF(result);
      return NULL;
    } else if (item == Py_None) {
      /* None means: select nothing */
      igraph_es_destroy(&result->es);
      igraph_es_none(&result->es);
      /* We can simply bail out here */
      return (PyObject*) result;
    } else if (PyCallable_Check(item)) {
      /* Call the callable for every edge in the current sequence to
       * determine what's up */
      igraph_bool_t was_excluded = false;
      igraph_vector_int_t v;

      if (igraph_vector_int_init(&v, 0)) {
        igraphmodule_handle_igraph_error();
        return 0;
      }

      m = PySequence_Size((PyObject*)result);
      for (j = 0; j < m; j++) {
        PyObject *edge = PySequence_GetItem((PyObject*)result, j);
        PyObject *call_result;
        if (edge == 0) {
          Py_DECREF(result);
          igraph_vector_int_destroy(&v);
          return NULL;
        }
        call_result = PyObject_CallFunctionObjArgs(item, edge, NULL);
        if (call_result == 0) {
          Py_DECREF(edge); Py_DECREF(result);
          igraph_vector_int_destroy(&v);
          return NULL;
        }
        if (PyObject_IsTrue(call_result)) {
          igraph_vector_int_push_back(&v,
            igraphmodule_Edge_get_index_as_igraph_integer((igraphmodule_EdgeObject*)edge));
        } else {
          was_excluded = 1;
        }
        Py_DECREF(call_result);
        Py_DECREF(edge);
      }

      if (was_excluded) {
        igraph_es_destroy(&result->es);
        if (igraph_es_vector_copy(&result->es, &v)) {
          Py_DECREF(result);
          igraph_vector_int_destroy(&v);
          igraphmodule_handle_igraph_error();
          return NULL;
        }
      }

      igraph_vector_int_destroy(&v);
    } else if (PyLong_Check(item)) {
      /* Integers are treated specially: from now on, all remaining items
       * in the argument list must be integers and they will be used together
       * to restrict the edge set. Integers are interpreted as indices on the
       * edge set and NOT on the original, untouched edge sequence of the
       * graph */
      if (igraph_vector_int_init(&v, 0)) {
        igraphmodule_handle_igraph_error();
        return 0;
      }

      if (!working_on_whole_graph) {
        /* Extract the current vertex sequence into a vector */
        if (igraph_vector_int_init(&v2, 0)) {
          igraph_vector_int_destroy(&v);
          igraphmodule_handle_igraph_error();
          return 0;
        }
        if (igraph_es_as_vector(&gr->g, self->es, &v2)) {
          igraph_vector_int_destroy(&v);
          igraph_vector_int_destroy(&v2);
          igraphmodule_handle_igraph_error();
          return 0;
        }
        m = igraph_vector_int_size(&v2);
      } else {
        /* v2 left uninitialized, we are not going to use it as it would
         * simply contain integers from 0 to ecount(g)-1 */
        m = igraph_ecount(&gr->g);
      }

      for (; i < n; i++) {
        PyObject *item2 = PyTuple_GetItem(args, i);
        igraph_integer_t idx;

        if (item2 == 0) {
          Py_DECREF(result);
          igraph_vector_int_destroy(&v);
          if (!working_on_whole_graph) {
            igraph_vector_int_destroy(&v2);
          }
          return NULL;
        }
        if (!PyLong_Check(item2)) {
          Py_DECREF(result);
          PyErr_SetString(PyExc_TypeError, "edge indices expected");
          igraph_vector_int_destroy(&v);
          if (!working_on_whole_graph) {
            igraph_vector_int_destroy(&v2);
          }
          return NULL;
        }
        if (igraphmodule_PyObject_to_integer_t(item2, &idx)) {
          Py_DECREF(result);
          igraph_vector_int_destroy(&v);
          if (!working_on_whole_graph) {
            igraph_vector_int_destroy(&v2);
          }
          return NULL;
        }
        if (idx >= m || idx < 0) {
          Py_DECREF(result);
          PyErr_SetString(PyExc_ValueError, "edge index out of range");
          igraph_vector_int_destroy(&v);
          if (!working_on_whole_graph) {
            igraph_vector_int_destroy(&v2);
          }
          return NULL;
        }
        if (igraph_vector_int_push_back(&v, working_on_whole_graph ? idx : VECTOR(v2)[idx])) {
          Py_DECREF(result);
          igraphmodule_handle_igraph_error();
          igraph_vector_int_destroy(&v);
          if (!working_on_whole_graph) {
            igraph_vector_int_destroy(&v2);
          }
          return NULL;
        }
      }

      if (!working_on_whole_graph) {
        igraph_vector_int_destroy(&v2);
      }

      igraph_es_destroy(&result->es);

      if (igraph_es_vector_copy(&result->es, &v)) {
        Py_DECREF(result);
        igraphmodule_handle_igraph_error();
        igraph_vector_int_destroy(&v);
        return NULL;
      }

      igraph_vector_int_destroy(&v);
    } else {
      /* Iterators and everything that was not handled directly */
      PyObject *iter, *item2;

      /* Allocate stuff */
      if (igraph_vector_int_init(&v, 0)) {
        igraphmodule_handle_igraph_error();
        return 0;
      }
      if (!working_on_whole_graph) {
        /* Extract the current vertex sequence into a vector */
        if (igraph_vector_int_init(&v2, 0)) {
          igraph_vector_int_destroy(&v);
          igraphmodule_handle_igraph_error();
          return 0;
        }
        if (igraph_es_as_vector(&gr->g, self->es, &v2)) {
          igraph_vector_int_destroy(&v);
          igraph_vector_int_destroy(&v2);
          igraphmodule_handle_igraph_error();
          return 0;
        }
        m = igraph_vector_int_size(&v2);
      } else {
        /* v2 left uninitialized, we are not going to use it as it would
         * simply contain integers from 0 to ecount(g)-1 */
        m = igraph_ecount(&gr->g);
      }

      /* Create an appropriate iterator */
      if (PySlice_Check(item)) {
        /* Create an iterator from the slice (which is not iterable by default )*/
        Py_ssize_t start, stop, step, sl;
        PyObject* range;
        igraph_bool_t ok;

        ok = (PySlice_GetIndicesEx(item, m, &start, &stop, &step, &sl) == 0);
        if (ok) {
          range = igraphmodule_PyRange_create(start, stop, step);
          ok = (range != 0);
        }
        if (ok) {
          iter = PyObject_GetIter(range);
          Py_DECREF(range);
          ok = (iter != 0);
        }
        if (!ok) {
          igraph_vector_int_destroy(&v);
          if (!working_on_whole_graph) {
            igraph_vector_int_destroy(&v2);
          }
          PyErr_SetString(PyExc_TypeError, "error while converting slice to iterator");
          Py_DECREF(result);
          return 0;
        }
      } else {
        /* Simply create the iterator corresponding to the object */
        iter = PyObject_GetIter(item);
      }

      /* Did we manage to get an iterator? */
      if (iter == 0) {
        igraph_vector_int_destroy(&v);
        if (!working_on_whole_graph) {
          igraph_vector_int_destroy(&v2);
        }
        PyErr_SetString(PyExc_TypeError, "invalid edge filter among positional arguments");
        Py_DECREF(result);
        return 0;
      }
      /* Do the iteration */
      while ((item2 = PyIter_Next(iter)) != 0) {
        if (igraphmodule_PyObject_to_integer_t(item2, &igraph_idx)) {
          /* We simply ignore elements that we don't know */
          Py_DECREF(item2);
        } else {
          Py_DECREF(item2);
          if (igraph_idx >= m || igraph_idx < 0) {
            PyErr_SetString(PyExc_ValueError, "edge index out of range");
            Py_DECREF(result);
            Py_DECREF(iter);
            igraph_vector_int_destroy(&v);
            if (!working_on_whole_graph) {
              igraph_vector_int_destroy(&v2);
            }
            return NULL;
          }
          if (igraph_vector_int_push_back(&v, working_on_whole_graph ? igraph_idx : VECTOR(v2)[igraph_idx])) {
            Py_DECREF(result);
            Py_DECREF(iter);
            igraphmodule_handle_igraph_error();
            igraph_vector_int_destroy(&v);
            if (!working_on_whole_graph) {
              igraph_vector_int_destroy(&v2);
            }
            return NULL;
          }
        }
      }

      /* Deallocate stuff */
      if (!working_on_whole_graph) {
        igraph_vector_int_destroy(&v2);
      }

      Py_DECREF(iter);
      if (PyErr_Occurred()) {
        igraph_vector_int_destroy(&v);
        Py_DECREF(result);
        return 0;
      }

      igraph_es_destroy(&result->es);

      if (igraph_es_vector_copy(&result->es, &v)) {
        Py_DECREF(result);
        igraphmodule_handle_igraph_error();
        igraph_vector_int_destroy(&v);
        return NULL;
      }
      igraph_vector_int_destroy(&v);
    }
  }

  return (PyObject*)result;
}


/**
 * \ingroup python_interface_edgeseq
 * Method table for the \c igraph.EdgeSeq object
 */
PyMethodDef igraphmodule_EdgeSeq_methods[] = {
  {"attribute_names", (PyCFunction)igraphmodule_EdgeSeq_attribute_names,
   METH_NOARGS,
   "attribute_names()\n--\n\n"
   "Returns the attribute name list of the graph's edges\n"
  },
  {"find", (PyCFunction)igraphmodule_EdgeSeq_find,
   METH_VARARGS,
   "find(condition)\n--\n\n"
   "For internal use only.\n"
  },
  {"get_attribute_values", (PyCFunction)igraphmodule_EdgeSeq_get_attribute_values,
   METH_O,
   "get_attribute_values(attrname)\n--\n\n"
   "Returns the value of a given edge attribute for all edges.\n\n"
   "@param attrname: the name of the attribute\n"
  },
  {"is_all", (PyCFunction)igraphmodule_EdgeSeq_is_all, METH_NOARGS,
   "is_all()\n--\n\n"
   "Returns whether the edge sequence contains all the edges exactly once, in\n"
   "the order of their edge IDs.\n\n"
   "This is used for optimizations in some of the edge selector routines.\n"
  },
  {"set_attribute_values", (PyCFunction)igraphmodule_EdgeSeq_set_attribute_values,
   METH_VARARGS | METH_KEYWORDS,
   "set_attribute_values(attrname, values)\n--\n\n"
   "Sets the value of a given edge attribute for all vertices\n"
   "@param attrname: the name of the attribute\n"
   "@param values: the new attribute values in a list\n"
  },
  {"select", (PyCFunction)igraphmodule_EdgeSeq_select,
   METH_VARARGS,
   "select(*args, **kwds)\n--\n\n"
   "For internal use only.\n"
  },
  {NULL}
};

/**
 * \ingroup python_interface_edgeseq
 * Returns the graph where the edge sequence belongs
 */
PyObject* igraphmodule_EdgeSeq_get_graph(igraphmodule_EdgeSeqObject* self,
  void* closure) {
  Py_INCREF(self->gref);
  return (PyObject*)self->gref;
}

/**
 * \ingroup python_interface_edgeseq
 * Returns the indices of the edges in this edge sequence
 */
PyObject* igraphmodule_EdgeSeq_get_indices(igraphmodule_EdgeSeqObject* self,
  void* closure) {
  igraphmodule_GraphObject *gr = self->gref;
  igraph_vector_int_t es;
  PyObject *result;

  if (igraph_vector_int_init(&es, 0)) {
    igraphmodule_handle_igraph_error();
    return 0;
  }
  if (igraph_es_as_vector(&gr->g, self->es, &es)) {
    igraphmodule_handle_igraph_error();
    igraph_vector_int_destroy(&es);
    return 0;
  }

  result = igraphmodule_vector_int_t_to_PyList(&es);
  igraph_vector_int_destroy(&es);

  return result;
}

/**
 * \ingroup python_interface_edgeseq
 * Getter/setter table for the \c igraph.EdgeSeq object
 */
PyGetSetDef igraphmodule_EdgeSeq_getseters[] = {
  {"graph", (getter)igraphmodule_EdgeSeq_get_graph, NULL,
      "The graph the edge sequence belongs to", NULL},
  {"indices", (getter)igraphmodule_EdgeSeq_get_indices, NULL,
      "The edge indices in this edge sequence", NULL,
  },
  {NULL}
};

/**
 * \ingroup python_interface_edgeseq
 * Member table for the \c igraph.EdgeSeq object
 */
PyMemberDef igraphmodule_EdgeSeq_members[] = {
  {"__weaklistoffset__", T_PYSSIZET, offsetof(igraphmodule_EdgeSeqObject, weakreflist), READONLY},
  { 0 }
};

PyDoc_STRVAR(
  igraphmodule_EdgeSeq_doc,
  "Low-level representation of an edge sequence.\n\n" /* tp_doc */
  "Don't use it directly, use L{igraph.EdgeSeq} instead.\n\n"
  "@deffield ref: Reference"
);

int igraphmodule_EdgeSeq_register_type() {
  PyType_Slot slots[] = {
    { Py_tp_init, igraphmodule_EdgeSeq_init },
    { Py_tp_dealloc, igraphmodule_EdgeSeq_dealloc },
    { Py_tp_members, igraphmodule_EdgeSeq_members },
    { Py_tp_methods, igraphmodule_EdgeSeq_methods },
    { Py_tp_getset, igraphmodule_EdgeSeq_getseters },
    { Py_tp_doc, (void*) igraphmodule_EdgeSeq_doc },

    { Py_sq_length, igraphmodule_EdgeSeq_sq_length },
    { Py_sq_item, igraphmodule_EdgeSeq_sq_item },

    { Py_mp_subscript, igraphmodule_EdgeSeq_get_attribute_values_mapping },
    { Py_mp_ass_subscript, igraphmodule_EdgeSeq_set_attribute_values_mapping },
  
    { 0 }
  };

  PyType_Spec spec = {
    "igraph._igraph.EdgeSeq",                   /* name */
    sizeof(igraphmodule_EdgeSeqObject),         /* basicsize */
    0,                                          /* itemsize */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,   /* flags */
    slots,                                      /* slots */
  };

  igraphmodule_EdgeSeqType = (PyTypeObject*) PyType_FromSpec(&spec);
  return igraphmodule_EdgeSeqType == 0;
}
