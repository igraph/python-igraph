/* -*- mode: C -*-  */
/* vim: set ts=2 sw=2 sts=2 et: */

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
#include "convert.h"
#include "edgeobject.h"
#include "error.h"
#include "graphobject.h"
#include "pyhelpers.h"
#include "vertexobject.h"

/**
 * \ingroup python_interface
 * \defgroup python_interface_edge Edge object
 */

PyTypeObject* igraphmodule_EdgeType;

PyObject* igraphmodule_Edge_attributes(igraphmodule_EdgeObject* self, PyObject* _null);

/**
 * \ingroup python_interface_edge
 * \brief Checks whether the given Python object is an edge
 */
int igraphmodule_Edge_Check(PyObject* obj) {
  return obj ? PyObject_IsInstance(obj, (PyObject*)igraphmodule_EdgeType) : 0;
}

/**
 * \ingroup python_interface_edge
 * \brief Checks whether the index in the given edge object is a valid one.
 * \return nonzero if the edge object is valid. Raises an appropriate Python
 *   exception and returns zero if the edge object is invalid.
 */
int igraphmodule_Edge_Validate(PyObject* obj) {
  igraph_integer_t n;
  igraphmodule_EdgeObject *self;
  igraphmodule_GraphObject *graph;

  if (!igraphmodule_Edge_Check(obj)) {
    PyErr_SetString(PyExc_TypeError, "object is not an Edge");
    return 0;
  }

  self = (igraphmodule_EdgeObject*)obj;
  graph = self->gref;

  if (graph == 0) {
    PyErr_SetString(PyExc_ValueError, "Edge object refers to a null graph");
    return 0;
  }

  if (self->idx < 0) {
    PyErr_SetString(PyExc_ValueError, "Edge object refers to a negative edge index");
    return 0;
  }

  n = igraph_ecount(&graph->g);

  if (self->idx >= n) {
    PyErr_SetString(PyExc_ValueError, "Edge object refers to a nonexistent edge");
    return 0;
  }

  return 1;
}

/**
 * \ingroup python_interface_edge
 * \brief Allocates a new Python edge object
 * \param gref weak reference of the \c igraph.Graph being referenced by the edge
 * \param idx the index of the edge
 * 
 * \warning \c igraph references its edges by indices, so if
 * you delete some edges from the graph, the edge indices will
 * change. Since the \c igraph.Edge objects do not follow these
 * changes, your existing edge objects will point to elsewhere
 * (or they might even get invalidated).
 */
PyObject* igraphmodule_Edge_New(igraphmodule_GraphObject *gref, igraph_integer_t idx) {
  return PyObject_CallFunction((PyObject*) igraphmodule_EdgeType, "On", gref, (Py_ssize_t) idx);
}

/**
 * \ingroup python_interface_edge
 * \brief Initialize a new edge object for a given graph
 * \return the initialized PyObject
 */
static int igraphmodule_Edge_init(igraphmodule_EdgeObject *self, PyObject *args, PyObject *kwds) {
  static char *kwlist[] = { "graph", "eid", NULL };
  PyObject *g, *index_o = Py_None;
  igraph_integer_t eid;
  igraph_t *graph;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O!|O", kwlist,
    igraphmodule_GraphType, &g, &index_o)) {
    return -1;
  }

  graph = &((igraphmodule_GraphObject*)g)->g;

  if (igraphmodule_PyObject_to_eid(index_o, &eid, graph)) {
    return -1;
  }

  Py_INCREF(g);
  self->gref = (igraphmodule_GraphObject*)g;
  self->idx = eid;
  self->hash = -1;

  return 0;
}

/**
 * \ingroup python_interface_edge
 * \brief Deallocates a Python representation of a given edge object
 */
static void igraphmodule_Edge_dealloc(igraphmodule_EdgeObject* self) {
  RC_DEALLOC("Edge", self);
  Py_CLEAR(self->gref);
  PY_FREE_AND_DECREF_TYPE(self, igraphmodule_EdgeType);
}

/** \ingroup python_interface_edge
 * \brief Formats an \c igraph.Edge object as a string
 * 
 * \return the formatted textual representation as a \c PyObject
 */
static PyObject* igraphmodule_Edge_repr(igraphmodule_EdgeObject *self) {
  PyObject *s;
  PyObject *attrs;

  attrs = igraphmodule_Edge_attributes(self, NULL);
  if (attrs == 0)
    return NULL;

  s = PyUnicode_FromFormat("igraph.Edge(%R, %" IGRAPH_PRId ", %R)",
      (PyObject*)self->gref, self->idx, attrs);
  Py_DECREF(attrs);

  return s;
}

/** \ingroup python_interface_edge
 * \brief Returns the hash code of the edge
 */
static long igraphmodule_Edge_hash(igraphmodule_EdgeObject* self) {
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

/** \ingroup python_interface_edge
 * \brief Rich comparison of an edge with another
 */
static PyObject* igraphmodule_Edge_richcompare(igraphmodule_EdgeObject *a,
    PyObject *b, int op) {

  igraphmodule_EdgeObject* self = a;
  igraphmodule_EdgeObject* other;

  if (!igraphmodule_Edge_Check(b))
    Py_RETURN_NOTIMPLEMENTED;

  other = (igraphmodule_EdgeObject*)b;

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

/** \ingroup python_interface_edge
 * \brief Returns the number of edge attributes
 */
Py_ssize_t igraphmodule_Edge_attribute_count(igraphmodule_EdgeObject* self) {
  igraphmodule_GraphObject *o = self->gref;
  
  if (!o || !((PyObject**)o->g.attr)[1]) {
    return 0;
  } else {
    return PyDict_Size(((PyObject**)o->g.attr)[1]);
  }
}

/** \ingroup python_interface_edge
 * \brief Returns the list of attribute names
 */
PyObject* igraphmodule_Edge_attribute_names(igraphmodule_EdgeObject* self, PyObject* Py_UNUSED(_null)) {
  return self->gref ? igraphmodule_Graph_edge_attributes(self->gref, NULL) : NULL;
}

/** \ingroup python_interface_edge
 * \brief Returns a dict with attribute names and values
 */
PyObject* igraphmodule_Edge_attributes(igraphmodule_EdgeObject* self, PyObject* Py_UNUSED(_null)) {
  igraphmodule_GraphObject *o = self->gref;
  PyObject *names, *dict;
  Py_ssize_t i, n;

  if (!igraphmodule_Edge_Validate((PyObject*)self)) {
    return NULL;
  }

  dict = PyDict_New();
  if (!dict) {
    return NULL;
  }

  names = igraphmodule_Graph_edge_attributes(o, NULL);
  if (!names) {
    Py_DECREF(dict);
    return NULL;
  }

  n = PyList_Size(names);
  for (i = 0; i < n; i++) {
    PyObject *name = PyList_GetItem(names, i);
    if (name) {
      PyObject *dictit;
      dictit = PyDict_GetItem(((PyObject**)o->g.attr)[ATTRHASH_IDX_EDGE], name);
      if (dictit) {
        PyObject *value = PyList_GetItem(dictit, self->idx);
        if (value) {
          /* no need to Py_INCREF, PyDict_SetItem will do that */
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
 * \ingroup python_interface_edge
 * \brief Updates some attributes of an edge
 * 
 * \param self the edge object
 * \param args positional arguments
 * \param kwds keyword arguments
 */
PyObject* igraphmodule_Edge_update_attributes(PyObject* self, PyObject* args,
    PyObject* kwds) {
  return igraphmodule_Vertex_update_attributes(self, args, kwds);
}

/** \ingroup python_interface_edge
 * \brief Returns the corresponding value to a given attribute of the edge
 * \param self the edge object
 * \param s the attribute name to be queried
 */
PyObject* igraphmodule_Edge_get_attribute(igraphmodule_EdgeObject* self,
                      PyObject* s) {
  igraphmodule_GraphObject *o = self->gref;
  PyObject* result;

  if (!igraphmodule_Edge_Validate((PyObject*)self))
    return 0;

  if (!igraphmodule_attribute_name_check(s))
    return 0;

  result=PyDict_GetItem(((PyObject**)o->g.attr)[2], s);
  if (result) {
    /* result is a list, so get the element with index self->idx */
    if (!PyList_Check(result)) {
      PyErr_SetString(igraphmodule_InternalError, "Edge attribute dict member is not a list");
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

/** \ingroup python_interface_edge
 * \brief Sets the corresponding value of a given attribute of the edge
 * \param self the edge object
 * \param k the attribute name to be set
 * \param v the value to be set
 * \return 0 if everything's ok, -1 in case of error
 */
int igraphmodule_Edge_set_attribute(igraphmodule_EdgeObject* self, PyObject* k, PyObject* v) {
  igraphmodule_GraphObject *o=self->gref;
  PyObject* result;
  int r;
  
  if (!igraphmodule_Edge_Validate((PyObject*)self))
    return -1;

  if (!igraphmodule_attribute_name_check(k))
    return -1;

  if (v==NULL)
    // we are deleting attribute
    return PyDict_DelItem(((PyObject**)o->g.attr)[2], k);
  
  result=PyDict_GetItem(((PyObject**)o->g.attr)[2], k);
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
    igraph_integer_t i, n = igraph_ecount(&o->g);
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
    if (PyDict_SetItem(((PyObject**)o->g.attr)[2], k, result) == -1) {
      Py_DECREF(result); /* TODO: is it needed here? maybe not! */
      return -1;
    }
    Py_DECREF(result); /* compensating for PyDict_SetItem */
    return 0;
  }
  
  return -1;
}

/**
 * \ingroup python_interface_edge
 * Returns the source vertex index of an edge
 */
PyObject* igraphmodule_Edge_get_from(igraphmodule_EdgeObject* self, void* closure) {
  igraphmodule_GraphObject *o = self->gref;
  igraph_integer_t from, to;

  if (!igraphmodule_Edge_Validate((PyObject*)self)) {
    return NULL;
  }

  if (igraph_edge(&o->g, self->idx, &from, &to)) {
    return igraphmodule_handle_igraph_error();
  }

  return igraphmodule_integer_t_to_PyObject(from);
}

/**
 * \ingroup python_interface_edge
 * Returns the source vertex index of an edge
 */
PyObject* igraphmodule_Edge_get_source_vertex(igraphmodule_EdgeObject* self, void* closure) {
  igraphmodule_GraphObject *o = self->gref;
  igraph_integer_t from, to;

  if (!igraphmodule_Edge_Validate((PyObject*)self))
    return NULL;

  if (igraph_edge(&o->g, self->idx, &from, &to)) {
    igraphmodule_handle_igraph_error(); return NULL;
  }

  return igraphmodule_Vertex_New(o, from);
}

/**
 * \ingroup python_interface_edge
 * Returns the target vertex index of an edge
 */
PyObject* igraphmodule_Edge_get_to(igraphmodule_EdgeObject* self, void* closure) {
  igraphmodule_GraphObject *o = self->gref;
  igraph_integer_t from, to;
  
  if (!igraphmodule_Edge_Validate((PyObject*)self)) {
    return NULL;
  }

  if (igraph_edge(&o->g, self->idx, &from, &to)) {
    return igraphmodule_handle_igraph_error();
  }

  return igraphmodule_integer_t_to_PyObject(to);
}

/**
 * \ingroup python_interface_edge
 * Returns the target vertex of an edge
 */
PyObject* igraphmodule_Edge_get_target_vertex(igraphmodule_EdgeObject* self, void* closure) {
  igraphmodule_GraphObject *o = self->gref;
  igraph_integer_t from, to;

  if (!igraphmodule_Edge_Validate((PyObject*)self))
    return NULL;

  if (igraph_edge(&o->g, self->idx, &from, &to)) {
    igraphmodule_handle_igraph_error(); return NULL;
  }

  return igraphmodule_Vertex_New(o, to);
}

/**
 * \ingroup python_interface_edge
 * Returns the edge index
 */
PyObject* igraphmodule_Edge_get_index(igraphmodule_EdgeObject* self, void* closure) {
  return igraphmodule_integer_t_to_PyObject(self->idx);
}

/**
 * \ingroup python_interface_edge
 * Returns the edge index as an igraph_integer_t
 */
igraph_integer_t igraphmodule_Edge_get_index_as_igraph_integer(igraphmodule_EdgeObject* self) {
  return self->idx;
}

/**
 * \ingroup python_interface_edge
 * Returns the source and target vertex index of an edge
 */
PyObject* igraphmodule_Edge_get_tuple(igraphmodule_EdgeObject* self, void* closure) {
  igraphmodule_GraphObject *o = self->gref;
  igraph_integer_t from, to;
  PyObject *from_o, *to_o, *result;
  
  if (!igraphmodule_Edge_Validate((PyObject*)self)) {
    return NULL;
  }

  if (igraph_edge(&o->g, self->idx, &from, &to)) {
    return igraphmodule_handle_igraph_error();
  }

  from_o = igraphmodule_integer_t_to_PyObject(from);
  if (!from_o) {
    return NULL;
  }

  to_o = igraphmodule_integer_t_to_PyObject(to);
  if (!to_o) {
    Py_DECREF(from_o);
    return NULL;
  }

  result = PyTuple_Pack(2, from_o, to_o);
  Py_DECREF(to_o);
  Py_DECREF(from_o);

  return result;
}

/**
 * \ingroup python_interface_edge
 * Returns the source and target vertex of an edge
 */
PyObject* igraphmodule_Edge_get_vertex_tuple(igraphmodule_EdgeObject* self, void* closure) {
  igraphmodule_GraphObject *o = self->gref;
  igraph_integer_t from, to;
  PyObject *from_o, *to_o;

  if (!igraphmodule_Edge_Validate((PyObject*)self))
    return NULL;

  if (igraph_edge(&o->g, self->idx, &from, &to)) {
    igraphmodule_handle_igraph_error(); return NULL;
  }

  from_o = igraphmodule_Vertex_New(o, from);
  if (!from_o) {
    return NULL;
  }

  to_o = igraphmodule_Vertex_New(o, to);
  if (!to_o) {
    Py_DECREF(from_o);
    return NULL;
  }

  return Py_BuildValue("(NN)", from_o, to_o);     /* steals references */
}

/** \ingroup python_interface_edge
 * Returns the graph where the edge belongs
 */
PyObject* igraphmodule_Edge_get_graph(igraphmodule_EdgeObject* self, void* closure) {
  Py_INCREF(self->gref);
  return (PyObject*)self->gref;
}

#define GRAPH_PROXY_METHOD(FUNC, METHODNAME) \
    PyObject* igraphmodule_Edge_##FUNC(igraphmodule_EdgeObject* self, PyObject* args, PyObject* kwds) { \
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
      return result;                                          \
    }

GRAPH_PROXY_METHOD(count_multiple, "count_multiple");
GRAPH_PROXY_METHOD(delete, "delete_edges");
GRAPH_PROXY_METHOD(is_loop, "is_loop");
GRAPH_PROXY_METHOD(is_multiple, "is_multiple");
GRAPH_PROXY_METHOD(is_mutual, "is_mutual");

#undef GRAPH_PROXY_METHOD

#define GRAPH_PROXY_METHOD_SPEC(FUNC, METHODNAME) \
  {METHODNAME, (PyCFunction)igraphmodule_Edge_##FUNC, METH_VARARGS | METH_KEYWORDS, \
    METHODNAME "(*args, **kwds)\n--\n\n" \
    "Proxy method to L{Graph." METHODNAME "()<igraph._igraph.GraphBase." METHODNAME ">}\n\n"              \
    "This method calls the " METHODNAME " method of the L{Graph} class " \
    "with this edge as the first argument, and returns the result.\n\n"\
    "@see: L{Graph." METHODNAME "()<igraph._igraph.GraphBase." METHODNAME ">} for details."}
#define GRAPH_PROXY_METHOD_SPEC_2(FUNC, METHODNAME, METHODNAME_IN_GRAPH) \
  {METHODNAME, (PyCFunction)igraphmodule_Edge_##FUNC, METH_VARARGS | METH_KEYWORDS, \
    METHODNAME "(*args, **kwds)\n--\n\n" \
    "Proxy method to L{Graph." METHODNAME_IN_GRAPH "()<igraph._igraph.GraphBase." METHODNAME_IN_GRAPH ">}\n\n"              \
    "This method calls the " METHODNAME_IN_GRAPH " method of the L{Graph} class " \
    "with this edge as the first argument, and returns the result.\n\n"\
    "@see: L{Graph." METHODNAME_IN_GRAPH "()<igraph._igraph.GraphBase." METHODNAME_IN_GRAPH ">} for details."}

/**
 * \ingroup python_interface_edge
 * Method table for the \c igraph.Edge object
 */
PyMethodDef igraphmodule_Edge_methods[] = {
  {"attributes", (PyCFunction)igraphmodule_Edge_attributes,
    METH_NOARGS,
    "attributes()\n--\n\n"
    "Returns a dict of attribute names and values for the edge\n"
  },
  {"attribute_names", (PyCFunction)igraphmodule_Edge_attribute_names,
    METH_NOARGS,
    "attribute_names()\n--\n\n"
    "Returns the list of edge attribute names\n"
  },
  {"update_attributes", (PyCFunction)igraphmodule_Edge_update_attributes,
    METH_VARARGS | METH_KEYWORDS,
    "update_attributes(E, **F)\n--\n\n"
    "Updates the attributes of the edge from dict/iterable E and F.\n\n"
    "If E has a C{keys()} method, it does: C{for k in E: self[k] = E[k]}.\n"
    "If E lacks a C{keys()} method, it does: C{for (k, v) in E: self[k] = v}.\n"
    "In either case, this is followed by: C{for k in F: self[k] = F[k]}.\n\n"
    "This method thus behaves similarly to the C{update()} method of Python\n"
    "dictionaries."
  },
  GRAPH_PROXY_METHOD_SPEC(count_multiple, "count_multiple"),
  GRAPH_PROXY_METHOD_SPEC_2(delete, "delete", "delete_edges"),
  GRAPH_PROXY_METHOD_SPEC(is_loop, "is_loop"),
  GRAPH_PROXY_METHOD_SPEC(is_multiple, "is_multiple"),
  GRAPH_PROXY_METHOD_SPEC(is_mutual, "is_mutual"),
  {NULL}
};

#undef GRAPH_PROXY_METHOD_SPEC
#undef GRAPH_PROXY_METHOD_SPEC_2

/**
 * \ingroup python_interface_edge
 * Getter/setter table for the \c igraph.Edge object
 */
PyGetSetDef igraphmodule_Edge_getseters[] = {
  {"source", (getter)igraphmodule_Edge_get_from, NULL,
      "Source vertex index of this edge", NULL
  },
  {"source_vertex", (getter)igraphmodule_Edge_get_source_vertex, NULL,
      "Source vertex of this edge", NULL
  },
  {"target", (getter)igraphmodule_Edge_get_to, NULL,
      "Target vertex index of this edge", NULL
  },
  {"target_vertex", (getter)igraphmodule_Edge_get_target_vertex, NULL,
      "Target vertex of this edge", NULL
  },
  {"tuple", (getter)igraphmodule_Edge_get_tuple, NULL,
      "Source and target vertex index of this edge as a tuple", NULL
  },
  {"vertex_tuple", (getter)igraphmodule_Edge_get_vertex_tuple, NULL,
      "Source and target vertex of this edge as a tuple", NULL
  },
  {"index", (getter)igraphmodule_Edge_get_index, NULL,
      "Index of this edge", NULL,
  },
  {"graph", (getter)igraphmodule_Edge_get_graph, NULL,
    "The graph the edge belongs to", NULL,
  },
  {NULL}
};

PyDoc_STRVAR(
  igraphmodule_Edge_doc,
  "Class representing a single edge in a graph.\n\n"
  "The edge is referenced by its index, so if the underlying graph\n"
  "changes, the semantics of the edge object might change as well\n"
  "(if the edge indices are altered in the original graph).\n\n"
  "The attributes of the edge can be accessed by using the edge\n"
  "as a hash:\n\n"
  "  >>> e[\"weight\"] = 2                  #doctest: +SKIP\n"
  "  >>> print(e[\"weight\"])               #doctest: +SKIP\n"
  "  2\n"
);

int igraphmodule_Edge_register_type() {
  PyType_Slot slots[] = {
    { Py_tp_init, igraphmodule_Edge_init },
    { Py_tp_dealloc, igraphmodule_Edge_dealloc },
    { Py_tp_hash, igraphmodule_Edge_hash },
    { Py_tp_repr, igraphmodule_Edge_repr },
    { Py_tp_richcompare, igraphmodule_Edge_richcompare },
    { Py_tp_methods, igraphmodule_Edge_methods },
    { Py_tp_getset, igraphmodule_Edge_getseters },
    { Py_tp_doc, (void*) igraphmodule_Edge_doc },

    { Py_mp_length, igraphmodule_Edge_attribute_count },
    { Py_mp_subscript, igraphmodule_Edge_get_attribute },
    { Py_mp_ass_subscript, igraphmodule_Edge_set_attribute },
  
    { 0 }
  };

  PyType_Spec spec = {
    "igraph.Edge",                              /* name */
    sizeof(igraphmodule_EdgeObject),            /* basicsize */
    0,                                          /* itemsize */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,   /* flags */
    slots,                                      /* slots */
  };

  igraphmodule_EdgeType = (PyTypeObject*) PyType_FromSpec(&spec);
  return igraphmodule_EdgeType == 0;
}
