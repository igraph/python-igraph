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

#include "attributes.h"
#include "common.h"
#include "convert.h"
#include "platform.h"
#include "pyhelpers.h"

static INLINE int PyObject_allowed_in_boolean_attribute(PyObject* o) {
  return o == Py_None || o == Py_False || o == Py_True;
}

static INLINE int PyObject_allowed_in_numeric_attribute(PyObject* o) {
  return o == Py_None || (o != 0 && PyNumber_Check(o));
}

static INLINE int PyObject_allowed_in_string_attribute(PyObject* o) {
  return o == Py_None || (o != 0 && PyBaseString_Check(o));
}

static INLINE void igraphmodule_i_attribute_struct_invalidate_vertex_name_index(
    igraphmodule_i_attribute_struct *attrs
);

int igraphmodule_i_attribute_struct_init(igraphmodule_i_attribute_struct *attrs) {
  int i, j;
  
  for (i = 0; i < 3; i++) {
    attrs->attrs[i] = PyDict_New();
    if (PyErr_Occurred()) {
      for (j = 0; j < i; j++) {
        RC_DEALLOC("dict", attrs->attrs[j]);
        Py_DECREF(attrs->attrs[j]);
        attrs->attrs[j] = NULL;
      }
      return 1;
    }

    RC_ALLOC("dict", attrs->attrs[i]);
  }

  attrs->vertex_name_index = NULL;

  return 0;
}

void igraphmodule_i_attribute_struct_destroy(igraphmodule_i_attribute_struct *attrs) {
  int i;

  for (i = 0; i < 3; i++) {
    if (attrs->attrs[i]) {
      RC_DEALLOC("dict", attrs->attrs[i]);
      Py_DECREF(attrs->attrs[i]);
      attrs->attrs[i] = NULL;
    }
  }

  if (attrs->vertex_name_index) {
    RC_DEALLOC("dict", attrs->vertex_name_index);
    Py_DECREF(attrs->vertex_name_index);
  }
}

int igraphmodule_i_attribute_struct_index_vertex_names(
    igraphmodule_i_attribute_struct *attrs, igraph_bool_t force) {
  Py_ssize_t n = 0;
  PyObject *name_list, *key, *value;
  igraph_bool_t success = false;

  if (attrs->vertex_name_index && !force) {
    return 0;
  }

  if (attrs->vertex_name_index == 0) {
    attrs->vertex_name_index = PyDict_New();
    if (attrs->vertex_name_index == 0) {
      goto cleanup;
    }
  }

  PyDict_Clear(attrs->vertex_name_index);

  name_list = PyDict_GetItemString(attrs->attrs[ATTRHASH_IDX_VERTEX], "name");
  if (name_list == 0) {
    success = true;
    goto cleanup;
  }

  n = PyList_Size(name_list) - 1;
  while (n >= 0) {
    key = PyList_GetItem(name_list, n);      /* we don't own a reference to key */
    if (key == 0) {
      goto cleanup;
    }

    value = PyLong_FromLong(n);              /* we do own a reference to value */
    if (value == 0) {
      goto cleanup;
    }

    if (PyDict_SetItem(attrs->vertex_name_index, key, value)) {
      /* probably unhashable vertex name. If the error is a TypeError, convert
       * it to a more readable error message */
      if (PyErr_Occurred() && PyErr_ExceptionMatches(PyExc_TypeError)) {
        PyErr_Format(
          PyExc_RuntimeError,
          "error while indexing vertex names; did you accidentally try to "
          "use a non-hashable object as a vertex name earlier?"
          " Check the name of vertex %R (%R)", value, key
        );
      }

      /* Drop reference to value because we still own it */
      Py_DECREF(value);

      goto cleanup;
    }

    /* PyDict_SetItem did an INCREF for both the key and a value, therefore we
     * have to drop our reference on value */
    Py_DECREF(value);

    n--;
  }

  success = true;

cleanup:
  if (!success) {
    igraphmodule_i_attribute_struct_invalidate_vertex_name_index(attrs);
  }

  return success ? 0 : 1;
}

static void igraphmodule_i_attribute_struct_invalidate_vertex_name_index(
    igraphmodule_i_attribute_struct *attrs
) {
  if (attrs->vertex_name_index) {
    RC_DEALLOC("dict", attrs->vertex_name_index);
    Py_DECREF(attrs->vertex_name_index);
    attrs->vertex_name_index = NULL;
  }
}

void igraphmodule_invalidate_vertex_name_index(igraph_t *graph) {
  igraphmodule_i_attribute_struct_invalidate_vertex_name_index(ATTR_STRUCT(graph));
}

void igraphmodule_index_vertex_names(igraph_t *graph, igraph_bool_t force) {
  igraphmodule_i_attribute_struct_index_vertex_names(ATTR_STRUCT(graph), force);
}

int igraphmodule_PyObject_matches_attribute_record(PyObject* object, igraph_attribute_record_t* record) {
  if (record == 0) {
    return 0;
  }

  if (PyUnicode_Check(object)) {
    return PyUnicode_IsEqualToASCIIString(object, record->name);
  }

  return 0;
}

int igraphmodule_get_vertex_id_by_name(igraph_t *graph, PyObject* o, igraph_integer_t* vid) {
  igraphmodule_i_attribute_struct* attrs = ATTR_STRUCT(graph);
  PyObject* o_vid = NULL;

  if (graph) {
    attrs = ATTR_STRUCT(graph);
    if (igraphmodule_i_attribute_struct_index_vertex_names(attrs, 0))
      return 1;
    o_vid = PyDict_GetItem(attrs->vertex_name_index, o);
  }

  if (o_vid == NULL) {
    PyErr_Format(PyExc_ValueError, "no such vertex: %R", o);
    return 1;
  }

  if (!PyLong_Check(o_vid)) {
    PyErr_SetString(PyExc_ValueError, "non-numeric vertex ID assigned to vertex name. This is most likely a bug.");
    return 1;
  }
  
  if (igraphmodule_PyObject_to_integer_t(o_vid, vid)) {
    return 1;
  }

  return 0;
}

/**
 * \brief Checks whether the given graph has the given graph attribute.
 *
 * \param  graph  the graph
 * \param  name   the name of the attribute being searched for
 */
igraph_bool_t igraphmodule_has_graph_attribute(const igraph_t *graph, const char* name) {
  PyObject *dict = ATTR_STRUCT_DICT(graph)[ATTRHASH_IDX_GRAPH];
  return name != 0 && dict != 0 && PyDict_GetItemString(dict, name) != 0;
}

/**
 * \brief Checks whether the given graph has the given vertex attribute.
 *
 * \param  graph  the graph
 * \param  name   the name of the attribute being searched for
 */
igraph_bool_t igraphmodule_has_vertex_attribute(const igraph_t *graph, const char* name) {
  PyObject *dict = ATTR_STRUCT_DICT(graph)[ATTRHASH_IDX_VERTEX];
  return name != 0 && dict != 0 && PyDict_GetItemString(dict, name) != 0;
}

/**
 * \brief Checks whether the given graph has the given edge attribute.
 *
 * \param  graph  the graph
 * \param  name   the name of the attribute being searched for
 */
igraph_bool_t igraphmodule_has_edge_attribute(const igraph_t *graph, const char* name) {
  PyObject *dict = ATTR_STRUCT_DICT(graph)[ATTRHASH_IDX_EDGE];
  return name != 0 && dict != 0 && PyDict_GetItemString(dict, name) != 0;
}

/**
 * \brief Creates a new edge attribute and sets the values to None.
 *
 * This returns the actual list that we use to store the edge attributes, so
 * be careful when modifying it - any modification will propagate back to the
 * graph itself. You have been warned.
 *
 * \param  graph  the graph
 * \param  name   the name of the attribute being created
 * \returns  a Python list of the values or \c NULL if the given
 *           attribute exists already (no exception set). The returned
 *           reference is borrowed.
 */
PyObject* igraphmodule_i_create_edge_attribute(const igraph_t* graph,
    const char* name) {
  PyObject *dict = ATTR_STRUCT_DICT(graph)[ATTRHASH_IDX_EDGE];
  PyObject *values;
  Py_ssize_t i, n;

  if (dict == NULL) {
    dict = ATTR_STRUCT_DICT(graph)[ATTRHASH_IDX_EDGE] = PyDict_New();
    if (dict == NULL) {
      return NULL;
    }
  }

  if (PyDict_GetItemString(dict, name))
    return 0;

  n = igraph_ecount(graph);
  values = PyList_New(n);
  if (values == 0)
    return 0;

  for (i = 0; i < n; i++) {
    Py_INCREF(Py_None);
    if (PyList_SetItem(values, i, Py_None)) {  /* reference stolen */
      Py_DECREF(values);
      Py_DECREF(Py_None);
      return 0;
    }
  }

  if (PyDict_SetItemString(dict, name, values)) {
    Py_DECREF(values);
    return 0;
  }

  Py_DECREF(values);
  return values;
}

/**
 * \brief Returns the values of the given edge attribute for all edges in the
 *        given graph.
 *
 * This returns the actual list that we use to store the edge attributes, so
 * be careful when modifying it - any modification will propagate back to the
 * graph itself. You have been warned.
 *
 * \param  graph  the graph
 * \param  name   the name of the attribute being searched for
 * \returns  a Python list or \c NULL if there is no such attribute
 *           (no exception set). The returned reference is borrowed.
 */
PyObject* igraphmodule_get_edge_attribute_values(const igraph_t* graph,
    const char* name) {
  PyObject *dict = ATTR_STRUCT_DICT(graph)[ATTRHASH_IDX_EDGE];
  if (dict == 0)
    return 0;
  return PyDict_GetItemString(dict, name);
}

/**
 * \brief Returns the values of the given edge attribute for all edges in the
 *        given graph, optionally creating it if it does not exist.
 *
 * This returns the actual list that we use to store the edge attributes, so
 * be careful when modifying it - any modification will propagate back to the
 * graph itself. You have been warned.
 *
 * \param  graph  the graph
 * \param  name   the name of the attribute being searched for
 * \returns  a Python list (borrowed reference)
 */
PyObject* igraphmodule_create_or_get_edge_attribute_values(const igraph_t* graph,
    const char* name) {
  PyObject *dict = ATTR_STRUCT_DICT(graph)[ATTRHASH_IDX_EDGE], *result;
  if (dict == NULL) {
    return 0;
  }

  result = PyDict_GetItemString(dict, name);
  if (result != NULL) {
    return result;
  }
  
  return igraphmodule_i_create_edge_attribute(graph, name);
}

/* Attribute handlers for the Python interface */

/* Initialization */ 
static igraph_error_t igraphmodule_i_attribute_init(igraph_t *graph, igraph_vector_ptr_t *attr) {
  igraphmodule_i_attribute_struct* attrs;
  igraph_integer_t i, n;
  
  attrs = (igraphmodule_i_attribute_struct*)calloc(1, sizeof(igraphmodule_i_attribute_struct));
  if (!attrs) {
    IGRAPH_ERROR("not enough memory to allocate attribute hashes", IGRAPH_ENOMEM);
  }
  IGRAPH_FINALLY(free, attrs);

  if (igraphmodule_i_attribute_struct_init(attrs)) {
    PyErr_PrintEx(0);
    IGRAPH_ERROR("not enough memory to allocate attribute hashes", IGRAPH_ENOMEM);
  }
  IGRAPH_FINALLY(igraphmodule_i_attribute_struct_destroy, attrs);

  /* See if we have graph attributes */
  if (attr) {
    PyObject *dict = attrs->attrs[0], *value;
    const char *s;
  
    n = igraph_vector_ptr_size(attr);
    for (i = 0; i < n; i++) {
      igraph_attribute_record_t *attr_rec;
      attr_rec = VECTOR(*attr)[i];

      switch (attr_rec->type) {
      case IGRAPH_ATTRIBUTE_NUMERIC:
        value = PyFloat_FromDouble((double)VECTOR(*(igraph_vector_t*)attr_rec->value)[0]);
        if (!value) {
          PyErr_PrintEx(0);
        }
        break;
      case IGRAPH_ATTRIBUTE_STRING:
        s = igraph_strvector_get((igraph_strvector_t*)attr_rec->value, 0);
        value = PyUnicode_FromString(s ? s : "");
        if (!value) {
          PyErr_PrintEx(0);
        }
        break;
      case IGRAPH_ATTRIBUTE_BOOLEAN:
        value = VECTOR(*(igraph_vector_bool_t*)attr_rec->value)[0] ? Py_True : Py_False;
        Py_INCREF(value);
        break;
      default:
        IGRAPH_WARNING("unsupported attribute type (not string, numeric or Boolean)");
        value = NULL;
        break;
      }

      if (value) {
        if (PyDict_SetItemString(dict, attr_rec->name, value)) {
          Py_DECREF(value);
          value = NULL;  /* set value to NULL to indicate an error */
        } else {
          Py_DECREF(value);
        }
      }
      
      if (!value) {
        /* there was an error above, bail out */
        IGRAPH_ERROR("failed to add attributes to graph attribute hash", IGRAPH_FAILURE);
      }
    }
  }

  graph->attr = (void*)attrs;
  IGRAPH_FINALLY_CLEAN(2);

  return IGRAPH_SUCCESS;
}

/* Destruction */
static void igraphmodule_i_attribute_destroy(igraph_t *graph) {
  igraphmodule_i_attribute_struct* attrs;
 
  /* printf("Destroying attribute table\n"); */
  if (graph->attr) {
    attrs = (igraphmodule_i_attribute_struct*)graph->attr;
    graph->attr = NULL;
    igraphmodule_i_attribute_struct_destroy(attrs);
    free(attrs);
  }
}

/* Copying */
static igraph_error_t igraphmodule_i_attribute_copy(igraph_t *to, const igraph_t *from,
  igraph_bool_t ga, igraph_bool_t va, igraph_bool_t ea) {
  igraphmodule_i_attribute_struct *fromattrs, *toattrs;
  PyObject *key, *value, *newval, *o=NULL;
  igraph_bool_t copy_attrs[3] = { ga, va, ea };
  int i;
  Py_ssize_t j, pos = 0, list_len;
 
  if (from->attr) {
    fromattrs = ATTR_STRUCT(from);

    toattrs = (igraphmodule_i_attribute_struct*) calloc(1, sizeof(igraphmodule_i_attribute_struct));
    if (!toattrs) {
      IGRAPH_ERROR("not enough memory to allocate attribute hashes", IGRAPH_ENOMEM);
    }
    IGRAPH_FINALLY(free, toattrs);

    if (igraphmodule_i_attribute_struct_init(toattrs)) {
      PyErr_PrintEx(0);
      IGRAPH_ERROR("not enough memory to allocate attribute hashes", IGRAPH_ENOMEM);
    }
    IGRAPH_FINALLY(igraphmodule_i_attribute_struct_destroy, toattrs);

    for (i = 0; i < 3; i++) {
      if (!copy_attrs[i]) {
        continue;
      }

      if (!PyDict_Check(fromattrs->attrs[i])) {
        IGRAPH_ERRORF("expected dict in attribute hash at index %d", IGRAPH_EINVAL, i);
      }

      /* graph attributes are easy to copy because the dict is a key-value map */
      if (i == ATTRHASH_IDX_GRAPH) {
        Py_XDECREF(toattrs->attrs[i]); /* we already had a pre-constructed dict there */
        toattrs->attrs[i] = PyDict_Copy(fromattrs->attrs[i]);
        if (!toattrs->attrs[i]) {
          PyErr_PrintEx(0);
          IGRAPH_ERROR("cannot copy attribute hashes", IGRAPH_FAILURE);
        }
      } else {
        /* vertex and edge attributes have to be copied in a way that values
         * are also copied */
        pos = 0;
        while (PyDict_Next(fromattrs->attrs[i], &pos, &key, &value)) {
          /* value is only borrowed, so copy it */
          if (!PyList_Check(value)) {
            IGRAPH_ERRORF("expected list in attribute hash at index %d", IGRAPH_EINVAL, i);
          }

          list_len = PyList_Size(value);
          newval = PyList_New(list_len);
          for (j = 0; j < list_len; j++) {
            o = PyList_GetItem(value, j);
            Py_INCREF(o);
            PyList_SetItem(newval, j, o);
          }

          if (!newval) {
            PyErr_PrintEx(0);
            IGRAPH_ERROR("cannot copy attribute hashes", IGRAPH_FAILURE);
          }

          if (PyDict_SetItem(toattrs->attrs[i], key, newval)) {
            PyErr_PrintEx(0);
            Py_DECREF(newval);
            IGRAPH_ERROR("cannot copy attribute hashes", IGRAPH_FAILURE);
          }

          Py_DECREF(newval); /* compensate for PyDict_SetItem */
        }
      }
    }

    to->attr = toattrs;
    IGRAPH_FINALLY_CLEAN(2);
  }

  return IGRAPH_SUCCESS;
}

/* Adding vertices */
static igraph_error_t igraphmodule_i_attribute_add_vertices(igraph_t *graph, igraph_integer_t nv, igraph_vector_ptr_t *attr) {
  /* Extend the end of every value in the vertex hash with nv pieces of None */
  PyObject *key, *value, *dict;
  igraph_integer_t i, j, k, num_attr_entries;
  igraph_attribute_record_t *attr_rec;
  igraph_vector_bool_t added_attrs;
  Py_ssize_t pos = 0;

  if (!graph->attr) {
    return IGRAPH_SUCCESS;
  }

  if (nv < 0) {
    return IGRAPH_SUCCESS;
  }

  num_attr_entries = attr ? igraph_vector_ptr_size(attr) : 0;
  IGRAPH_VECTOR_BOOL_INIT_FINALLY(&added_attrs, num_attr_entries);

  dict = ATTR_STRUCT_DICT(graph)[ATTRHASH_IDX_VERTEX];
  if (!PyDict_Check(dict)) {
    IGRAPH_ERROR("vertex attribute hash type mismatch", IGRAPH_EINVAL);
  }

  while (PyDict_Next(dict, &pos, &key, &value)) {
    if (!PyList_Check(value)) {
      IGRAPH_ERROR("vertex attribute hash member is not a list", IGRAPH_EINVAL);
    }

    /* Check if we have specific values for the given attribute */
    attr_rec = NULL;
    for (i = 0; i < num_attr_entries; i++) {
      attr_rec = VECTOR(*attr)[i];
      if (igraphmodule_PyObject_matches_attribute_record(key, attr_rec)) {
        VECTOR(added_attrs)[i] = 1;
        break;
      }
      attr_rec = NULL;
    }

    /* If we have specific values for the given attribute, attr_rec contains
     * the appropriate vector. If not, it is null. */
    if (attr_rec) {
      for (i = 0; i < nv; i++) {
        const char *s;
        PyObject *o = NULL;

        switch (attr_rec->type) {
        case IGRAPH_ATTRIBUTE_NUMERIC:
          o = PyFloat_FromDouble((double)VECTOR(*(igraph_vector_t*)attr_rec->value)[i]);
          break;
        case IGRAPH_ATTRIBUTE_STRING:
          s = igraph_strvector_get((igraph_strvector_t*)attr_rec->value, i);
          o = PyUnicode_FromString(s);
          break;
        case IGRAPH_ATTRIBUTE_BOOLEAN:
          o = VECTOR(*(igraph_vector_bool_t*)attr_rec->value)[i] ? Py_True : Py_False;
          Py_INCREF(o);
          break;
        default:
          IGRAPH_WARNING("unsupported attribute type (not string, numeric or Boolean)");
          o = Py_None;
          Py_INCREF(o);
          break;
        }

        if (o) {
          if (PyList_Append(value, o)) {
            Py_DECREF(o); /* append failed */
            o = NULL; /* indicate error */
          } else {
            Py_DECREF(o); /* drop reference, the list has it now */
          }
        }

        if (!o) {
          PyErr_PrintEx(0);
          IGRAPH_ERROR("can't extend a vertex attribute hash member", IGRAPH_FAILURE);
        }
      }

      /* Invalidate the vertex name index if needed */
      if (!strcmp(attr_rec->name, "name")) {
        igraphmodule_i_attribute_struct_invalidate_vertex_name_index(ATTR_STRUCT(graph));
      }
    } else {
      for (i = 0; i < nv; i++) {
        if (PyList_Append(value, Py_None)) {
          PyErr_PrintEx(0);
          IGRAPH_ERROR("can't extend a vertex attribute hash member", IGRAPH_FAILURE);
        }
      }
    }
  }

  /* Okay, now we added the new attribute values for the already existing
   * attribute keys. Let's see if we have something left */
  j = igraph_vcount(graph) - nv;

  /* j contains the number of vertices EXCLUDING the new ones! */
  for (k = 0; k < num_attr_entries; k++) {
    if (VECTOR(added_attrs)[k]) {
      continue;
    }

    attr_rec = (igraph_attribute_record_t*)VECTOR(*attr)[k];

    value = PyList_New(j + nv);
    if (!value) {
      IGRAPH_ERROR("can't add attributes", IGRAPH_ENOMEM);
    }

    for (i = 0; i < j; i++) {
      Py_INCREF(Py_None);
      PyList_SetItem(value, i, Py_None);
    }

    for (i = 0; i < nv; i++) {
      const char *s;
      PyObject *o = NULL;
      switch (attr_rec->type) {
      case IGRAPH_ATTRIBUTE_NUMERIC:
        o = PyFloat_FromDouble((double)VECTOR(*(igraph_vector_t*)attr_rec->value)[i]);
        break;
      case IGRAPH_ATTRIBUTE_STRING:
        s = igraph_strvector_get((igraph_strvector_t*)attr_rec->value, i);
        o = PyUnicode_FromString(s);
        break;
      case IGRAPH_ATTRIBUTE_BOOLEAN:
        o = VECTOR(*(igraph_vector_bool_t*)attr_rec->value)[i] ? Py_True : Py_False;
        Py_INCREF(o);
        break;
      default:
        IGRAPH_WARNING("unsupported attribute type (not string, numeric or Boolean)");
        o = Py_None;
        Py_INCREF(o);
        break;
      }

      if (o) {
        if (PyList_SetItem(value, i + j, o)) {  
          Py_DECREF(o); /* append failed */
          o = NULL; /* indicate error */
        } else {
          /* reference stolen by the list */
        }
      }

      if (!o) {
        PyErr_PrintEx(0);
        IGRAPH_ERROR("can't extend a vertex attribute hash member", IGRAPH_FAILURE);
      }
    }

    /* Invalidate the vertex name index if needed */
    if (!strcmp(attr_rec->name, "name")) {
      igraphmodule_i_attribute_struct_invalidate_vertex_name_index(ATTR_STRUCT(graph));
    }

    PyDict_SetItemString(dict, attr_rec->name, value);
    Py_DECREF(value);   /* compensate for PyDict_SetItemString */
  }

  igraph_vector_bool_destroy(&added_attrs);
  IGRAPH_FINALLY_CLEAN(1);

  return IGRAPH_SUCCESS;
}

/* Permuting vertices */
static igraph_error_t igraphmodule_i_attribute_permute_vertices(const igraph_t *graph,
    igraph_t *newgraph, const igraph_vector_int_t *idx) {
  igraph_integer_t i, n;
  PyObject *key, *value, *dict, *newdict, *newlist, *o;
  Py_ssize_t pos = 0;
  
  dict = ATTR_STRUCT_DICT(graph)[ATTRHASH_IDX_VERTEX];
  if (!PyDict_Check(dict)) {
    IGRAPH_ERROR("vertex attribute hash type mismatch", IGRAPH_EINVAL);
  }

  newdict = PyDict_New();
  if (!newdict) {
    IGRAPH_ERROR("cannot allocate new dict for vertex permutation", IGRAPH_ENOMEM);
  }

  n = igraph_vector_int_size(idx);
  pos = 0;

  while (PyDict_Next(dict, &pos, &key, &value)) {
    newlist = PyList_New(n);
    for (i = 0; i < n; i++) {
      o = PyList_GetItem(value, VECTOR(*idx)[i]);
      if (!o) {
        PyErr_PrintEx(0);
        Py_DECREF(newlist);
        Py_DECREF(newdict);
        PyErr_Clear();
        IGRAPH_ERROR("", IGRAPH_FAILURE);
      }
      Py_INCREF(o);
      if (PyList_SetItem(newlist, i, o)) {
        PyErr_PrintEx(0);
        Py_DECREF(o);
        Py_DECREF(newlist);
        Py_DECREF(newdict);
        IGRAPH_ERROR("", IGRAPH_FAILURE);
      }
    }
    PyDict_SetItem(newdict, key, newlist);
    Py_DECREF(newlist);
  }

  dict = ATTR_STRUCT_DICT(newgraph)[ATTRHASH_IDX_VERTEX];
  ATTR_STRUCT_DICT(newgraph)[ATTRHASH_IDX_VERTEX]=newdict;
  Py_DECREF(dict);

  /* Invalidate the vertex name index */
  igraphmodule_i_attribute_struct_invalidate_vertex_name_index(ATTR_STRUCT(newgraph));

  return IGRAPH_SUCCESS;
}

/* Adding edges */
static igraph_error_t igraphmodule_i_attribute_add_edges(igraph_t *graph, const igraph_vector_int_t *edges, igraph_vector_ptr_t *attr) {
  /* Extend the end of every value in the edge hash with ne pieces of None */
  PyObject *key, *value, *dict;
  Py_ssize_t pos = 0;
  igraph_integer_t i, j, k, ne, num_attr_entries;
  igraph_vector_bool_t added_attrs;
  igraph_attribute_record_t *attr_rec;

  if (!graph->attr) {
    return IGRAPH_SUCCESS;
  }

  ne = igraph_vector_int_size(edges) / 2;
  if (ne < 0) {
    return IGRAPH_SUCCESS;
  }

  num_attr_entries = attr ? igraph_vector_ptr_size(attr) : 0;
  IGRAPH_VECTOR_BOOL_INIT_FINALLY(&added_attrs, num_attr_entries);

  dict = ATTR_STRUCT_DICT(graph)[ATTRHASH_IDX_EDGE];
  if (!PyDict_Check(dict)) {
    IGRAPH_ERROR("edge attribute hash type mismatch", IGRAPH_EINVAL);
  }

  while (PyDict_Next(dict, &pos, &key, &value)) {
    if (!PyList_Check(value)) {
      IGRAPH_ERROR("edge attribute hash member is not a list", IGRAPH_EINVAL);
    }

    /* Check if we have specific values for the given attribute */
    attr_rec = NULL;
    for (i = 0; i < num_attr_entries; i++) {
      attr_rec = VECTOR(*attr)[i];
      if (igraphmodule_PyObject_matches_attribute_record(key, attr_rec)) {
        VECTOR(added_attrs)[i] = 1;
        break;
      }
      attr_rec = NULL;
    }

    /* If we have specific values for the given attribute, attr_rec contains
     * the appropriate vector. If not, it is null. */
    if (attr_rec) {
      for (i = 0; i < ne; i++) {
        const char *s;
        PyObject *o;
        switch (attr_rec->type) {
        case IGRAPH_ATTRIBUTE_NUMERIC:
          o = PyFloat_FromDouble((double)VECTOR(*(igraph_vector_t*)attr_rec->value)[i]);
          break;
        case IGRAPH_ATTRIBUTE_STRING:
          s = igraph_strvector_get((igraph_strvector_t*)attr_rec->value, i);
          o = PyUnicode_FromString(s);
          break;
        case IGRAPH_ATTRIBUTE_BOOLEAN:
          o = VECTOR(*(igraph_vector_bool_t*)attr_rec->value)[i] ? Py_True : Py_False;
          Py_INCREF(o);
          break;
        default:
          IGRAPH_WARNING("unsupported attribute type (not string, numeric or Boolean)");
          o = Py_None;
          Py_INCREF(o);
          break;
        }

        if (o) {
          if (PyList_Append(value, o)) {
            Py_DECREF(o); /* append failed */
            o = NULL; /* indicate error */
          } else {
            Py_DECREF(o); /* drop reference, the list has it now */
          }
        }

        if (!o) {
          PyErr_PrintEx(0);
          IGRAPH_ERROR("can't extend an edge attribute hash member", IGRAPH_FAILURE);
        }
      }
    } else {
      for (i = 0; i < ne; i++) {
        if (PyList_Append(value, Py_None)) {
          PyErr_PrintEx(0);
          IGRAPH_ERROR("can't extend an edge attribute hash member", IGRAPH_FAILURE);
        }
      }
    }
  }
  
  /* Okay, now we added the new attribute values for the already existing
   * attribute keys. Let's see if we have something left */
  j = igraph_ecount(graph) - ne;
  /* j contains the number of edges EXCLUDING the new ones! */
  for (k = 0; k < num_attr_entries; k++) {
    if (VECTOR(added_attrs)[k]) {
      continue;
    }
    attr_rec=(igraph_attribute_record_t*)VECTOR(*attr)[k];

    value = PyList_New(j + ne);
    if (!value) {
      IGRAPH_ERROR("can't add attributes", IGRAPH_ENOMEM);
    }

    for (i = 0; i < j; i++) {
      Py_INCREF(Py_None);
      PyList_SetItem(value, i, Py_None);
    }

    for (i = 0; i < ne; i++) {
      const char *s;
      PyObject *o;
      switch (attr_rec->type) {
      case IGRAPH_ATTRIBUTE_NUMERIC:
        o = PyFloat_FromDouble((double)VECTOR(*(igraph_vector_t*)attr_rec->value)[i]);
        break;
      case IGRAPH_ATTRIBUTE_STRING:
        s = igraph_strvector_get((igraph_strvector_t*)attr_rec->value, i);
        o = PyUnicode_FromString(s);
        break;
      case IGRAPH_ATTRIBUTE_BOOLEAN:
        o = VECTOR(*(igraph_vector_bool_t*)attr_rec->value)[i] ? Py_True : Py_False;
        Py_INCREF(o);
        break;
      default:
        IGRAPH_WARNING("unsupported attribute type (not string, numeric or Boolean)");
        o = Py_None;
        Py_INCREF(o);
        break;
      }

      if (o) {
        if (PyList_SetItem(value, i + j, o)) {  
          Py_DECREF(o); /* append failed */
          o = NULL; /* indicate error */
        } else {
          /* reference stolen by the list */
        }
      }

      if (!o) {
        PyErr_PrintEx(0);
        IGRAPH_ERROR("can't extend a vertex attribute hash member", IGRAPH_FAILURE);
      }
    }

    PyDict_SetItemString(dict, attr_rec->name, value);
    Py_DECREF(value);   /* compensate for PyDict_SetItemString */
  }

  igraph_vector_bool_destroy(&added_attrs);
  IGRAPH_FINALLY_CLEAN(1);

  return IGRAPH_SUCCESS;
}

/* Permuting edges */
static igraph_error_t igraphmodule_i_attribute_permute_edges(const igraph_t *graph,
    igraph_t *newgraph, const igraph_vector_int_t *idx) { 
  igraph_integer_t i, n;
  PyObject *key, *value, *dict, *newdict, *newlist, *o;
  Py_ssize_t pos=0;

  dict = ATTR_STRUCT_DICT(graph)[ATTRHASH_IDX_EDGE];
  if (!PyDict_Check(dict)) {
    IGRAPH_ERROR("edge attribute hash type mismatch", IGRAPH_EINVAL);
  }

  newdict = PyDict_New();
  if (!newdict) {
    IGRAPH_ERROR("cannot allocate new dict for edge permutation", IGRAPH_ENOMEM);
  }

  n = igraph_vector_int_size(idx);
  pos = 0;

  while (PyDict_Next(dict, &pos, &key, &value)) {
    newlist = PyList_New(n);
    for (i = 0; i < n; i++) {
      o = PyList_GetItem(value, VECTOR(*idx)[i]);
      if (!o) {
        PyErr_PrintEx(0);
        Py_DECREF(newlist);
        Py_DECREF(newdict);
        PyErr_Clear();
        IGRAPH_ERROR("", IGRAPH_FAILURE);
      }
      Py_INCREF(o);
      if (PyList_SetItem(newlist, i, o)) {
        PyErr_PrintEx(0);
        Py_DECREF(o);
        Py_DECREF(newlist);
        Py_DECREF(newdict);
        IGRAPH_ERROR("", IGRAPH_FAILURE);
      }
    }
    PyDict_SetItem(newdict, key, newlist);
    Py_DECREF(newlist);
  }

  dict = ATTR_STRUCT_DICT(newgraph)[ATTRHASH_IDX_EDGE];
  ATTR_STRUCT_DICT(newgraph)[ATTRHASH_IDX_EDGE]=newdict;
  Py_DECREF(dict);

  return IGRAPH_SUCCESS;
}

/* Auxiliary function for combining vertices/edges. Given a merge list
 * (which specifies the vertex/edge IDs that were merged), the source
 * attribute values and a Python callable to be called for every merge,
 * returns a new list with the new attribute values. Each new attribute
 * is derived by calling func with the old attributes of the set of
 * merged vertices/edges as the first argument.
 */
static PyObject* igraphmodule_i_ac_func(PyObject* values,
    const igraph_vector_int_list_t *merges, PyObject* func) {
  igraph_integer_t i, len = igraph_vector_int_list_size(merges);
  PyObject *res, *list, *item;

  res = PyList_New(len);
  
  for (i = 0; i < len; i++) {
    igraph_vector_int_t *v = igraph_vector_int_list_get_ptr(merges, i);
    igraph_integer_t j, n = igraph_vector_int_size(v);

    list = PyList_New(n);
    for (j = 0; j < n; j++) {
      item = PyList_GetItem(values, (Py_ssize_t)VECTOR(*v)[j]);
      if (item == 0) {
        Py_DECREF(list);
        Py_DECREF(res);
        return 0;
      }

      Py_INCREF(item);

      if (PyList_SetItem(list, j, item)) {   /* reference to item stolen */
        Py_DECREF(item);
        Py_DECREF(res);
        return 0;
      }
    }
    item = PyObject_CallFunctionObjArgs(func, list, 0);
    Py_DECREF(list);

    if (item == 0) {
      Py_DECREF(res);
      return 0;
    }

    if (PyList_SetItem(res, i, item)) {   /* reference to item stolen */
      Py_DECREF(item);
      Py_DECREF(res);
      return 0;
    }
  }

  return res;
}

/* Auxiliary function for combining vertices/edges. Given a merge list
 * (which specifies the vertex/edge IDs that were merged, the source
 * attribute values and a name of a Python builtin function,
 * returns a new list with the new attribute values. Each new attribute
 * is derived by calling the given builtin function with the old
 * attributes of the set of merged vertices/edges as the first argument.
 */
static PyObject* igraphmodule_i_ac_builtin_func(PyObject* values,
    const igraph_vector_int_list_t *merges, const char* func_name) {
  static PyObject* builtin_module_dict = 0;
  PyObject* func = 0;

  if (builtin_module_dict == 0) {
    PyObject* builtin_module = PyImport_ImportModule("builtins");
    if (builtin_module == 0)
      return 0;
    builtin_module_dict = PyModule_GetDict(builtin_module);
    Py_DECREF(builtin_module);
    if (builtin_module_dict == 0)
      return 0;
  }

  func = PyDict_GetItemString(builtin_module_dict, func_name);
  if (func == 0) {
    PyErr_Format(PyExc_NameError, "no such builtin function; %s", func_name);
    return 0;
  }

  return igraphmodule_i_ac_func(values, merges, func);
}

/* Auxiliary function for combining vertices/edges. Given a merge list
 * (which specifies the vertex/edge IDs that were merged and the source
 * attribute values, returns a new list with the new attribute values.
 * Each new attribute is derived from the sum of the attributes of
 * the merged vertices/edges.
 */
static PyObject* igraphmodule_i_ac_sum(PyObject* values,
    const igraph_vector_int_list_t *merges) {
  igraph_integer_t i, len = igraph_vector_int_list_size(merges);
  PyObject *res, *item;

  res = PyList_New(len);
  for (i = 0; i < len; i++) {
    igraph_vector_int_t *v = igraph_vector_int_list_get_ptr(merges, i);
    igraph_real_t num = 0.0, sum = 0.0;
    igraph_integer_t j, n = igraph_vector_int_size(v);

    for (j = 0; j < n; j++) {
      item = PyList_GetItem(values, (Py_ssize_t)VECTOR(*v)[j]);
      if (item == 0) {
        Py_DECREF(res);
        return 0;
      }

      if (igraphmodule_PyObject_to_real_t(item, &num)) {
        PyErr_SetString(PyExc_TypeError, "product can only be invoked on numeric attributes");
        Py_DECREF(res);
        return 0;
      }
      sum += num;
    }

    item = PyFloat_FromDouble(sum);
    if (PyList_SetItem(res, i, item)) {   /* reference to item stolen */
      Py_DECREF(item);
      Py_DECREF(res);
      return 0;
    }
  }

  return res;
}

/* Auxiliary function for combining vertices/edges. Given a merge list
 * (which specifies the vertex/edge IDs that were merged and the source
 * attribute values, returns a new list with the new attribute values.
 * Each new attribute is derived from the product of the attributes of
 * the merged vertices/edges.
 */
static PyObject* igraphmodule_i_ac_prod(PyObject* values,
    const igraph_vector_int_list_t *merges) {
  igraph_integer_t i, len = igraph_vector_int_list_size(merges);
  PyObject *res, *item;

  res = PyList_New(len);
  for (i = 0; i < len; i++) {
    igraph_vector_int_t *v = igraph_vector_int_list_get_ptr(merges, i);
    igraph_real_t num = 1.0, prod = 1.0;
    igraph_integer_t j, n = igraph_vector_int_size(v);

    for (j = 0; j < n; j++) {
      item = PyList_GetItem(values, (Py_ssize_t)VECTOR(*v)[j]);
      if (item == 0) {
        Py_DECREF(res);
        return 0;
      }

      if (igraphmodule_PyObject_to_real_t(item, &num)) {
        PyErr_SetString(PyExc_TypeError, "product can only be invoked on numeric attributes");
        Py_DECREF(res);
        return 0;
      }
      prod *= num;
    }

    /* reference to new float stolen */
    item = PyFloat_FromDouble((double)prod);
    if (PyList_SetItem(res, i, item)) {   /* reference to item stolen */
      Py_DECREF(item);
      Py_DECREF(res);
      return 0;
    }
  }

  return res;
}

/* Auxiliary function for combining vertices/edges. Given a merge list
 * (which specifies the vertex/edge IDs that were merged and the source
 * attribute values, returns a new list with the new attribute values.
 * Each new attribute is derived from the first entry of the set of merged
 * vertices/edges.
 */
static PyObject* igraphmodule_i_ac_first(PyObject* values,
    const igraph_vector_int_list_t *merges) {
  igraph_integer_t i, len = igraph_vector_int_list_size(merges);
  PyObject *res, *item;

  res = PyList_New(len);
  for (i = 0; i < len; i++) {
    igraph_vector_int_t *v = igraph_vector_int_list_get_ptr(merges, i);
    igraph_integer_t n = igraph_vector_int_size(v);

    item = n > 0 ? PyList_GetItem(values, (Py_ssize_t)VECTOR(*v)[0]) : Py_None;
    if (item == 0) {
      Py_DECREF(res);
      return 0;
    }
    
    Py_INCREF(item);
    if (PyList_SetItem(res, i, item)) {  /* reference to item stolen */
      Py_DECREF(item);
      Py_DECREF(res);
      return 0;
    }
  }

  return res;
}

/* Auxiliary function for combining vertices/edges. Given a merge list
 * (which specifies the vertex/edge IDs that were merged and the source
 * attribute values, returns a new list with the new attribute values.
 * Each new attribute is derived from a randomly selected entry of the set of
 * merged vertices/edges.
 */
static PyObject* igraphmodule_i_ac_random(PyObject* values,
    const igraph_vector_int_list_t *merges) {
  igraph_integer_t i, len = igraph_vector_int_list_size(merges);
  PyObject *res, *item, *num;
  PyObject *random_module = PyImport_ImportModule("random");
  PyObject *random_func;

  if (random_module == 0)
    return 0;

  random_func = PyObject_GetAttrString(random_module, "random");
  Py_DECREF(random_module);

  if (random_func == 0)
    return 0;

  res = PyList_New(len);
  for (i = 0; i < len; i++) {
    igraph_vector_int_t *v = igraph_vector_int_list_get_ptr(merges, i);
    igraph_integer_t n = igraph_vector_int_size(v);

    if (n > 0) {
      num = PyObject_CallObject(random_func, 0);
      if (num == 0) {
        Py_DECREF(random_func);
        Py_DECREF(res);
        return 0;
      }

      item = PyList_GetItem(
        values, VECTOR(*v)[(igraph_integer_t)(n * PyFloat_AsDouble(num))]
      );
      if (item == 0) {
        Py_DECREF(random_func);
        Py_DECREF(res);
        return 0;
      }

      Py_DECREF(num);
    } else {
      item = Py_None;
    }

    Py_INCREF(item);
    if (PyList_SetItem(res, i, item)) {  /* reference to item stolen */
      Py_DECREF(item);
      Py_DECREF(random_func);
      Py_DECREF(res);
      return 0;
    }
  }

  Py_DECREF(random_func);

  return res;
}

/* Auxiliary function for combining vertices/edges. Given a merge list
 * (which specifies the vertex/edge IDs that were merged and the source
 * attribute values, returns a new list with the new attribute values.
 * Each new attribute is derived from the last entry of the set of merged
 * vertices/edges.
 */
static PyObject* igraphmodule_i_ac_last(PyObject* values,
    const igraph_vector_int_list_t *merges) {
  igraph_integer_t i, len = igraph_vector_int_list_size(merges);
  PyObject *res, *item;

  res = PyList_New(len);
  for (i = 0; i < len; i++) {
    igraph_vector_int_t *v = igraph_vector_int_list_get_ptr(merges, i);
    igraph_integer_t n = igraph_vector_int_size(v);

    item = (n > 0) ? PyList_GetItem(values, (Py_ssize_t)VECTOR(*v)[n-1]) : Py_None;
    if (item == 0) {
      Py_DECREF(res);
      return 0;
    }

    Py_INCREF(item);

    if (PyList_SetItem(res, i, item)) {   /* reference to item stolen */
      Py_DECREF(item);
      Py_DECREF(res);
      return 0;
    }
  }

  return res;
}

/* Auxiliary function for combining vertices/edges. Given a merge list
 * (which specifies the vertex/edge IDs that were merged and the source
 * attribute values, returns a new list with the new attribute values.
 * Each new attribute is derived from the mean of the attributes of
 * the merged vertices/edges.
 */
static PyObject* igraphmodule_i_ac_mean(PyObject* values,
    const igraph_vector_int_list_t *merges) {
  igraph_integer_t i, len = igraph_vector_int_list_size(merges);
  PyObject *res, *item;

  res = PyList_New(len);
  for (i = 0; i < len; i++) {
    igraph_vector_int_t *v = igraph_vector_int_list_get_ptr(merges, i);
    igraph_real_t num = 0.0, mean = 0.0;
    igraph_integer_t j, n = igraph_vector_int_size(v);

    for (j = 0; j < n; ) {
      item = PyList_GetItem(values, (Py_ssize_t)VECTOR(*v)[j]);
      if (item == 0) {
        Py_DECREF(res);
        return 0;
      }
      
      if (igraphmodule_PyObject_to_real_t(item, &num)) {
        PyErr_SetString(PyExc_TypeError, "mean can only be invoked on numeric attributes");
        Py_DECREF(res);
        return 0;
      }
      j++;
      num -= mean;
      mean += num / j;
    }

    /* reference to new float stolen */
    item = PyFloat_FromDouble((double)mean);
    if (PyList_SetItem(res, i, item)) {   /* reference to item stolen */
      Py_DECREF(item);
      Py_DECREF(res);
      return 0;
    }
  }

  return res;
}

/* Auxiliary function for combining vertices/edges. Given a merge list
 * (which specifies the vertex/edge IDs that were merged and the source
 * attribute values, returns a new list with the new attribute values.
 * Each new attribute is derived from the median of the attributes of
 * the merged vertices/edges.
 */
static PyObject* igraphmodule_i_ac_median(PyObject* values,
    const igraph_vector_int_list_t *merges) {
  igraph_integer_t i, len = igraph_vector_int_list_size(merges);
  PyObject *res, *list, *item;

  res = PyList_New(len);
  for (i = 0; i < len; i++) {
    igraph_vector_int_t *v = igraph_vector_int_list_get_ptr(merges, i);
    igraph_integer_t j, n = igraph_vector_int_size(v);
    list = PyList_New(n);
    for (j = 0; j < n; j++) {
      item = PyList_GetItem(values, (Py_ssize_t)VECTOR(*v)[j]);
      if (item == 0) {
        Py_DECREF(res);
        return 0;
      }

      Py_INCREF(item);
      if (PyList_SetItem(list, j, item)) {  /* reference to item stolen */
        Py_DECREF(item);
        Py_DECREF(list);
        Py_DECREF(res);
        return 0;
      }
    }

    /* sort the list */
    if (PyList_Sort(list)) {
      Py_DECREF(list);
      Py_DECREF(res);
      return 0;
    }

    if (n == 0) {
      item = Py_None;
      Py_INCREF(item);
    } else if (n % 2 == 1) {
      item = PyList_GetItem(list, n / 2);
      if (item == 0) {
        Py_DECREF(list);
        Py_DECREF(res);
        return 0;
      }

      Py_INCREF(item);
    } else {
      igraph_real_t num1, num2;
      item = PyList_GetItem(list, n / 2 - 1);
      if (item == 0) {
        Py_DECREF(list);
        Py_DECREF(res);
        return 0;
      }

      if (igraphmodule_PyObject_to_real_t(item, &num1)) {
        Py_DECREF(list);
        Py_DECREF(res);
        return 0;
      }

      item = PyList_GetItem(list, n / 2);
      if (item == 0) {
        Py_DECREF(list);
        Py_DECREF(res);
        return 0;
      }

      if (igraphmodule_PyObject_to_real_t(item, &num2)) {
        Py_DECREF(list);
        Py_DECREF(res);
        return 0;
      }

      item = PyFloat_FromDouble((num1 + num2) / 2);
    }

    /* reference to item stolen */
    if (PyList_SetItem(res, i, item)) {
      Py_DECREF(item);
      Py_DECREF(list);
      Py_DECREF(res);
      return 0;
    }
  }

  return res;
}

static void igraphmodule_i_free_attribute_combination_records(
    igraph_attribute_combination_record_t* records) {
  igraph_attribute_combination_record_t* ptr = records;
  while (ptr->name != 0) {
    free((char*)ptr->name);
    ptr++;
  }
  free(records);
}

/* Auxiliary function for the common parts of
 * igraphmodule_i_attribute_combine_vertices and
 * igraphmodule_i_attribute_combine_edges
 */
static igraph_error_t igraphmodule_i_attribute_combine_dicts(PyObject *dict,
    PyObject *newdict, const igraph_vector_int_list_t *merges,
    const igraph_attribute_combination_t *comb) {
  PyObject *key, *value;
  Py_ssize_t pos;
  igraph_attribute_combination_record_t* todo;
  Py_ssize_t i, n;
  
  if (!PyDict_Check(dict) || !PyDict_Check(newdict)) {
    IGRAPH_ERROR("dict or newdict are corrupted", IGRAPH_FAILURE);
  }

  /* Allocate memory for the attribute_combination_records */
  n = PyDict_Size(dict);
  todo = (igraph_attribute_combination_record_t*)calloc(
    n + 1, sizeof(igraph_attribute_combination_record_t)
  );
  if (todo == 0) {
    IGRAPH_ERROR("cannot allocate memory for attribute combination", IGRAPH_ENOMEM);
  }
  for (i = 0; i < n + 1; i++) {
    todo[i].name = 0;       /* sentinel elements */
  }
  IGRAPH_FINALLY(igraphmodule_i_free_attribute_combination_records, todo);

  /* Collect what to do for each attribute in the source dict */
  pos = 0; i = 0;
  while (PyDict_Next(dict, &pos, &key, &value)) {
    todo[i].name = PyUnicode_CopyAsString(key);
    if (todo[i].name == 0) {
      IGRAPH_ERROR("PyUnicode_CopyAsString failed", IGRAPH_FAILURE);
    }
    IGRAPH_CHECK(igraph_attribute_combination_query(comb, todo[i].name, &todo[i].type, &todo[i].func));
    i++;
  }

  /* Combine the attributes. Here we make use of the fact that PyDict_Next
   * will iterate over the dict in the same order */
  pos = 0; i = 0;
  while (PyDict_Next(dict, &pos, &key, &value)) {
    PyObject *empty_str;
    PyObject *func;
    PyObject *newvalue;

    /* Safety check */
    if (!PyUnicode_IsEqualToASCIIString(key, todo[i].name)) {
      IGRAPH_ERROR("PyDict_Next iteration order not consistent. "
          "This should never happen. Please report the bug to the igraph "
          "developers!", IGRAPH_FAILURE);
    }

    newvalue = 0;
    switch (todo[i].type) {
      case IGRAPH_ATTRIBUTE_COMBINE_DEFAULT:
      case IGRAPH_ATTRIBUTE_COMBINE_IGNORE:
        break;

      case IGRAPH_ATTRIBUTE_COMBINE_FUNCTION:
        func = (PyObject*)todo[i].func;
        newvalue = igraphmodule_i_ac_func(value, merges, func);
        break;

      case IGRAPH_ATTRIBUTE_COMBINE_SUM:
        newvalue = igraphmodule_i_ac_sum(value, merges);
        break;

      case IGRAPH_ATTRIBUTE_COMBINE_PROD:
        newvalue = igraphmodule_i_ac_prod(value, merges);
        break;

      case IGRAPH_ATTRIBUTE_COMBINE_MIN:
        newvalue = igraphmodule_i_ac_builtin_func(value, merges, "min");
        break;

      case IGRAPH_ATTRIBUTE_COMBINE_MAX:
        newvalue = igraphmodule_i_ac_builtin_func(value, merges, "max");
        break;

      case IGRAPH_ATTRIBUTE_COMBINE_RANDOM:
        newvalue = igraphmodule_i_ac_random(value, merges);
        break;

      case IGRAPH_ATTRIBUTE_COMBINE_FIRST:
        newvalue = igraphmodule_i_ac_first(value, merges);
        break;

      case IGRAPH_ATTRIBUTE_COMBINE_LAST:
        newvalue = igraphmodule_i_ac_last(value, merges);
        break;

      case IGRAPH_ATTRIBUTE_COMBINE_MEAN:
        newvalue = igraphmodule_i_ac_mean(value, merges);
        break;

      case IGRAPH_ATTRIBUTE_COMBINE_MEDIAN:
        newvalue = igraphmodule_i_ac_median(value, merges);
        break;

      case IGRAPH_ATTRIBUTE_COMBINE_CONCAT:
        empty_str = PyUnicode_FromString("");
        func = PyObject_GetAttrString(empty_str, "join");
        newvalue = igraphmodule_i_ac_func(value, merges, func);
        Py_DECREF(func);
        Py_DECREF(empty_str);
        break;

      default:
        IGRAPH_ERROR("Unsupported combination type. "
            "This should never happen. Please report the bug to the igraph "
            "developers!", IGRAPH_FAILURE);
    }

    if (newvalue) {
      if (PyDict_SetItem(newdict, key, newvalue)) {
        Py_DECREF(newvalue);  /* PyDict_SetItem does not steal reference */
        IGRAPH_ERROR("PyDict_SetItem failed when combining attributes.", IGRAPH_FAILURE);
      }
      Py_DECREF(newvalue);    /* PyDict_SetItem does not steal reference */
    } else {
      /* We can arrive here for two reasons: first, if the attribute is to
       * be ignored explicitly; second, if there was an error. */
      if (PyErr_Occurred()) {
        IGRAPH_ERROR("Unexpected failure when combining attributes", IGRAPH_FAILURE);
      }
    }

    i++;
  }

  igraphmodule_i_free_attribute_combination_records(todo);
  IGRAPH_FINALLY_CLEAN(1);

  return IGRAPH_SUCCESS;
}

/* Combining vertices */
static igraph_error_t igraphmodule_i_attribute_combine_vertices(const igraph_t *graph,
    igraph_t *newgraph, const igraph_vector_int_list_t *merges,
    const igraph_attribute_combination_t *comb) {
  PyObject *dict, *newdict;
  igraph_error_t result;

  /* Get the attribute dicts */
  dict = ATTR_STRUCT_DICT(graph)[ATTRHASH_IDX_VERTEX];
  newdict = ATTR_STRUCT_DICT(newgraph)[ATTRHASH_IDX_VERTEX];

  /* Combine the attribute dicts */
  result = igraphmodule_i_attribute_combine_dicts(dict, newdict,
      merges, comb);

  /* Invalidate vertex name index */
  igraphmodule_i_attribute_struct_invalidate_vertex_name_index(ATTR_STRUCT(graph));

  return result;
}

/* Combining edges */
static igraph_error_t igraphmodule_i_attribute_combine_edges(const igraph_t *graph,
    igraph_t *newgraph, const igraph_vector_int_list_t *merges,
    const igraph_attribute_combination_t *comb) {
  PyObject *dict, *newdict;

  /* Get the attribute dicts */
  dict = ATTR_STRUCT_DICT(graph)[ATTRHASH_IDX_EDGE];
  newdict = ATTR_STRUCT_DICT(newgraph)[ATTRHASH_IDX_EDGE];

  return igraphmodule_i_attribute_combine_dicts(dict, newdict,
      merges, comb);
}

/* Getting attribute names and types */
static igraph_error_t igraphmodule_i_attribute_get_info(const igraph_t *graph,
                                             igraph_strvector_t *gnames,
                                             igraph_vector_int_t *gtypes,
                                             igraph_strvector_t *vnames,
                                             igraph_vector_int_t *vtypes,
                                             igraph_strvector_t *enames,
                                             igraph_vector_int_t *etypes) {
  igraph_strvector_t *names[3] = { gnames, vnames, enames };
  igraph_vector_int_t *types[3] = { gtypes, vtypes, etypes };
  int i, retval;
  Py_ssize_t j, k, l, m;
  
  for (i = 0; i < 3; i++) {
    igraph_strvector_t *n = names[i];
    igraph_vector_int_t *t = types[i];
    PyObject *dict = ATTR_STRUCT_DICT(graph)[i];
    PyObject *keys;
    PyObject *values;

    keys = PyDict_Keys(dict);
    if (!keys) {
      IGRAPH_ERROR("Internal error in PyDict_Keys", IGRAPH_FAILURE);
    }

    if (n) {
      retval = igraphmodule_PyList_to_existing_strvector_t(keys, n);
      if (retval) {
        IGRAPH_ERROR("Cannot convert Python list to existing igraph_strvector_t", IGRAPH_FAILURE);
      }
    }

    if (t) {
      k = PyList_Size(keys);
      IGRAPH_CHECK(igraph_vector_int_resize(t, k));
      for (j = 0; j < k; j++) {
        int is_numeric = 1;
        int is_string = 1;
        int is_boolean = 1;
        values = PyDict_GetItem(dict, PyList_GetItem(keys, j));
        if (PyList_Check(values)) {
          m = PyList_Size(values);
          for (l = 0; l < m && is_numeric; l++) {
            if (!PyObject_allowed_in_numeric_attribute(PyList_GetItem(values, l))) {
              is_numeric = 0;
            }
          }
          for (l = 0; l < m && is_string; l++) {
            if (!PyObject_allowed_in_string_attribute(PyList_GetItem(values, l))) {
              is_string = 0;
            }
          }
          for (l = 0; l < m && is_boolean; l++) {
            if (!PyObject_allowed_in_boolean_attribute(PyList_GetItem(values, l))) {
              is_boolean = 0;
            }
          }
        } else {
          if (!PyObject_allowed_in_numeric_attribute(values)) {
            is_numeric = 0;
          }
          if (!PyObject_allowed_in_string_attribute(values)) {
            is_string = 0;
          }
          if (!PyObject_allowed_in_boolean_attribute(values)) {
            is_boolean = 0;
          }
        }
        if (is_boolean) {
          VECTOR(*t)[j] = IGRAPH_ATTRIBUTE_BOOLEAN;
        } else if (is_numeric) {
          VECTOR(*t)[j] = IGRAPH_ATTRIBUTE_NUMERIC;
        } else if (is_string) {
          VECTOR(*t)[j] = IGRAPH_ATTRIBUTE_STRING;
        } else {
          VECTOR(*t)[j] = IGRAPH_ATTRIBUTE_OBJECT;
        }
      }
    }
    
    Py_DECREF(keys);
  }
 
  return IGRAPH_SUCCESS;
}

/* Checks whether the graph has a graph/vertex/edge attribute with the given name */
igraph_bool_t igraphmodule_i_attribute_has_attr(const igraph_t *graph,
                                                igraph_attribute_elemtype_t type,
                                                const char* name) {
  switch (type) {
  case IGRAPH_ATTRIBUTE_GRAPH:
    return igraphmodule_has_graph_attribute(graph, name);
  case IGRAPH_ATTRIBUTE_VERTEX:
    return igraphmodule_has_vertex_attribute(graph, name);
  case IGRAPH_ATTRIBUTE_EDGE:
    return igraphmodule_has_edge_attribute(graph, name);
  default:
    return 0;
  }
}

/* Returns the type of a given attribute */
igraph_error_t igraphmodule_i_attribute_get_type(const igraph_t *graph,
                                      igraph_attribute_type_t *type,
                                      igraph_attribute_elemtype_t elemtype,
                                      const char *name) {
  int attrnum;
  int is_numeric, is_string, is_boolean;
  Py_ssize_t i, j;
  PyObject *o, *dict;

  switch (elemtype) {
  case IGRAPH_ATTRIBUTE_GRAPH:  attrnum = ATTRHASH_IDX_GRAPH;  break;
  case IGRAPH_ATTRIBUTE_VERTEX: attrnum = ATTRHASH_IDX_VERTEX; break;
  case IGRAPH_ATTRIBUTE_EDGE:   attrnum = ATTRHASH_IDX_EDGE;   break;
  default: IGRAPH_ERROR("No such attribute type", IGRAPH_EINVAL); break;
  }

  /* Get the attribute dict */
  dict = ATTR_STRUCT_DICT(graph)[attrnum];

  /* Check whether the attribute exists */
  o = PyDict_GetItemString(dict, name);
  if (o == 0) {
    IGRAPH_ERROR("No such attribute", IGRAPH_EINVAL);
  }

  /* Basic type check */
  if (attrnum != ATTRHASH_IDX_GRAPH && !PyList_Check(o)) {
    IGRAPH_ERROR("attribute hash type mismatch", IGRAPH_EINVAL);
  }

  j = PyList_Size(o);
  if (j == 0) {
    *type = IGRAPH_ATTRIBUTE_NUMERIC;
    return IGRAPH_SUCCESS;
  }

  /* Go on with the checks */
  is_numeric = is_string = is_boolean = 1;
  if (attrnum > 0) {
    PyObject *item;
    for (i = 0; i < j && is_numeric; i++) {
      item = PyList_GetItem(o, i);
      if (!PyObject_allowed_in_numeric_attribute(item)) {
        is_numeric = 0;
      }
    }
    for (i = 0; i < j && is_string; i++) {
      item = PyList_GetItem(o, i);
      if (!PyObject_allowed_in_string_attribute(item)) {
        is_string = 0;
      }
    }
    for (i = 0; i < j && is_boolean; i++) {
      item = PyList_GetItem(o, i);
      if (!PyObject_allowed_in_boolean_attribute(item)) {
        is_boolean = 0;
      }
    }
  } else {
    if (!PyObject_allowed_in_numeric_attribute(o)) {
      is_numeric = 0;
    }
    if (!PyObject_allowed_in_string_attribute(o)) {
      is_string = 0;
    }
    if (!PyObject_allowed_in_boolean_attribute(o)) {
      is_boolean = 0;
    }
  }
  if (is_boolean) {
    *type = IGRAPH_ATTRIBUTE_BOOLEAN;
  } else if (is_numeric) {
    *type = IGRAPH_ATTRIBUTE_NUMERIC;
  } else if (is_string) {
    *type = IGRAPH_ATTRIBUTE_STRING;
  } else {
    *type = IGRAPH_ATTRIBUTE_OBJECT;
  }
  return IGRAPH_SUCCESS;
}

/* Getting Boolean graph attributes */
igraph_error_t igraphmodule_i_get_boolean_graph_attr(const igraph_t *graph,
                                          const char *name, igraph_vector_bool_t *value) {
  PyObject *dict, *o;
  dict = ATTR_STRUCT_DICT(graph)[ATTRHASH_IDX_GRAPH];
  /* No error checking, if we get here, the type has already been checked by previous
     attribute handler calls... hopefully :) Same applies for the other handlers. */
  o = PyDict_GetItemString(dict, name);
  if (!o) {
    IGRAPH_ERROR("No such attribute", IGRAPH_EINVAL);
  }
  IGRAPH_CHECK(igraph_vector_bool_resize(value, 1));
  VECTOR(*value)[0] = PyObject_IsTrue(o);
  return IGRAPH_SUCCESS;
}

/* Getting numeric graph attributes */
igraph_error_t igraphmodule_i_get_numeric_graph_attr(const igraph_t *graph,
                                          const char *name, igraph_vector_t *value) {
  PyObject *dict, *o, *result;
  dict = ATTR_STRUCT_DICT(graph)[ATTRHASH_IDX_GRAPH];
  /* No error checking, if we get here, the type has already been checked by previous
     attribute handler calls... hopefully :) Same applies for the other handlers. */
  o = PyDict_GetItemString(dict, name);
  if (!o) {
    IGRAPH_ERROR("No such attribute", IGRAPH_EINVAL);
  }
  IGRAPH_CHECK(igraph_vector_resize(value, 1));
  if (o == Py_None) {
    VECTOR(*value)[0] = IGRAPH_NAN;
    return IGRAPH_SUCCESS;
  }
  result = PyNumber_Float(o);
  if (result) {
    VECTOR(*value)[0] = PyFloat_AsDouble(o);
    Py_DECREF(result);
  } else IGRAPH_ERROR("Internal error in PyFloat_AsDouble", IGRAPH_EINVAL); 

  return IGRAPH_SUCCESS;
}

/* Getting string graph attributes */
igraph_error_t igraphmodule_i_get_string_graph_attr(const igraph_t *graph,
                                         const char *name, igraph_strvector_t *value) {
  PyObject *dict, *o, *str = 0;
  const char* c_str;

  dict = ATTR_STRUCT_DICT(graph)[ATTRHASH_IDX_GRAPH];
  o = PyDict_GetItemString(dict, name);
  if (!o) {
    IGRAPH_ERROR("No such attribute", IGRAPH_EINVAL);
  }
  IGRAPH_CHECK(igraph_strvector_resize(value, 1));

  /* For Python 3.x, we simply call PyObject_Str, which produces a
   * Unicode string, then encode it into UTF-8, except when we
   * already have a PyBytes object -- this is assumed to be in
   * UTF-8.
   */
  if (PyBytes_Check(o)) {
    str = o;
    Py_INCREF(str);
  } else {
    PyObject* unicode = PyObject_Str(o);
    if (unicode == 0) {
      IGRAPH_ERROR("Internal error in PyObject_Str", IGRAPH_EINVAL);
    }
    str = PyUnicode_AsEncodedString(unicode, "utf-8", "xmlcharrefreplace");
    Py_DECREF(unicode);
  }

  if (str == 0) {
    IGRAPH_ERROR("Internal error in PyObject_Str", IGRAPH_EINVAL);
  }
  
  c_str = PyBytes_AsString(str);
  if (c_str == 0) {
    IGRAPH_ERROR("Internal error in PyBytes_AsString", IGRAPH_EINVAL);
  }

  IGRAPH_CHECK(igraph_strvector_set(value, 0, c_str));

  Py_XDECREF(str);

  return IGRAPH_SUCCESS;
}

/* Getting numeric vertex attributes */
igraph_error_t igraphmodule_i_get_numeric_vertex_attr(const igraph_t *graph,
                                           const char *name,
                                           igraph_vs_t vs,
                                           igraph_vector_t *value) {
  PyObject *dict, *list, *result, *o;
  igraph_vector_t newvalue;

  dict = ATTR_STRUCT_DICT(graph)[ATTRHASH_IDX_VERTEX];
  list = PyDict_GetItemString(dict, name);
  if (!list) IGRAPH_ERROR("No such attribute", IGRAPH_EINVAL);

  if (igraph_vs_is_all(&vs)) {
    if (igraphmodule_PyObject_float_to_vector_t(list, &newvalue))
      IGRAPH_ERROR("Internal error", IGRAPH_EINVAL);
    igraph_vector_update(value, &newvalue);
    igraph_vector_destroy(&newvalue);
  } else {
    igraph_vit_t it;
    igraph_integer_t i = 0;
    IGRAPH_CHECK(igraph_vit_create(graph, vs, &it));
    IGRAPH_FINALLY(igraph_vit_destroy, &it);
    IGRAPH_CHECK(igraph_vector_resize(value, IGRAPH_VIT_SIZE(it)));
    while (!IGRAPH_VIT_END(it)) {
      o = PyList_GetItem(list, (Py_ssize_t)IGRAPH_VIT_GET(it));
      if (o != Py_None) {
        result = PyNumber_Float(o);
        VECTOR(*value)[i] = PyFloat_AsDouble(result);
        Py_XDECREF(result);
      } else {
        VECTOR(*value)[i] = IGRAPH_NAN;
      }
      IGRAPH_VIT_NEXT(it);
      i++;
    }
    igraph_vit_destroy(&it);
    IGRAPH_FINALLY_CLEAN(1);
  }

  return IGRAPH_SUCCESS;
}

/* Getting string vertex attributes */
igraph_error_t igraphmodule_i_get_string_vertex_attr(const igraph_t *graph,
                                          const char *name,
                                          igraph_vs_t vs,
                                          igraph_strvector_t *value) {
  PyObject *dict, *list, *result;
  igraph_strvector_t newvalue;

  dict = ATTR_STRUCT_DICT(graph)[ATTRHASH_IDX_VERTEX];
  list = PyDict_GetItemString(dict, name);
  if (!list)
    IGRAPH_ERROR("No such attribute", IGRAPH_EINVAL);

  if (igraph_vs_is_all(&vs)) {
    if (igraphmodule_PyList_to_strvector_t(list, &newvalue))
      IGRAPH_ERROR("Internal error", IGRAPH_EINVAL);
    igraph_strvector_destroy(value);
    *value=newvalue;
  } else {
    igraph_vit_t it;
    igraph_integer_t i = 0;
    IGRAPH_CHECK(igraph_vit_create(graph, vs, &it));
    IGRAPH_FINALLY(igraph_vit_destroy, &it);
    IGRAPH_CHECK(igraph_strvector_resize(value, IGRAPH_VIT_SIZE(it)));
    while (!IGRAPH_VIT_END(it)) {
      igraph_integer_t v = IGRAPH_VIT_GET(it);
      char* str;

      result = PyList_GetItem(list, v);
      if (result == 0)
        IGRAPH_ERROR("null element in PyList", IGRAPH_EINVAL);

      str = igraphmodule_PyObject_ConvertToCString(result);
      if (str == 0)
        IGRAPH_ERROR("error while calling igraphmodule_PyObject_ConvertToCString", IGRAPH_EINVAL);

      /* Note: this is a bit inefficient here, igraphmodule_PyObject_ConvertToCString
       * allocates a new string which could be copied into the string
       * vector straight away. Instead of that, the string vector makes
       * another copy. Probably the performance hit is not too severe.
       */
      igraph_strvector_set(value, i, str);
      free(str);

      IGRAPH_VIT_NEXT(it);
      i++;
    }
    igraph_vit_destroy(&it);
    IGRAPH_FINALLY_CLEAN(1);
  }

  return IGRAPH_SUCCESS;
}

/* Getting boolean vertex attributes */
igraph_error_t igraphmodule_i_get_boolean_vertex_attr(const igraph_t *graph,
                                           const char *name,
                                           igraph_vs_t vs,
                                           igraph_vector_bool_t *value) {
  PyObject *dict, *list, *o;
  igraph_vector_bool_t newvalue;

  dict = ATTR_STRUCT_DICT(graph)[ATTRHASH_IDX_VERTEX];
  list = PyDict_GetItemString(dict, name);
  if (!list) IGRAPH_ERROR("No such attribute", IGRAPH_EINVAL);

  if (igraph_vs_is_all(&vs)) {
    if (igraphmodule_PyObject_to_vector_bool_t(list, &newvalue))
      IGRAPH_ERROR("Internal error", IGRAPH_EINVAL);
    igraph_vector_bool_update(value, &newvalue);
    igraph_vector_bool_destroy(&newvalue);
  } else {
    igraph_vit_t it;
    igraph_integer_t i = 0;
    IGRAPH_CHECK(igraph_vit_create(graph, vs, &it));
    IGRAPH_FINALLY(igraph_vit_destroy, &it);
    IGRAPH_CHECK(igraph_vector_bool_resize(value, IGRAPH_VIT_SIZE(it)));
    while (!IGRAPH_VIT_END(it)) {
      o = PyList_GetItem(list, (Py_ssize_t)IGRAPH_VIT_GET(it));
      VECTOR(*value)[i] = PyObject_IsTrue(o);
      IGRAPH_VIT_NEXT(it);
      i++;
    }
    igraph_vit_destroy(&it);
    IGRAPH_FINALLY_CLEAN(1);
  }

  return IGRAPH_SUCCESS;
}

/* Getting numeric edge attributes */
igraph_error_t igraphmodule_i_get_numeric_edge_attr(const igraph_t *graph,
                                         const char *name,
                                         igraph_es_t es,
                                         igraph_vector_t *value) {
  PyObject *dict, *list, *result, *o;
  igraph_vector_t newvalue;

  dict = ATTR_STRUCT_DICT(graph)[ATTRHASH_IDX_EDGE];
  list = PyDict_GetItemString(dict, name);
  if (!list) IGRAPH_ERROR("No such attribute", IGRAPH_EINVAL);

  if (igraph_es_is_all(&es)) {
    if (igraphmodule_PyObject_float_to_vector_t(list, &newvalue))
      IGRAPH_ERROR("Internal error", IGRAPH_EINVAL);
    igraph_vector_update(value, &newvalue);
    igraph_vector_destroy(&newvalue);
  } else {
    igraph_eit_t it;
    igraph_integer_t i = 0;
    IGRAPH_CHECK(igraph_eit_create(graph, es, &it));
    IGRAPH_FINALLY(igraph_eit_destroy, &it);
    IGRAPH_CHECK(igraph_vector_resize(value, IGRAPH_EIT_SIZE(it)));
    while (!IGRAPH_EIT_END(it)) {
      o = PyList_GetItem(list, (Py_ssize_t)IGRAPH_EIT_GET(it));
      if (o != Py_None) {
        result = PyNumber_Float(o);
        VECTOR(*value)[i] = PyFloat_AsDouble(result);
        Py_XDECREF(result);
      } else VECTOR(*value)[i] = IGRAPH_NAN;
      IGRAPH_EIT_NEXT(it);
      i++;
    }
    igraph_eit_destroy(&it);
    IGRAPH_FINALLY_CLEAN(1);
  }

  return IGRAPH_SUCCESS;
}

/* Getting string edge attributes */
igraph_error_t igraphmodule_i_get_string_edge_attr(const igraph_t *graph,
                                        const char *name,
                                        igraph_es_t es,
                                        igraph_strvector_t *value) {
  PyObject *dict, *list, *result;
  igraph_strvector_t newvalue;

  dict = ATTR_STRUCT_DICT(graph)[ATTRHASH_IDX_EDGE];
  list = PyDict_GetItemString(dict, name);
  if (!list) IGRAPH_ERROR("No such attribute", IGRAPH_EINVAL);

  if (igraph_es_is_all(&es)) {
    if (igraphmodule_PyList_to_strvector_t(list, &newvalue))
      IGRAPH_ERROR("Internal error", IGRAPH_EINVAL);
    igraph_strvector_destroy(value);
    *value=newvalue;
  } else {
    igraph_eit_t it;
    igraph_integer_t i = 0;
    IGRAPH_CHECK(igraph_eit_create(graph, es, &it));
    IGRAPH_FINALLY(igraph_eit_destroy, &it);
    IGRAPH_CHECK(igraph_strvector_resize(value, IGRAPH_EIT_SIZE(it)));
    while (!IGRAPH_EIT_END(it)) {
      char* str;

      result = PyList_GetItem(list, (Py_ssize_t)IGRAPH_EIT_GET(it));
      if (result == 0)
        IGRAPH_ERROR("null element in PyList", IGRAPH_EINVAL);

      str = igraphmodule_PyObject_ConvertToCString(result);
      if (str == 0)
        IGRAPH_ERROR("error while calling igraphmodule_PyObject_ConvertToCString", IGRAPH_EINVAL);

      /* Note: this is a bit inefficient here, igraphmodule_PyObject_ConvertToCString
       * allocates a new string which could be copied into the string
       * vector straight away. Instead of that, the string vector makes
       * another copy. Probably the performance hit is not too severe.
       */
      igraph_strvector_set(value, i, str);
      free(str);

      IGRAPH_EIT_NEXT(it);
      i++;
    }
    igraph_eit_destroy(&it);
    IGRAPH_FINALLY_CLEAN(1);
  }

  return IGRAPH_SUCCESS;
}

/* Getting boolean edge attributes */
igraph_error_t igraphmodule_i_get_boolean_edge_attr(const igraph_t *graph,
                                         const char *name,
                                         igraph_es_t es,
                                         igraph_vector_bool_t *value) {
  PyObject *dict, *list, *o;
  igraph_vector_bool_t newvalue;

  dict = ATTR_STRUCT_DICT(graph)[ATTRHASH_IDX_EDGE];
  list = PyDict_GetItemString(dict, name);
  if (!list) IGRAPH_ERROR("No such attribute", IGRAPH_EINVAL);

  if (igraph_es_is_all(&es)) {
    if (igraphmodule_PyObject_to_vector_bool_t(list, &newvalue))
      IGRAPH_ERROR("Internal error", IGRAPH_EINVAL);
    igraph_vector_bool_update(value, &newvalue);
    igraph_vector_bool_destroy(&newvalue);
  } else {
    igraph_eit_t it;
    igraph_integer_t i=0;
    IGRAPH_CHECK(igraph_eit_create(graph, es, &it));
    IGRAPH_FINALLY(igraph_eit_destroy, &it);
    IGRAPH_CHECK(igraph_vector_bool_resize(value, IGRAPH_EIT_SIZE(it)));
    while (!IGRAPH_EIT_END(it)) {
      o = PyList_GetItem(list, (Py_ssize_t)IGRAPH_EIT_GET(it));
      VECTOR(*value)[i] = PyObject_IsTrue(o);
      IGRAPH_EIT_NEXT(it);
      i++;
    }
    igraph_eit_destroy(&it);
    IGRAPH_FINALLY_CLEAN(1);
  }

  return IGRAPH_SUCCESS;
}

static igraph_attribute_table_t igraphmodule_attribute_table = {
  igraphmodule_i_attribute_init,
  igraphmodule_i_attribute_destroy,
  igraphmodule_i_attribute_copy,
  igraphmodule_i_attribute_add_vertices,
  igraphmodule_i_attribute_permute_vertices,
  igraphmodule_i_attribute_combine_vertices,
  igraphmodule_i_attribute_add_edges,
  igraphmodule_i_attribute_permute_edges,
  igraphmodule_i_attribute_combine_edges,
  igraphmodule_i_attribute_get_info,
  igraphmodule_i_attribute_has_attr,
  igraphmodule_i_attribute_get_type,
  igraphmodule_i_get_numeric_graph_attr,
  igraphmodule_i_get_string_graph_attr,
  igraphmodule_i_get_boolean_graph_attr,
  igraphmodule_i_get_numeric_vertex_attr,
  igraphmodule_i_get_string_vertex_attr,
  igraphmodule_i_get_boolean_vertex_attr,
  igraphmodule_i_get_numeric_edge_attr,
  igraphmodule_i_get_string_edge_attr,
  igraphmodule_i_get_boolean_edge_attr,
};

void igraphmodule_initialize_attribute_handler(void) {
  igraph_set_attribute_table(&igraphmodule_attribute_table);
}

/**
 * Checks whether the given Python object can be a valid attribute name or not.
 * Returns 1 if the object could be used as an attribute name, 0 otherwise.
 * Also raises a suitable Python exception if needed.
 */
int igraphmodule_attribute_name_check(PyObject* obj) {
  PyTypeObject* type_obj;

  if (obj != 0 && PyBaseString_Check(obj)) {
    return 1;
  }

  type_obj = Py_TYPE(obj);
  if (type_obj != 0) {
    PyErr_Format(PyExc_TypeError, "igraph supports string attribute names only, got %R", type_obj);
  } else {
    PyErr_Format(PyExc_TypeError, "igraph supports string attribute names only");
  }

  return 0;
}

