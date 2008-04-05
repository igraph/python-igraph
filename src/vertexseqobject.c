/* -*- mode: C -*-  */
/* vim: set ts=2 sts=2 sw=2 et: */

/* 
   IGraph library.
   Copyright (C) 2006  Gabor Csardi <csardi@rmki.kfki.hu>
   MTA RMKI, Konkoly-Thege Miklos st. 29-33, Budapest 1121, Hungary
   
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

#include "vertexseqobject.h"
#include "vertexobject.h"
#include "common.h"
#include "convert.h"
#include "error.h"

#define GET_GRAPH(obj) (((igraphmodule_GraphObject*)obj->gref)->g)

/**
 * \ingroup python_interface
 * \defgroup python_interface_vertexseq Vertex sequence object
 */

PyTypeObject igraphmodule_VertexSeqType;

/**
 * \ingroup python_interface_vertexseq
 * \brief Allocate a new vertex sequence object for a given graph
 * \return the allocated PyObject
 */
PyObject* igraphmodule_VertexSeq_new(PyTypeObject *subtype,
  PyObject *args, PyObject *kwds) {
  igraphmodule_VertexSeqObject *o;

  o=(igraphmodule_VertexSeqObject*)PyType_GenericNew(subtype, args, kwds);
  if (o == NULL) return NULL;

  igraph_vs_all(&o->vs);
  o->gref=0;
  o->weakreflist=0;

  RC_ALLOC("VertexSeq", o);

  return (PyObject*)o;
}

/**
 * \ingroup python_interface_vertexseq
 * \brief Copies a vertex sequence object
 * \return the copied PyObject
 */
igraphmodule_VertexSeqObject*
igraphmodule_VertexSeq_copy(igraphmodule_VertexSeqObject* o) {
  igraphmodule_VertexSeqObject *copy;

  copy=(igraphmodule_VertexSeqObject*)PyType_GenericNew(o->ob_type, 0, 0);
  if (copy == NULL) return NULL;
 
  if (igraph_vs_type(&o->vs) == IGRAPH_VS_VECTOR) {
    igraph_vector_t v;
    if (igraph_vector_copy(&v, o->vs.data.vecptr)) {
      igraphmodule_handle_igraph_error();
      return 0;
    }
    if (igraph_vs_vector_copy(&copy->vs, &v)) {
      igraphmodule_handle_igraph_error();
      igraph_vector_destroy(&v);
      return 0;
    }
    igraph_vector_destroy(&v);
  } else {
    copy->vs = o->vs;
  }

  copy->gref = o->gref;
  if (o->gref) Py_INCREF(o->gref);
  RC_ALLOC("VertexSeq(copy)", copy);

  return copy;
}

/**
 * \ingroup python_interface_vertexseq
 * \brief Initialize a new vertex sequence object for a given graph
 * \return the initialized PyObject
 */
int igraphmodule_VertexSeq_init(igraphmodule_VertexSeqObject *self,
  PyObject *args, PyObject *kwds) {
  static char *kwlist[] = { "graph", "vertices", NULL };
  PyObject *g, *vsobj=Py_None;
  igraph_vs_t vs;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O!|O", kwlist,
    &igraphmodule_GraphType, &g, &vsobj))
      return -1;

  if (vsobj == Py_None) {
    /* If vs is None, we are selecting all the vertices */
    igraph_vs_all(&vs);
  } else if (PyInt_Check(vsobj)) {
    /* We selected a single vertex */
    long idx = PyInt_AsLong(vsobj);
    if (idx < 0 || idx >= igraph_vcount(&((igraphmodule_GraphObject*)g)->g)) {
      PyErr_SetString(PyExc_ValueError, "vertex index out of bounds");
      return -1;
    }
    igraph_vs_1(&vs, idx);
  } else {
    igraph_vector_t v;
    igraph_integer_t n = igraph_vcount(&((igraphmodule_GraphObject*)g)->g);
    if (igraphmodule_PyObject_to_vector_t(vsobj, &v, 1, 0))
      return -1;
    if (!igraph_vector_isininterval(&v, 0, n-1)) {
      igraph_vector_destroy(&v);
      PyErr_SetString(PyExc_ValueError, "vertex index out of bounds");
      return -1;
    }
    if (igraph_vs_vector_copy(&vs, &v)) {
      igraphmodule_handle_igraph_error();
      igraph_vector_destroy(&v);
      return -1;
    }
    igraph_vector_destroy(&v);
  }

  self->vs = vs;
  Py_INCREF(g);
  self->gref = (igraphmodule_GraphObject*)g;

  return 0;
}

/**
 * \ingroup python_interface_vertexseq
 * \brief Deallocates a Python representation of a given vertex sequence object
 */
void igraphmodule_VertexSeq_dealloc(igraphmodule_VertexSeqObject* self) {
  if (self->weakreflist != NULL)
    PyObject_ClearWeakRefs((PyObject *) self);
  if (self->gref) {
    igraph_vs_destroy(&self->vs);
    Py_DECREF(self->gref);
    self->gref=0;
  }
  self->ob_type->tp_free((PyObject*)self);
  RC_DEALLOC("VertexSeq", self);
}

/**
 * \ingroup python_interface_vertexseq
 * \brief Returns the length of the sequence
 */
int igraphmodule_VertexSeq_sq_length(igraphmodule_VertexSeqObject* self) {
  igraph_t *g;
  igraph_integer_t result;
  if (!self->gref) return -1;
  g=&GET_GRAPH(self);
  if (igraph_vs_size(g, &self->vs, &result)) {
    igraphmodule_handle_igraph_error();
    return -1;
  }
  return (int)result;
}

/**
 * \ingroup python_interface_vertexseq
 * \brief Returns the item at the given index in the sequence
 */
PyObject* igraphmodule_VertexSeq_sq_item(igraphmodule_VertexSeqObject* self,
                     Py_ssize_t i) {
  igraph_t *g;
  long idx = -1;

  if (!self->gref) return NULL;
  g=&GET_GRAPH(self);
  switch (igraph_vs_type(&self->vs)) {
    case IGRAPH_VS_ALL:
      if (i >= 0 && i < (long)igraph_vcount(g)) idx = i;
      break;
    case IGRAPH_VS_VECTOR:
    case IGRAPH_VS_VECTORPTR:
      if (i >= 0 && i < igraph_vector_size(self->vs.data.vecptr))
        idx = (long)VECTOR(*self->vs.data.vecptr)[i];
      break;
    case IGRAPH_VS_1:
      if (i == 0) idx = (long)self->vs.data.vid;
      break;
    case IGRAPH_VS_SEQ:
      if (i >= 0 && i < self->vs.data.seq.to - self->vs.data.seq.from)
        idx = (long)(self->vs.data.seq.from + i);
      break;
    /* TODO: IGRAPH_VS_ADJ, IGRAPH_VS_NONADJ - someday :) They are unused
       yet in the Python interface */
  }

  if (idx < 0) {
    PyErr_SetString(PyExc_IndexError, "vertex index out of range");
    return NULL;
  }

  return igraphmodule_Vertex_New(self->gref, idx);
}

/** \ingroup python_interface_vertexseq
 * \brief Returns the list of attribute names
 */
PyObject* igraphmodule_VertexSeq_attribute_names(igraphmodule_VertexSeqObject* self) {
  return igraphmodule_Graph_vertex_attributes(self->gref);
}

/** \ingroup python_interface_vertexseq
 * \brief Returns the count of attribute names
 */
PyObject* igraphmodule_VertexSeq_attribute_count(igraphmodule_VertexSeqObject* self) {
  PyObject *list;
  long int size;
  
  list=igraphmodule_Graph_vertex_attributes(self->gref);
  size=PySequence_Size(list);
  Py_DECREF(list);

  return Py_BuildValue("i", size);
}

/** \ingroup python_interface_vertexseq
 * \brief Returns the list of values for a given attribute
 */
PyObject* igraphmodule_VertexSeq_get_attribute_values(igraphmodule_VertexSeqObject* self, PyObject* o) {
  igraphmodule_GraphObject *gr = self->gref;
  PyObject *result=0, *values, *item;
  long int i, n;

  PyErr_Clear();
  values=PyDict_GetItem(((PyObject**)gr->g.attr)[ATTRHASH_IDX_VERTEX], o);
  if (!values) {
    PyErr_SetString(PyExc_KeyError, "Attribute does not exist");
    return NULL;
  } else if (PyErr_Occurred()) return NULL;
  
  switch (igraph_vs_type(&self->vs)) {
    case IGRAPH_VS_NONE:
      n = 0;
      result = PyList_New(0);
      break;

    case IGRAPH_VS_ALL:
      n = PyList_Size(values);
      result = PyList_New(n);
      if (!result) return 0;
      
      for (i=0; i<n; i++) {
        item = PyList_GET_ITEM(values, i);
        Py_INCREF(item);
        PyList_SET_ITEM(result, i, item);
      }
      break;

    case IGRAPH_VS_VECTOR:
    case IGRAPH_VS_VECTORPTR:
      n = igraph_vector_size(self->vs.data.vecptr);
      result = PyList_New(n);
      if (!result) return 0;

      for (i=0; i<n; i++) {
        item = PyList_GET_ITEM(values, (long)VECTOR(*self->vs.data.vecptr)[i]);
        Py_INCREF(item);
        PyList_SET_ITEM(result, i, item);
      }
      break;

    case IGRAPH_VS_SEQ:
      n = self->vs.data.seq.to - self->vs.data.seq.from;
      result = PyList_New(n);
      if (!result) return 0;

      for (i=0; i<n; i++) {
        item = PyList_GET_ITEM(values, (long)self->vs.data.seq.from+i);
        Py_INCREF(item);
        PyList_SET_ITEM(result, i, item);
      }
      break;

    default:
      PyErr_SetString(PyExc_RuntimeError, "invalid vertex selector");
  }

  return result;
}

PyObject* igraphmodule_VertexSeq_get_attribute_values_mapping(igraphmodule_VertexSeqObject *self, PyObject *o) {
  /* Handle integer indices according to the sequence protocol */
  if (PyInt_Check(o)) return igraphmodule_VertexSeq_sq_item(self, PyInt_AsLong(o));
  if (PyTuple_Check(o)) {
    /* Return a restricted VertexSeq */
    return igraphmodule_VertexSeq_select(self, o, NULL);
  } else if (PyList_Check(o)) {
    /* Return a restricted VertexSeq */
    PyObject *t = PyList_AsTuple(o);
    PyObject *result;
    if (!t) return NULL;
    result = igraphmodule_VertexSeq_select(self, t, NULL);
    Py_DECREF(t);
    return result;
  }
  return igraphmodule_VertexSeq_get_attribute_values(self, o);
}

/** \ingroup python_interface_vertexseq
 * \brief Sets the list of values for a given attribute
 */
int igraphmodule_VertexSeq_set_attribute_values_mapping(igraphmodule_VertexSeqObject* self, PyObject* attrname, PyObject* values) {
  PyObject *dict, *list, *item;
  igraphmodule_GraphObject *gr;
  igraph_vector_t vs;
  long i, n;

  gr = self->gref;
  dict = ((PyObject**)gr->g.attr)[ATTRHASH_IDX_VERTEX];
  
  if (values == 0) {
    if (igraph_vs_type(&self->vs) == IGRAPH_VS_ALL)
      return PyDict_DelItem(dict, attrname);
    PyErr_SetString(PyExc_TypeError, "can't delete attribute from a vertex sequence not representing the whole graph");
    return -1;
  }

  n=PySequence_Size(values);
  if (n<0) return -1;

  if (igraph_vs_type(&self->vs) == IGRAPH_VS_ALL) {
    if (n != (long)igraph_vcount(&gr->g)) {
      PyErr_SetString(PyExc_ValueError, "value list length must be equal to the number of vertices in the graph");
      return -1;
    }

    /* Check if we already have attributes with the given name */
    list = PyDict_GetItem(dict, attrname);
    if (list != 0) {
      /* Yes, we have. Modify its items to the items found in values */
      for (i=0; i<n; i++) {
        item = PyList_GetItem(values, i);
        if (item == 0) return -1;
        Py_INCREF(item);
        if (PyList_SetItem(list, i, item)) {
          Py_DECREF(item);
          return -1;
        } /* PyList_SetItem stole a reference to the item automatically */ 
      }
    } else if (values != 0) {
      /* We don't have attributes with the given name yet. Create an entry
       * in the dict, create a new list and copy everything */
      list = PyList_New(n);
      if (list == 0) return -1;
      for (i=0; i<n; i++) {
        item = PyList_GET_ITEM(values, i);
        if (item == 0) { Py_DECREF(list); return -1; }
        Py_INCREF(item);
        PyList_SET_ITEM(list, i, item);
      }
      if (PyDict_SetItem(dict, attrname, list)) {
        Py_DECREF(list);
        return -1;
      }
    }
  } else {
    /* We are working with a subset of the graph. Convert the sequence to a
     * vector and loop through it */
    if (igraph_vector_init(&vs, 0)) {
      igraphmodule_handle_igraph_error();
      return -1;
    } 
    if (igraph_vs_as_vector(&gr->g, self->vs, &vs)) {
      igraphmodule_handle_igraph_error();
      igraph_vector_destroy(&vs);
      return -1;
    }
    if (n != (long)igraph_vector_size(&vs)) {
      PyErr_SetString(PyExc_ValueError, "value list length must be equal to the number of vertices in the vertex sequence");
      igraph_vector_destroy(&vs);
      return -1;
    }
    /* Check if we already have attributes with the given name */
    list = PyDict_GetItem(dict, attrname);
    if (list != 0) {
      /* Yes, we have. Modify its items to the items found in values */
      for (i=0; i<n; i++) {
        item = PyList_GetItem(values, i);
        if (item == 0) {
          igraph_vector_destroy(&vs);
          return -1;
        }
        Py_INCREF(item);
        if (PyList_SetItem(list, (long)VECTOR(vs)[i], item)) {
          Py_DECREF(item);
          igraph_vector_destroy(&vs);
          return -1;
        } /* PyList_SetItem stole a reference to the item automatically */ 
      }
    } else if (values != 0) {
      /* We don't have attributes with the given name yet. Create an entry
       * in the dict, create a new list, fill with None for vertices not in the
       * sequence and copy the rest */
      long n2 = igraph_vcount(&gr->g);
      list = PyList_New(n2);
      if (list == 0) {
        igraph_vector_destroy(&vs);
        return -1;
      }
      for (i=0; i<n2; i++) {
        Py_INCREF(Py_None);
        PyList_SET_ITEM(list, i, Py_None);
      }
      for (i=0; i<n; i++) {
        item = PyList_GET_ITEM(values, i);
        if (item == 0) {
          igraph_vector_destroy(&vs);
          Py_DECREF(list); return -1;
        }
        Py_INCREF(item);
        PyList_SET_ITEM(list, (long)VECTOR(vs)[i], item);
      }
      igraph_vector_destroy(&vs);
      if (PyDict_SetItem(dict, attrname, list)) {
        Py_DECREF(list);
        return -1;
      }
    }
  }

  return 0;
}

PyObject* igraphmodule_VertexSeq_set_attribute_values(igraphmodule_VertexSeqObject *self, PyObject *args, PyObject *kwds) {
  static char* kwlist[] = { "attrname", "values", NULL };
  PyObject *attrname, *values;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "OO", kwlist,
           &attrname, &values))
  return NULL;

  if (igraphmodule_VertexSeq_set_attribute_values_mapping(self, attrname, values))
  return NULL;

  Py_RETURN_NONE;
}

/**
 * \ingroup python_interface_vertexseq
 * \brief Selects a subset of the vertex sequence based on some criteria
 */
PyObject* igraphmodule_VertexSeq_select(igraphmodule_VertexSeqObject *self,
  PyObject *args, PyObject *kwds) {
  igraphmodule_VertexSeqObject *result;
  igraphmodule_GraphObject *gr;
  long i, j, n, m;

  gr=self->gref;
  result=igraphmodule_VertexSeq_copy(self);
  if (result==0) return NULL;

  /* First, filter by positional arguments */
  n = PyTuple_Size(args);
  for (i=0; i<n; i++) {
    PyObject *item = PyTuple_GET_ITEM(args, i);
    if (item == Py_None) {
      /* None means: select nothing */
      igraph_vs_destroy(&result->vs);
      igraph_vs_none(&result->vs);
      /* We can simply bail out here */
      return (PyObject*)result;
    } else if (PyCallable_Check(item)) {
      /* Call the callable for every vertex in the current sequence to
       * determine what's up */
      igraph_bool_t was_excluded = 0;
      igraph_vector_t v;

      if (igraph_vector_init(&v, 0)) {
        igraphmodule_handle_igraph_error();
        return 0;
      }

      m = PySequence_Size((PyObject*)result);
      for (j=0; j<m; j++) {
        PyObject *vertex = PySequence_GetItem((PyObject*)result, j);
        PyObject *call_result;
        if (vertex == 0) {
          Py_DECREF(result);
          igraph_vector_destroy(&v);
          return NULL;
        }
        call_result = PyObject_CallFunctionObjArgs(item, vertex, NULL);
        if (call_result == 0) {
          Py_DECREF(vertex); Py_DECREF(result);
          igraph_vector_destroy(&v);
          return NULL;
        }
        if (PyObject_IsTrue(call_result))
          igraph_vector_push_back(&v,
            igraphmodule_Vertex_get_index_long((igraphmodule_VertexObject*)vertex));
        else was_excluded=1;
        Py_DECREF(call_result);
        Py_DECREF(vertex);
      }

      if (was_excluded) {
        igraph_vs_destroy(&result->vs);
        if (igraph_vs_vector_copy(&result->vs, &v)) {
          Py_DECREF(result);
          igraph_vector_destroy(&v);
          igraphmodule_handle_igraph_error();
          return NULL;
        }
      }

      igraph_vector_destroy(&v);
    } else if (PyInt_Check(item)) {
      /* Integers are treated specially: from now on, all remaining items
       * in the argument list must be integers and they will be used together
       * to restrict the vertex set. Integers are interpreted as indices on the
       * vertex set and NOT on the original, untouched vertex sequence of the
       * graph */
      igraph_vector_t v, v2;
      if (igraph_vector_init(&v, 0)) {
        igraphmodule_handle_igraph_error();
        return 0;
      }
      if (igraph_vector_init(&v2, 0)) {
        igraph_vector_destroy(&v);
        igraphmodule_handle_igraph_error();
        return 0;
      }
      if (igraph_vs_as_vector(&gr->g, result->vs, &v2)) {
        igraph_vector_destroy(&v);
        igraph_vector_destroy(&v2);
        igraphmodule_handle_igraph_error();
        return 0;
      }
      for (; i<n; i++) {
        PyObject *item2 = PyTuple_GET_ITEM(args, i);
        long idx;
        if (!PyInt_Check(item2)) {
          Py_DECREF(result);
          PyErr_SetString(PyExc_TypeError, "vertex indices expected");
          igraph_vector_destroy(&v);
          igraph_vector_destroy(&v2);
          return NULL;
        }
        idx = PyInt_AsLong(item2);
        if (igraph_vector_push_back(&v, VECTOR(v2)[idx])) {
          Py_DECREF(result);
          igraphmodule_handle_igraph_error();
          igraph_vector_destroy(&v);
          igraph_vector_destroy(&v2);
          return NULL;
        }
      }
      igraph_vector_destroy(&v2);
      igraph_vs_destroy(&result->vs);
      if (igraph_vs_vector_copy(&result->vs, &v)) {
        Py_DECREF(result);
        igraphmodule_handle_igraph_error();
        igraph_vector_destroy(&v);
        return NULL;
      }
      igraph_vector_destroy(&v);
    } else {
      /* Iterators and everything that was not handled directly */
      PyObject *iter, *item2;
      igraph_vector_t v, v2;
      
      iter = PyObject_GetIter(item);
      if (iter == 0) {
        PyErr_SetString(PyExc_TypeError, "invalid vertex filter among positional arguments");
        Py_DECREF(result);
        return 0;
      }
      /* Allocate stuff */
      if (igraph_vector_init(&v, 0)) {
        Py_DECREF(iter);
        igraphmodule_handle_igraph_error();
        return 0;
      }
      if (igraph_vector_init(&v2, 0)) {
        Py_DECREF(iter);
        igraph_vector_destroy(&v);
        igraphmodule_handle_igraph_error();
        return 0;
      }
      if (igraph_vs_as_vector(&gr->g, result->vs, &v2)) {
        Py_DECREF(iter);
        igraph_vector_destroy(&v);
        igraph_vector_destroy(&v2);
        igraphmodule_handle_igraph_error();
        return 0;
      }
      /* Do the iteration */
      while ((item2=PyIter_Next(iter)) != 0) {
        if (PyInt_Check(item2)) {
          long idx = PyInt_AsLong(item2);
          Py_DECREF(item2);
          if (igraph_vector_push_back(&v, VECTOR(v2)[idx])) {
            Py_DECREF(result);
            Py_DECREF(iter);
            igraphmodule_handle_igraph_error();
            igraph_vector_destroy(&v);
            igraph_vector_destroy(&v2);
            return NULL;
          }
        } else {
          /* We simply ignore elements that we don't know */
          Py_DECREF(item2);
        }
      }
      /* Deallocate stuff */
      igraph_vector_destroy(&v2);
      Py_DECREF(iter);
      if (PyErr_Occurred()) {
        igraph_vector_destroy(&v);
        Py_DECREF(result);
        return 0;
      }
      igraph_vs_destroy(&result->vs);
      if (igraph_vs_vector_copy(&result->vs, &v)) {
        Py_DECREF(result);
        igraphmodule_handle_igraph_error();
        igraph_vector_destroy(&v);
        return NULL;
      }
      igraph_vector_destroy(&v);
    }
  }

  return (PyObject*)result;
}

/**
 * \ingroup python_interface_vertexseq
 * Converts a vertex sequence to an igraph vector containing the corresponding
 * vertex indices. The vector MUST be initialized and will be resized if needed.
 * \return 0 if everything was ok, 1 otherwise
 */
int igraphmodule_VertexSeq_to_vector_t(igraphmodule_VertexSeqObject *self,
  igraph_vector_t *v) {
  return igraph_vs_as_vector(&self->gref->g, self->vs, v);
}

/**
 * \ingroup python_interface_vertexseq
 * Returns the graph where the vertex sequence belongs
 */
PyObject* igraphmodule_VertexSeq_get_graph(igraphmodule_VertexSeqObject* self,
  void* closure) {
  Py_INCREF(self->gref);
  return (PyObject*)self->gref;
}

/**
 * \ingroup python_interface_vertexseq
 * Returns the indices of the vertices in this vertex sequence 
 */
PyObject* igraphmodule_VertexSeq_get_indices(igraphmodule_VertexSeqObject* self,
  void* closure) {
  igraphmodule_GraphObject *gr = self->gref;
  igraph_vector_t vs;
  PyObject *result;

  if (igraph_vector_init(&vs, 0)) {
    igraphmodule_handle_igraph_error();
    return 0;
  } 
  if (igraph_vs_as_vector(&gr->g, self->vs, &vs)) {
    igraphmodule_handle_igraph_error();
    igraph_vector_destroy(&vs);
    return 0;
  }

  result = igraphmodule_vector_t_to_PyList(&vs, IGRAPHMODULE_TYPE_INT);
  igraph_vector_destroy(&vs);

  return result;
}

/**
 * \ingroup python_interface_vertexseq
 * Method table for the \c igraph.VertexSeq object
 */
PyMethodDef igraphmodule_VertexSeq_methods[] = {
  {"attribute_names", (PyCFunction)igraphmodule_VertexSeq_attribute_names,
   METH_NOARGS,
   "attribute_names() -> list\n\n"
   "Returns the attribute name list of the graph's vertices\n"
  },
  {"get_attribute_values", (PyCFunction)igraphmodule_VertexSeq_get_attribute_values,
   METH_O,
   "get_attribute_values(attrname) -> list\n"
   "Returns the value of a given vertex attribute for all vertices in a list.\n\n"
   "The values stored in the list are exactly the same objects that are stored\n"
   "in the vertex attribute, meaning that in the case of mutable objects,\n"
   "the modification of the list element does affect the attribute stored in\n"
   "the vertex. In the case of immutable objects, modification of the list\n"
   "does not affect the attribute values.\n\n"
   "@param attrname: the name of the attribute\n"
  },
  {"set_attribute_values", (PyCFunction)igraphmodule_VertexSeq_set_attribute_values,
   METH_VARARGS | METH_KEYWORDS,
   "set_attribute_values(attrname, values) -> list\n"
   "Sets the value of a given vertex attribute for all vertices\n\n"
   "@param attrname: the name of the attribute\n"
   "@param values: the new attribute values in a list\n"
  },
  {"select", (PyCFunction)igraphmodule_VertexSeq_select,
   METH_VARARGS | METH_KEYWORDS,
   "select(...) -> VertexSeq\n\n"
   "For internal use only.\n"
  },
  {NULL}
};

/**
 * \ingroup python_interface_vertexseq
 * This is the collection of functions necessary to implement the
 * vertex sequence as a real sequence (e.g. allowing to reference
 * vertices by indices)
 */
static PySequenceMethods igraphmodule_VertexSeq_as_sequence = {
  (lenfunc)igraphmodule_VertexSeq_sq_length,
  0,               /* sq_concat */
  0,               /* sq_repeat */
  (ssizeargfunc)igraphmodule_VertexSeq_sq_item, /* sq_item */
  0,                                          /* sq_slice */
  0,                                          /* sq_ass_item */
  0,                                          /* sq_ass_slice */
  0,                                          /* sq_contains */
  0,                                          /* sq_inplace_concat */
  0,                                          /* sq_inplace_repeat */
};

/**
 * \ingroup python_interface_vertexseq
 * This is the collection of functions necessary to implement the
 * vertex sequence as a mapping (which maps attribute names to values)
 */
static PyMappingMethods igraphmodule_VertexSeq_as_mapping = {
  /* this must be null, otherwise it f.cks up sq_length when inherited */
  (lenfunc) 0,
  /* returns the values of an attribute by name */
  (binaryfunc) igraphmodule_VertexSeq_get_attribute_values_mapping,
  /* sets the values of an attribute by name */
  (objobjargproc) igraphmodule_VertexSeq_set_attribute_values_mapping,
};

/**
 * \ingroup python_interface_vertexseq
 * Getter/setter table for the \c igraph.VertexSeq object
 */
PyGetSetDef igraphmodule_VertexSeq_getseters[] = {
  {"graph", (getter)igraphmodule_VertexSeq_get_graph, NULL,
      "The graph the vertex sequence belongs to", NULL,
  },
  {"indices", (getter)igraphmodule_VertexSeq_get_indices, NULL,
      "The vertex indices in this vertex sequence", NULL,
  },
  {NULL}
};

/** \ingroup python_interface_vertexseq
 * Python type object referencing the methods Python calls when it performs various operations on
 * a vertex sequence of a graph
 */
PyTypeObject igraphmodule_VertexSeqType =
{
  PyObject_HEAD_INIT(NULL)                    /* */
  0,                                          /* ob_size */
  "igraph.core.VertexSeq",                    /* tp_name */
  sizeof(igraphmodule_VertexSeqObject),       /* tp_basicsize */
  0,                                          /* tp_itemsize */
  (destructor)igraphmodule_VertexSeq_dealloc, /* tp_dealloc */
  0,                                          /* tp_print */
  0,                                          /* tp_getattr */
  0,                                          /* tp_setattr */
  0,                                          /* tp_compare */
  0,                                          /* tp_repr */
  0,                                          /* tp_as_number */
  &igraphmodule_VertexSeq_as_sequence,        /* tp_as_sequence */
  &igraphmodule_VertexSeq_as_mapping,         /* tp_as_mapping */
  0,                                          /* tp_hash */
  0,                                          /* tp_call */
  0,                                          /* tp_str */
  0,                                          /* tp_getattro */
  0,                                          /* tp_setattro */
  0,                                          /* tp_as_buffer */
  Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,   /* tp_flags */
  "Low-level representation of a vertex sequence.\n\n" /* tp_doc */
  "Don't use it directly, use L{igraph.VertexSeq} instead.\n\n"
  "@deffield ref: Reference",
  0,                                          /* tp_traverse */
  0,                                          /* tp_clear */
  0,                                          /* tp_richcompare */
  offsetof(igraphmodule_VertexSeqObject, weakreflist),  /* tp_weaklistoffset */
  0,                                          /* tp_iter */
  0,                                          /* tp_iternext */
  igraphmodule_VertexSeq_methods,             /* tp_methods */
  0,                                          /* tp_members */
  igraphmodule_VertexSeq_getseters,           /* tp_getset */
  0,                                          /* tp_base */
  0,                                          /* tp_dict */
  0,                                          /* tp_descr_get */
  0,                                          /* tp_descr_set */
  0,                                          /* tp_dictoffset */
  (initproc) igraphmodule_VertexSeq_init,     /* tp_init */
  0,                                          /* tp_alloc */
  (newfunc) igraphmodule_VertexSeq_new,       /* tp_new */
  0,                                          /* tp_free */
  0,                                          /* tp_is_gc */
  0,                                          /* tp_bases */
  0,                                          /* tp_mro */
  0,                                          /* tp_cache  */
  0,                                          /* tp_subclasses */
  0,                                          /* tp_weakreflist */
};

