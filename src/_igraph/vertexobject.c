/* -*- mode: C -*-  */
/* vim: set ts=2 sw=2 sts=2 et: */

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

#include "attributes.h"
#include "convert.h"
#include "edgeobject.h"
#include "error.h"
#include "graphobject.h"
#include "pyhelpers.h"
#include "vertexobject.h"

/**
 * \ingroup python_interface
 * \defgroup python_interface_vertex Vertex object
 */

PyTypeObject* igraphmodule_VertexType;

PyObject* igraphmodule_Vertex_attributes(igraphmodule_VertexObject* self, PyObject* _null);

/**
 * \ingroup python_interface_vertex
 * \brief Checks whether the given Python object is a vertex
 */
int igraphmodule_Vertex_Check(PyObject* obj) {
  return obj ? PyObject_IsInstance(obj, (PyObject*)igraphmodule_VertexType) : 0;
}

/**
 * \ingroup python_interface_vertex
 * \brief Checks whether the index in the given vertex object is a valid one.
 * \return nonzero if the vertex object is valid. Raises an appropriate Python
 *   exception and returns zero if the vertex object is invalid.
 */
int igraphmodule_Vertex_Validate(PyObject* obj) {
  igraph_int_t n;
  igraphmodule_VertexObject *self;
  igraphmodule_GraphObject *graph;

  if (!igraphmodule_Vertex_Check(obj)) {
    PyErr_SetString(PyExc_TypeError, "object is not a Vertex");
    return 0;
  }

  self = (igraphmodule_VertexObject*)obj;
  graph = self->gref;

  if (graph == 0) {
    PyErr_SetString(PyExc_ValueError, "Vertex object refers to a null graph");
    return 0;
  }

  if (self->idx < 0) {
    PyErr_SetString(PyExc_ValueError, "Vertex object refers to a negative vertex index");
    return 0;
  }

  n = igraph_vcount(&graph->g);

  if (self->idx >= n) {
    PyErr_SetString(PyExc_ValueError, "Vertex object refers to a nonexistent vertex");
    return 0;
  }

  return 1;
}

/**
 * \ingroup python_interface_vertex
 * \brief Allocates a new Python vertex object
 * \param gref the \c igraph.Graph being referenced by the vertex
 * \param idx the index of the vertex
 *
 * \warning \c igraph references its vertices by indices, so if
 * you delete some vertices from the graph, the vertex indices will
 * change. Since the \c igraph.Vertex objects do not follow these
 * changes, your existing vertex objects will point to elsewhere
 * (or they might even get invalidated).
 */
PyObject* igraphmodule_Vertex_New(igraphmodule_GraphObject *gref, igraph_int_t idx) {
  return PyObject_CallFunction((PyObject*) igraphmodule_VertexType, "On", gref, (Py_ssize_t) idx);
}

/**
 * \ingroup python_interface_vertex
 * \brief Initialize a new vertex object for a given graph
 * \return the initialized PyObject
 */
static int igraphmodule_Vertex_init(igraphmodule_EdgeObject *self, PyObject *args, PyObject *kwds) {
  static char *kwlist[] = { "graph", "vid", NULL };
  PyObject *g, *index_o = Py_None;
  igraph_int_t vid;
  igraph_t *graph;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O!|O", kwlist,
    igraphmodule_GraphType, &g, &index_o)) {
    return -1;
  }

  graph = &((igraphmodule_GraphObject*)g)->g;

  if (igraphmodule_PyObject_to_vid(index_o, &vid, graph)) {
    return -1;
  }

  Py_INCREF(g);
  self->gref = (igraphmodule_GraphObject*)g;
  self->idx = vid;
  self->hash = -1;

  return 0;
}

/**
 * \ingroup python_interface_vertex
 * \brief Deallocates a Python representation of a given vertex object
 */
static void igraphmodule_Vertex_dealloc(igraphmodule_VertexObject* self) {
  RC_DEALLOC("Vertex", self);
  Py_CLEAR(self->gref);
  PY_FREE_AND_DECREF_TYPE(self, igraphmodule_VertexType);
}

/** \ingroup python_interface_vertex
 * \brief Formats an \c igraph.Vertex object to a string
 *
 * \return the formatted textual representation as a \c PyObject
 */
static PyObject* igraphmodule_Vertex_repr(igraphmodule_VertexObject *self) {
  PyObject *s;
  PyObject *attrs;

  attrs = igraphmodule_Vertex_attributes(self, NULL);
  if (attrs == 0) {
    return NULL;
  }

  s = PyUnicode_FromFormat("igraph.Vertex(%R, %" IGRAPH_PRId ", %R)",
      (PyObject*)self->gref, self->idx, attrs);
  Py_DECREF(attrs);

  return s;
}

/** \ingroup python_interface_vertex
 * \brief Returns the hash code of the vertex
 */
static long igraphmodule_Vertex_hash(igraphmodule_VertexObject* self) {
  long hash_graph;
  long hash_index;
  long result;
  PyObject* index_o;

  if (self->hash != -1)
    return self->hash;

  index_o = igraphmodule_integer_t_to_PyObject(self->idx);
  if (index_o == 0)
    return -1;

  hash_index = PyObject_Hash(index_o);
  Py_DECREF(index_o);

  if (hash_index == -1)
    return -1;

  /* Graph objects are unhashable from Python so we cannot call PyObject_Hash
   * directly. */
  hash_graph = igraphmodule_Py_HashPointer(self->gref);
  if (hash_graph == -1)
    return -1;

  result = hash_graph ^ hash_index;
  if (result == -1)
    result = 590923713U;

  self->hash = result;

  return result;
}

/** \ingroup python_interface_vertex
 * \brief Rich comparison of a vertex with another
 */
static PyObject* igraphmodule_Vertex_richcompare(igraphmodule_VertexObject *a,
    PyObject *b, int op) {

  igraphmodule_VertexObject* self = a;
  igraphmodule_VertexObject* other;

  if (!igraphmodule_Vertex_Check(b))
    Py_RETURN_NOTIMPLEMENTED;

  other = (igraphmodule_VertexObject*)b;

  if (self->gref != other->gref)
    Py_RETURN_FALSE;

  switch (op) {
    case Py_EQ:
      Py_RETURN(self->idx == other->idx);

    case Py_NE:
      Py_RETURN(self->idx != other->idx);

    case Py_LE:
      Py_RETURN(self->idx <= other->idx);

    case Py_LT:
      Py_RETURN(self->idx <  other->idx);

    case Py_GE:
      Py_RETURN(self->idx >= other->idx);

    case Py_GT:
      Py_RETURN(self->idx >  other->idx);

    default:
      Py_RETURN_NOTIMPLEMENTED;
  }
}

/** \ingroup python_interface_vertex
 * \brief Returns the number of vertex attributes
 */
Py_ssize_t igraphmodule_Vertex_attribute_count(igraphmodule_VertexObject* self) {
  igraphmodule_GraphObject *o = self->gref;

  if (!o || !((PyObject**)o->g.attr)[1]) {
    return 0;
  } else {
    return PyDict_Size(((PyObject**)o->g.attr)[1]);
  }
}

/** \ingroup python_interface_vertex
 * \brief Returns the list of attribute names
 */
PyObject* igraphmodule_Vertex_attribute_names(igraphmodule_VertexObject* self, PyObject* Py_UNUSED(_null)) {
  return self->gref ? igraphmodule_Graph_vertex_attributes(self->gref, NULL) : NULL;
}

/** \ingroup python_interface_vertex
 * \brief Returns a dict with attribue names and values
 */
PyObject* igraphmodule_Vertex_attributes(igraphmodule_VertexObject* self, PyObject* Py_UNUSED(_null)) {
  igraphmodule_GraphObject *o = self->gref;
  PyObject *names, *dict;
  Py_ssize_t i, n;

  if (!igraphmodule_Vertex_Validate((PyObject*)self)) {
    return 0;
  }

  dict = PyDict_New();
  if (!dict) {
    return NULL;
  }

  names = igraphmodule_Graph_vertex_attributes(o, NULL);
  if (!names) {
    Py_DECREF(dict);
    return NULL;
  }

  n = PyList_Size(names);
  for (i = 0; i < n; i++) {
    PyObject *name = PyList_GetItem(names, i);
    if (name) {
      PyObject *dictit;
      dictit = PyDict_GetItem(((PyObject**)o->g.attr)[ATTRHASH_IDX_VERTEX], name);
      if (dictit) {
        PyObject *value = PyList_GetItem(dictit, self->idx);
        if (value) {
          /* No need to Py_INCREF, PyDict_SetItem will do that */
          PyDict_SetItem(dict, name, value);
        }
      } else {
        Py_DECREF(dict);
        Py_DECREF(names);
        return NULL;
      }
    } else {
      Py_DECREF(dict);
      Py_DECREF(names);
      return NULL;
    }
  }

  Py_DECREF(names);

  return dict;
}

/**
 * \ingroup python_interface_vertex
 * \brief Updates some attributes of a vertex
 *
 * Incidentally, this method is re-used intact in edgeobject.c for edges.
 *
 * \param self the vertex object
 * \param args positional arguments
 * \param kwds keyword arguments
 */
PyObject* igraphmodule_Vertex_update_attributes(PyObject* self, PyObject* args,
    PyObject* kwds) {
  PyObject* items[] = { Py_None, kwds, 0 };
  PyObject** pObj;
  PyObject *key, *value, *it, *item, *keys;

  igraph_bool_t ok = true;

  if (!PyArg_ParseTuple(args, "|O", &items[0]))
    return NULL;

  pObj = items;
  for (pObj = items; ok && *pObj != 0; pObj++) {
    PyObject* obj = *pObj;
    PyObject* keys_func;

    if (obj == Py_None)
      continue;

    keys_func = PyObject_GetAttrString(obj, "keys");
    if (keys_func == 0)
      PyErr_Clear();

    if (keys_func != 0 && PyCallable_Check(keys_func)) {
      /* Object has a "keys" method, so we iterate over the keys */
      keys = PyObject_CallObject(keys_func, 0);
      if (keys == 0) {
        ok = false;
      } else {
        /* Iterate over the keys */
        it = PyObject_GetIter(keys);
        if (it == 0) {
          ok = false;
        } else {
          while (ok && ((key = PyIter_Next(it)) != 0)) {
            value = PyObject_GetItem(obj, key);
            if (value == 0) {
              ok = false;
            } else {
              PyObject_SetItem((PyObject*)self, key, value);
              Py_DECREF(value);
            }
            Py_DECREF(key);
          }
          Py_DECREF(it);
          if (PyErr_Occurred())
            ok = false;
        }
        Py_DECREF(keys);
      }
    } else {
      /* Object does not have a "keys" method; assume that it
       * yields tuples when treated as an iterator */
      it = PyObject_GetIter(obj);
      if (!it) {
        ok = false;
      } else {
        while (ok && ((item = PyIter_Next(it)) != 0)) {
          if (!PySequence_Check(item) || PyBaseString_Check(item)) {
            PyErr_SetString(PyExc_TypeError, "cannot convert update sequence element to a sequence");
            ok = false;
          } else {
            key = PySequence_GetItem(item, 0);
            if (key == 0) {
              ok = false;
            } else {
              value = PySequence_GetItem(item, 1);
              if (value == 0) {
                ok = false;
              } else {
                PyObject_SetItem((PyObject*)self, key, value);
                Py_DECREF(value);
              }
              Py_DECREF(key);
            }
          }
          Py_DECREF(item);
        }
        Py_DECREF(it);
        if (PyErr_Occurred())
          ok = false;
      }
    }

    if (keys_func != 0) {
      Py_DECREF(keys_func);
    }
  }

  if (ok)
    Py_RETURN_NONE;
  return 0;
}

/**
 * \ingroup python_interface_vertex
 * \brief Returns the inbound and outbound edges of a vertex
 *
 * \param self the vertex object
 * \param args positional arguments
 * \param kwds keyword arguments
 */
PyObject* igraphmodule_Vertex_all_edges(PyObject* self, PyObject* Py_UNUSED(_null)) {
  return PyObject_CallMethod(self, "incident", "i", (int) IGRAPH_ALL);
}

/**
 * \ingroup python_interface_vertex
 * \brief Returns the inbound edges of a vertex
 *
 * \param self the vertex object
 * \param args positional arguments
 * \param kwds keyword arguments
 */
PyObject* igraphmodule_Vertex_in_edges(PyObject* self, PyObject* Py_UNUSED(_null)) {
  return PyObject_CallMethod(self, "incident", "i", (int) IGRAPH_IN);
}

/**
 * \ingroup python_interface_vertex
 * \brief Returns the outbound edges of a vertex
 *
 * \param self the vertex object
 * \param args positional arguments
 * \param kwds keyword arguments
 */
PyObject* igraphmodule_Vertex_out_edges(PyObject* self, PyObject* Py_UNUSED(_null)) {
  return PyObject_CallMethod(self, "incident", "i", (int) IGRAPH_OUT);
}

/** \ingroup python_interface_vertex
 * \brief Returns the corresponding value to a given attribute of the vertex
 * \param self the vertex object
 * \param s the attribute name to be queried
 */
PyObject* igraphmodule_Vertex_get_attribute(igraphmodule_VertexObject* self,
                       PyObject* s) {
  igraphmodule_GraphObject *o = self->gref;
  PyObject* result;

  if (!igraphmodule_Vertex_Validate((PyObject*)self))
    return 0;

  if (!igraphmodule_attribute_name_check(s))
    return 0;

  result=PyDict_GetItem(((PyObject**)o->g.attr)[ATTRHASH_IDX_VERTEX], s);
  if (result) {
    /* result is a list, so get the element with index self->idx */
    if (!PyList_Check(result)) {
      PyErr_SetString(igraphmodule_InternalError, "Vertex attribute dict member is not a list");
      return NULL;
    }
    result=PyList_GetItem(result, self->idx);
    Py_INCREF(result);
    return result;
  }

  /* result is NULL, check whether there was an error */
  if (!PyErr_Occurred())
    PyErr_SetString(PyExc_KeyError, "Attribute does not exist");
  return NULL;
}

/** \ingroup python_interface_vertex
 * \brief Sets the corresponding value of a given attribute of the vertex
 * \param self the vertex object
 * \param k the attribute name to be set
 * \param v the value to be set
 * \return 0 if everything's ok, -1 in case of error
 */
int igraphmodule_Vertex_set_attribute(igraphmodule_VertexObject* self, PyObject* k, PyObject* v) {
  igraphmodule_GraphObject *o=self->gref;
  PyObject* result;
  int r;

  if (!igraphmodule_Vertex_Validate((PyObject*)self))
    return -1;

  if (!igraphmodule_attribute_name_check(k))
    return -1;

  if (PyUnicode_IsEqualToASCIIString(k, "name"))
    igraphmodule_invalidate_vertex_name_index(&o->g);

  if (v==NULL)
    // we are deleting attribute
    return PyDict_DelItem(((PyObject**)o->g.attr)[ATTRHASH_IDX_VERTEX], k);

  result=PyDict_GetItem(((PyObject**)o->g.attr)[ATTRHASH_IDX_VERTEX], k);
  if (result) {
    /* result is a list, so set the element with index self->idx */
    if (!PyList_Check(result)) {
      PyErr_SetString(igraphmodule_InternalError, "Vertex attribute dict member is not a list");
      return -1;
    }
    /* we actually don't own a reference here to v, so we must increase
     * its reference count, because PyList_SetItem will "steal" a reference!
     * It took me 1.5 hours between London and Manchester to figure it out */
    Py_INCREF(v);
    r=PyList_SetItem(result, self->idx, v);
    if (r == -1) { Py_DECREF(v); }
    return r;
  }

  /* result is NULL, check whether there was an error */
  if (!PyErr_Occurred()) {
    /* no, there wasn't, so we must simply add the attribute */
    igraph_int_t i, n = igraph_vcount(&o->g);
    result = PyList_New(n);
    for (i = 0; i < n; i++) {
      if (i != self->idx) {
        Py_INCREF(Py_None);
        if (PyList_SetItem(result, i, Py_None) == -1) {
          Py_DECREF(Py_None);
          Py_DECREF(result);
          return -1;
        }
      } else {
        /* Same game with the reference count here */
        Py_INCREF(v);
        if (PyList_SetItem(result, i, v) == -1) {
          Py_DECREF(v);
          Py_DECREF(result);
          return -1;
        }
      }
    }
    if (PyDict_SetItem(((PyObject**)o->g.attr)[1], k, result) == -1) {
      Py_DECREF(result);
      return -1;
    }
    Py_DECREF(result);   /* compensating for PyDict_SetItem */
    return 0;
  }

  return -1;
}

/**
 * \ingroup python_interface_vertex
 * Returns the vertex index
 */
PyObject* igraphmodule_Vertex_get_index(igraphmodule_VertexObject* self, void* closure) {
  return igraphmodule_integer_t_to_PyObject(self->idx);
}

/**
 * \ingroup python_interface_vertex
 * Returns the vertex index as an igraph_int_t
 */
igraph_int_t igraphmodule_Vertex_get_index_igraph_integer(igraphmodule_VertexObject* self) {
  return self->idx;
}

/**
 * \ingroup python_interface_vertexseq
 * Returns the graph where the vertex belongs
 */
PyObject* igraphmodule_Vertex_get_graph(igraphmodule_VertexObject* self,
  void* closure) {
  Py_INCREF(self->gref);
  return (PyObject*)self->gref;
}

/**************************************************************************/
/* Implementing proxy method in Vertex that just forward the call to the
 * appropriate Graph method.
 *
 * These methods may also execute a postprocessing function on the result
 * of the Graph method; for instance, this mechanism is used to turn the
 * result of Graph.neighbors() (which is a list of vertex indices) into a
 * list of Vertex objects.
 */

/* Dummy postprocessing function that does nothing. */
static PyObject* _identity(igraphmodule_VertexObject* vertex, PyObject* obj) {
  Py_INCREF(obj);
  return obj;
}

/* Postprocessing function that converts a Python list of integers into a
 * list of edges in-place. */
static PyObject* _convert_to_edge_list(igraphmodule_VertexObject* vertex, PyObject* obj) {
  Py_ssize_t i, n;

  if (!PyList_Check(obj)) {
    PyErr_SetString(PyExc_TypeError, "_convert_to_edge_list expected list of integers");
    return NULL;
  }

  n = PyList_Size(obj);
  for (i = 0; i < n; i++) {
    PyObject* idx = PyList_GetItem(obj, i);
    PyObject* edge;
    igraph_int_t idx_int;

    if (!idx) {
      return NULL;
    }

    if (!PyLong_Check(idx)) {
      PyErr_SetString(PyExc_TypeError, "_convert_to_edge_list expected list of integers");
      return NULL;
    }

    if (igraphmodule_PyObject_to_integer_t(idx, &idx_int)) {
      return NULL;
    }

    edge = igraphmodule_Edge_New(vertex->gref, idx_int);
    if (!edge) {
      return NULL;
    }

    if (PyList_SetItem(obj, i, edge)) {  /* reference to v stolen, reference to idx discarded */
      Py_DECREF(edge);
      return NULL;
    }
  }

  Py_INCREF(obj);

  return obj;
}

/* Postprocessing function that converts a Python list of integers into a
 * list of vertices in-place. */
static PyObject* _convert_to_vertex_list(igraphmodule_VertexObject* vertex, PyObject* obj) {
  Py_ssize_t i, n;

  if (!PyList_Check(obj)) {
    PyErr_SetString(PyExc_TypeError, "_convert_to_vertex_list expected list of integers");
    return NULL;
  }

  n = PyList_Size(obj);
  for (i = 0; i < n; i++) {
    PyObject* idx = PyList_GetItem(obj, i);
    PyObject* v;
    igraph_int_t idx_int;

    if (!idx) {
      return NULL;
    }

    if (!PyLong_Check(idx)) {
      PyErr_SetString(PyExc_TypeError, "_convert_to_vertex_list expected list of integers");
      return NULL;
    }

    if (igraphmodule_PyObject_to_integer_t(idx, &idx_int)) {
      return NULL;
    }

    v = igraphmodule_Vertex_New(vertex->gref, idx_int);
    if (!v) {
      return NULL;
    }

    if (PyList_SetItem(obj, i, v)) {  /* reference to v stolen, reference to idx discarded */
      Py_DECREF(v);
      return NULL;
    }
  }

  Py_INCREF(obj);
  return obj;
}

#define GRAPH_PROXY_METHOD_PP(FUNC, METHODNAME, POSTPROCESS) \
    PyObject* igraphmodule_Vertex_##FUNC(igraphmodule_VertexObject* self, PyObject* args, PyObject* kwds) { \
      PyObject *new_args, *item, *result;                     \
      Py_ssize_t i, num_args = args ? PyTuple_Size(args) + 1 : 1; \
                                                              \
      /* Prepend ourselves to args */                         \
      new_args = PyTuple_New(num_args);                       \
      Py_INCREF(self);                                        \
      PyTuple_SetItem(new_args, 0, (PyObject*)self);          \
      for (i = 1; i < num_args; i++) {                        \
        item = PyTuple_GetItem(args, i - 1);                  \
        Py_INCREF(item);                                      \
        PyTuple_SetItem(new_args, i, item);                   \
      }                                                       \
                                                              \
      /* Get the method instance */                           \
      item = PyObject_GetAttrString((PyObject*)(self->gref), METHODNAME);  \
      if (item == 0) {                                        \
        Py_DECREF(new_args);                                  \
        return 0;                                             \
      }                                                       \
                                                              \
      result = PyObject_Call(item, new_args, kwds);           \
      Py_DECREF(item);                                        \
      Py_DECREF(new_args);                                    \
                                                              \
      /* Optional postprocessing */                           \
      if (result) {                                           \
        PyObject* pp_result = POSTPROCESS(self, result);      \
        Py_DECREF(result);                                    \
        return pp_result;                                     \
      }                                                       \
                                                              \
      return NULL;                                            \
    }

#define GRAPH_PROXY_METHOD(FUNC, METHODNAME) \
        GRAPH_PROXY_METHOD_PP(FUNC, METHODNAME, _identity)

GRAPH_PROXY_METHOD(betweenness, "betweenness");
GRAPH_PROXY_METHOD(closeness, "closeness");
GRAPH_PROXY_METHOD(constraint, "constraint");
GRAPH_PROXY_METHOD(degree, "degree");
GRAPH_PROXY_METHOD(delete, "delete_vertices");
GRAPH_PROXY_METHOD(diversity, "diversity");
GRAPH_PROXY_METHOD(distances, "distances");
GRAPH_PROXY_METHOD(eccentricity, "eccentricity");
GRAPH_PROXY_METHOD(get_shortest_paths, "get_shortest_paths");
GRAPH_PROXY_METHOD_PP(incident, "incident", _convert_to_edge_list);
GRAPH_PROXY_METHOD(indegree, "indegree");
GRAPH_PROXY_METHOD(is_minimal_separator, "is_minimal_separator");
GRAPH_PROXY_METHOD(is_separator, "is_separator");
GRAPH_PROXY_METHOD_PP(neighbors, "neighbors", _convert_to_vertex_list);
GRAPH_PROXY_METHOD(outdegree, "outdegree");
GRAPH_PROXY_METHOD(pagerank, "pagerank");
GRAPH_PROXY_METHOD_PP(predecessors, "predecessors", _convert_to_vertex_list);
GRAPH_PROXY_METHOD(personalized_pagerank, "personalized_pagerank");
GRAPH_PROXY_METHOD(shortest_paths, "shortest_paths");
GRAPH_PROXY_METHOD(strength, "strength");
GRAPH_PROXY_METHOD_PP(successors, "successors", _convert_to_vertex_list);

#undef GRAPH_PROXY_METHOD

#define GRAPH_PROXY_METHOD_SPEC(FUNC, METHODNAME) \
  {METHODNAME, (PyCFunction)igraphmodule_Vertex_##FUNC, METH_VARARGS | METH_KEYWORDS, \
    METHODNAME "(*args, **kwds)\n--\n\n" \
    "Proxy method to L{Graph." METHODNAME "()<igraph._igraph.GraphBase." METHODNAME ">}\n\n"              \
    "This method calls the C{" METHODNAME "()} method of the L{Graph} class " \
    "with this vertex as the first argument, and returns the result.\n\n"\
    "@see: L{Graph." METHODNAME "()<igraph._igraph.GraphBase." METHODNAME ">} for details."}
#define GRAPH_PROXY_METHOD_SPEC_2(FUNC, METHODNAME, METHODNAME_IN_GRAPH) \
  {METHODNAME, (PyCFunction)igraphmodule_Vertex_##FUNC, METH_VARARGS | METH_KEYWORDS, \
    METHODNAME "(*args, **kwds)\n--\n\n" \
    "Proxy method to L{Graph." METHODNAME_IN_GRAPH "()<igraph._igraph.GraphBase." METHODNAME_IN_GRAPH ">}\n\n"              \
    "This method calls the C{" METHODNAME_IN_GRAPH "} method of the L{Graph} class " \
    "with this vertex as the first argument, and returns the result.\n\n"\
    "@see: L{Graph." METHODNAME_IN_GRAPH "()<igraph._igraph.GraphBase." METHODNAME_IN_GRAPH ">} for details."}
#define GRAPH_PROXY_METHOD_SPEC_3(FUNC, METHODNAME) \
  {METHODNAME, (PyCFunction)igraphmodule_Vertex_##FUNC, METH_VARARGS | METH_KEYWORDS, \
    METHODNAME "(*args, **kwds)\n--\n\n" \
    "Proxy method to L{Graph." METHODNAME "()}\n\n"              \
    "This method calls the C{" METHODNAME "()} method of the L{Graph} class " \
    "with this vertex as the first argument, and returns the result.\n\n"\
    "@see: L{Graph." METHODNAME "()} for details."}

/**
 * \ingroup python_interface_vertex
 * Method table for the \c igraph.Vertex object
 */
PyMethodDef igraphmodule_Vertex_methods[] = {
  {"attributes", (PyCFunction)igraphmodule_Vertex_attributes,
    METH_NOARGS,
    "attributes()\n--\n\n"
    "Returns a dict of attribute names and values for the vertex\n"
  },
  {"attribute_names", (PyCFunction)igraphmodule_Vertex_attribute_names,
    METH_NOARGS,
    "attribute_names()\n--\n\n"
    "Returns the list of vertex attribute names\n"
  },
  {"update_attributes", (PyCFunction)igraphmodule_Vertex_update_attributes,
    METH_VARARGS | METH_KEYWORDS,
    "update_attributes(E, **F)\n--\n\n"
    "Updates the attributes of the vertex from dict/iterable E and F.\n\n"
    "If E has a C{keys()} method, it does: C{for k in E: self[k] = E[k]}.\n"
    "If E lacks a C{keys()} method, it does: C{for (k, v) in E: self[k] = v}.\n"
    "In either case, this is followed by: C{for k in F: self[k] = F[k]}.\n\n"
    "This method thus behaves similarly to the C{update()} method of Python\n"
    "dictionaries."
  },
  {"all_edges", (PyCFunction)igraphmodule_Vertex_all_edges, METH_NOARGS,
    "all_edges()\n--\n\n"
    "Proxy method to L{Graph.incident(..., mode=\"all\")<igraph._igraph.GraphBase.incident()>}\n\n" \
    "This method calls the incident() method of the L{Graph} class " \
    "with this vertex as the first argument and \"all\" as the mode " \
    "argument, and returns the result.\n\n"\
    "@see: L{Graph.incident()<igraph._igraph.GraphBase.incident()>} for details."},
  {"in_edges", (PyCFunction)igraphmodule_Vertex_in_edges, METH_NOARGS,
    "in_edges()\n--\n\n"
    "Proxy method to L{Graph.incident(..., mode=\"in\")<igraph._igraph.GraphBase.incident()>}\n\n" \
    "This method calls the incident() method of the L{Graph} class " \
    "with this vertex as the first argument and \"in\" as the mode " \
    "argument, and returns the result.\n\n"\
    "@see: L{Graph.incident()<igraph._igraph.GraphBase.incident()>} for details."},
  {"out_edges", (PyCFunction)igraphmodule_Vertex_out_edges, METH_NOARGS,
    "out_edges()\n--\n\n"
    "Proxy method to L{Graph.incident(..., mode=\"out\")<igraph._igraph.GraphBase.incident()>}\n\n" \
    "This method calls the incident() method of the L{Graph} class " \
    "with this vertex as the first argument and \"out\" as the mode " \
    "argument, and returns the result.\n\n"\
    "@see: L{Graph.incident()<igraph._igraph.GraphBase.incident()>} for details."},
  GRAPH_PROXY_METHOD_SPEC(betweenness, "betweenness"),
  GRAPH_PROXY_METHOD_SPEC(closeness, "closeness"),
  GRAPH_PROXY_METHOD_SPEC(constraint, "constraint"),
  GRAPH_PROXY_METHOD_SPEC(degree, "degree"),
  GRAPH_PROXY_METHOD_SPEC_2(delete, "delete", "delete_vertices"),
  GRAPH_PROXY_METHOD_SPEC(distances, "distances"),
  GRAPH_PROXY_METHOD_SPEC(diversity, "diversity"),
  GRAPH_PROXY_METHOD_SPEC(eccentricity, "eccentricity"),
  GRAPH_PROXY_METHOD_SPEC(get_shortest_paths, "get_shortest_paths"),
  GRAPH_PROXY_METHOD_SPEC(incident, "incident"),
  GRAPH_PROXY_METHOD_SPEC_3(indegree, "indegree"),
  GRAPH_PROXY_METHOD_SPEC(is_minimal_separator, "is_minimal_separator"),
  GRAPH_PROXY_METHOD_SPEC(is_separator, "is_separator"),
  GRAPH_PROXY_METHOD_SPEC(neighbors, "neighbors"),
  GRAPH_PROXY_METHOD_SPEC_3(outdegree, "outdegree"),
  GRAPH_PROXY_METHOD_SPEC_3(pagerank, "pagerank"),
  GRAPH_PROXY_METHOD_SPEC_3(predecessors, "predecessors"),
  GRAPH_PROXY_METHOD_SPEC(personalized_pagerank, "personalized_pagerank"),
  GRAPH_PROXY_METHOD_SPEC(strength, "strength"),
  GRAPH_PROXY_METHOD_SPEC_3(successors, "successors"),
  {NULL}
};

#undef GRAPH_PROXY_METHOD_SPEC
#undef GRAPH_PROXY_METHOD_SPEC_2

/**
 * \ingroup python_interface_vertex
 * Getter/setter table for the \c igraph.Vertex object
 */
PyGetSetDef igraphmodule_Vertex_getseters[] = {
  {"index", (getter)igraphmodule_Vertex_get_index, NULL,
      "Index of the vertex", NULL
  },
  {"graph", (getter)igraphmodule_Vertex_get_graph, NULL,
      "The graph the vertex belongs to", NULL
  },
  {NULL}
};

PyDoc_STRVAR(
  igraphmodule_Vertex_doc,
  "Class representing a single vertex in a graph.\n\n"
  "The vertex is referenced by its index, so if the underlying graph\n"
  "changes, the semantics of the vertex object might change as well\n"
  "(if the vertex indices are altered in the original graph).\n\n"
  "The attributes of the vertex can be accessed by using the vertex\n"
  "as a hash:\n\n"
  "  >>> v[\"color\"] = \"red\"                  #doctest: +SKIP\n"
  "  >>> print(v[\"color\"])                     #doctest: +SKIP\n"
  "  red\n"
  "\n"
  "@ivar index: Index of the vertex\n"
  "@ivar graph: The graph the vertex belongs to\t"
);

int igraphmodule_Vertex_register_type() {
  PyType_Slot slots[] = {
    { Py_tp_init, igraphmodule_Vertex_init },
    { Py_tp_dealloc, igraphmodule_Vertex_dealloc },
    { Py_tp_hash, igraphmodule_Vertex_hash },
    { Py_tp_repr, igraphmodule_Vertex_repr },
    { Py_tp_richcompare, igraphmodule_Vertex_richcompare },
    { Py_tp_methods, igraphmodule_Vertex_methods },
    { Py_tp_getset, igraphmodule_Vertex_getseters },
    { Py_tp_doc, (void*) igraphmodule_Vertex_doc },

    { Py_mp_length, igraphmodule_Vertex_attribute_count },
    { Py_mp_subscript, igraphmodule_Vertex_get_attribute },
    { Py_mp_ass_subscript, igraphmodule_Vertex_set_attribute },

    { 0 }
  };

  PyType_Spec spec = {
    "igraph.Vertex",                            /* name */
    sizeof(igraphmodule_VertexObject),          /* basicsize */
    0,                                          /* itemsize */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,   /* flags */
    slots,                                      /* slots */
  };

  igraphmodule_VertexType = (PyTypeObject*) PyType_FromSpec(&spec);
  return igraphmodule_VertexType == 0;
}
