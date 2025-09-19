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

/************************ Conversion functions *************************/

#include <limits.h>
#include <ctype.h>
#include "attributes.h"
#include "convert.h"
#include "edgeseqobject.h"
#include "edgeobject.h"
#include "error.h"
#include "graphobject.h"
#include "memory.h"
#include "pyhelpers.h"
#include "vertexseqobject.h"
#include "vertexobject.h"

#if defined(_MSC_VER)
  #define strcasecmp _stricmp
#endif

/**
 * \brief Converts a Python long to a C int
 *
 * This is similar to PyLong_AsLong, but it checks for overflow first and
 * throws an exception if necessary. This variant is needed for enum conversions
 * because we assume that enums fit into an int.
 *
 * Note that Python 3.13 also provides a PyLong_AsInt() function, hence we need
 * a different name for this function. The difference is that PyLong_AsInt()
 * needs an extra call to PyErr_Occurred() to disambiguate in case of errors.
 *
 * Returns -1 if there was an error, 0 otherwise.
 */
int PyLong_AsInt_OutArg(PyObject* obj, int* result) {
  long dummy = PyLong_AsLong(obj);
  if (dummy < INT_MIN) {
    PyErr_SetString(PyExc_OverflowError, "long integer too small for conversion to C int");
    return -1;
  }
  if (dummy > INT_MAX) {
    PyErr_SetString(PyExc_OverflowError, "long integer too large for conversion to C int");
    return -1;
  }
  *result = dummy;
  return 0;
}

/**
 * \ingroup python_interface_conversion
 * \brief Converts a Python object to a corresponding igraph enum.
 *
 * The numeric value is returned as an integer that must be converted
 * explicitly to the corresponding igraph enum type. This is to allow one
 * to use the same common conversion routine for multiple enum types.
 *
 * \param o a Python object to be converted
 * \param translation the translation table between strings and the
 *   enum values. Strings are treated as case-insensitive, but it is
 *   assumed that the translation table keys are lowercase. The last
 *   entry of the table must contain NULL values.
 * \param result the result is returned here. The default value must be
 *   passed in before calling this function, since this value is
 *   returned untouched if the given Python object is Py_None.
 * \return 0 if everything is OK, -1 otherwise. An appropriate exception
 *   is raised in this case.
 */
int igraphmodule_PyObject_to_enum(PyObject *o,
  igraphmodule_enum_translation_table_entry_t* table,
  int *result) {

  char *s, *s2;
  int i, best, best_result, best_unique;

  if (o == 0 || o == Py_None)
    return 0;

  if (PyLong_Check(o))
    return PyLong_AsInt_OutArg(o, result);

  s = PyUnicode_CopyAsString(o);
  if (s == 0) {
    PyErr_SetString(PyExc_TypeError, "int, long or string expected");
    return -1;
  }

  /* Convert string to lowercase */
  for (s2 = s; *s2; s2++) {
    *s2 = tolower(*s2);
  }

  /* Search for matches */
  best = 0; best_unique = 0; best_result = -1;
  while (table->name != 0) {
    if (strcmp(s, table->name) == 0) {
      /* Exact match found */
      *result = table->value;
      free(s);
      return 0;
    }

    /* Find length of longest prefix that matches */
    for (i = 0; s[i] == table->name[i]; i++);

    if (i > best) {
      /* Found a better match than before */
      best = i; best_unique = 1; best_result = table->value;
    } else if (i == best) {
      /* Best match is not unique */
      best_unique = 0;
    }

    table++;
  }

  free(s);

  if (best_unique) {
    PY_IGRAPH_DEPRECATED(
      "Partial string matches of enum members are deprecated since igraph 0.9.3; "
      "use strings that identify an enum member unambiguously."
    );

    *result = best_result;
    return 0;
  } else {
    PyErr_SetObject(PyExc_ValueError, o);
    return -1;
  }
}

/**
 * \ingroup python_interface_conversion
 * \brief Converts a Python object to a corresponding igraph enum, strictly.
 *
 * The numeric value is returned as an integer that must be converted
 * explicitly to the corresponding igraph enum type. This is to allow one
 * to use the same common conversion routine for multiple enum types.
 *
 * \param o a Python object to be converted
 * \param translation the translation table between strings and the
 *   enum values. Strings are treated as case-insensitive, but it is
 *   assumed that the translation table keys are lowercase. The last
 *   entry of the table must contain NULL values.
 * \param result the result is returned here. The default value must be
 *   passed in before calling this function, since this value is
 *   returned untouched if the given Python object is Py_None.
 * \return 0 if everything is OK, -1 otherwise. An appropriate exception
 *   is raised in this case.
 */
int igraphmodule_PyObject_to_enum_strict(PyObject *o,
  igraphmodule_enum_translation_table_entry_t* table,
  int *result) {
    char *s, *s2;

    if (o == 0 || o == Py_None) {
      return 0;
    }

    if (PyLong_Check(o)) {
      return PyLong_AsInt_OutArg(o, result);
    }

    s = PyUnicode_CopyAsString(o);
    if (s == 0) {
      PyErr_SetString(PyExc_TypeError, "int, long or string expected");
      return -1;
    }

    /* Convert string to lowercase */
    for (s2 = s; *s2; s2++) {
      *s2 = tolower(*s2);
    }

    /* Search for exact matches */
    while (table->name != 0) {
      if (strcmp(s, table->name) == 0) {
        *result = table->value;
        free(s);
        return 0;
      }
      table++;
    }

    free(s);
    PyErr_SetObject(PyExc_ValueError, o);

    return -1;
}

#define TRANSLATE_ENUM_WITH(translation_table) \
  int result_int = *result, retval; \
  retval = igraphmodule_PyObject_to_enum(o, translation_table, &result_int); \
  if (retval == 0) { \
    *result = result_int; \
  } \
  return retval;

#define TRANSLATE_ENUM_STRICTLY_WITH(translation_table) \
  int result_int = *result, retval; \
  retval = igraphmodule_PyObject_to_enum_strict(o, translation_table, &result_int); \
  if (retval == 0) { \
    *result = result_int; \
  } \
  return retval;

/**
 * \ingroup python_interface_conversion
 * \brief Converts a Python object to an igraph \c igraph_neimode_t
 */
int igraphmodule_PyObject_to_neimode_t(PyObject *o, igraph_neimode_t *result) {
  static igraphmodule_enum_translation_table_entry_t neimode_tt[] = {
        {"in", IGRAPH_IN},
        {"out", IGRAPH_OUT},
        {"all", IGRAPH_ALL},
        {0,0}
    };
  TRANSLATE_ENUM_WITH(neimode_tt);
}

/**
 * \ingroup python_interface_conversion
 * \brief Converts a Python object to an igraph \c igraph_add_weights_t
 */
int igraphmodule_PyObject_to_add_weights_t(PyObject *o,
  igraph_add_weights_t *result) {
  static igraphmodule_enum_translation_table_entry_t add_weights_tt[] = {
        {"true", IGRAPH_ADD_WEIGHTS_YES},
        {"yes", IGRAPH_ADD_WEIGHTS_YES},
        {"false", IGRAPH_ADD_WEIGHTS_NO},
        {"no", IGRAPH_ADD_WEIGHTS_NO},
        {"auto", IGRAPH_ADD_WEIGHTS_IF_PRESENT},
        {"if_present", IGRAPH_ADD_WEIGHTS_IF_PRESENT},
        {0,0}
    };

  if (o == Py_True) {
    *result = IGRAPH_ADD_WEIGHTS_YES;
    return 0;
  }

  if (o == Py_False) {
    *result = IGRAPH_ADD_WEIGHTS_NO;
    return 0;
  }

  TRANSLATE_ENUM_WITH(add_weights_tt);
}

/**
 * \ingroup python_interface_conversion
 * \brief Converts a Python object to an igraph \c igraph_adjacency_t
 */
int igraphmodule_PyObject_to_adjacency_t(PyObject *o,
  igraph_adjacency_t *result) {
  static igraphmodule_enum_translation_table_entry_t adjacency_tt[] = {
        {"directed", IGRAPH_ADJ_DIRECTED},
        {"undirected", IGRAPH_ADJ_UNDIRECTED},
        {"upper", IGRAPH_ADJ_UPPER},
        {"lower", IGRAPH_ADJ_LOWER},
        {"minimum", IGRAPH_ADJ_MIN},
        {"maximum", IGRAPH_ADJ_MAX},
        {"min", IGRAPH_ADJ_MIN},
        {"max", IGRAPH_ADJ_MAX},
        {"plus", IGRAPH_ADJ_PLUS},
        {0,0}
    };
  TRANSLATE_ENUM_WITH(adjacency_tt);
}

int igraphmodule_PyObject_to_attribute_combination_type_t(PyObject* o,
    igraph_attribute_combination_type_t *result) {
  static igraphmodule_enum_translation_table_entry_t attribute_combination_type_tt[] = {
        {"ignore", IGRAPH_ATTRIBUTE_COMBINE_IGNORE},
        {"sum", IGRAPH_ATTRIBUTE_COMBINE_SUM},
        {"prod", IGRAPH_ATTRIBUTE_COMBINE_PROD},
        {"product", IGRAPH_ATTRIBUTE_COMBINE_PROD},
        {"min", IGRAPH_ATTRIBUTE_COMBINE_MIN},
        {"max", IGRAPH_ATTRIBUTE_COMBINE_MAX},
        {"random", IGRAPH_ATTRIBUTE_COMBINE_RANDOM},
        {"first", IGRAPH_ATTRIBUTE_COMBINE_FIRST},
        {"last", IGRAPH_ATTRIBUTE_COMBINE_LAST},
        {"mean", IGRAPH_ATTRIBUTE_COMBINE_MEAN},
        {"median", IGRAPH_ATTRIBUTE_COMBINE_MEDIAN},
        {"concat", IGRAPH_ATTRIBUTE_COMBINE_CONCAT},
        {"concatenate", IGRAPH_ATTRIBUTE_COMBINE_CONCAT},
        {0, 0}
  };

  if (o == Py_None) {
    *result = IGRAPH_ATTRIBUTE_COMBINE_IGNORE;
    return 0;
  }

  if (PyCallable_Check(o)) {
    *result = IGRAPH_ATTRIBUTE_COMBINE_FUNCTION;
    return 0;
  }

  TRANSLATE_ENUM_WITH(attribute_combination_type_tt);
}

int igraphmodule_PyObject_to_eigen_algorithm_t(PyObject *o,
                                       igraph_eigen_algorithm_t *result) {
  static igraphmodule_enum_translation_table_entry_t eigen_algorithm_tt[] =
    {
      {"auto", IGRAPH_EIGEN_AUTO},
      {"lapack", IGRAPH_EIGEN_LAPACK},
      {"arpack", IGRAPH_EIGEN_ARPACK},
      {"comp_auto", IGRAPH_EIGEN_COMP_AUTO},
      {"comp_lapack", IGRAPH_EIGEN_COMP_LAPACK},
      {"comp_arpack", IGRAPH_EIGEN_COMP_ARPACK},
      {0,0}
    };

  if (o == Py_None) {
    *result = IGRAPH_EIGEN_ARPACK;
    return 0;
  }

  TRANSLATE_ENUM_WITH(eigen_algorithm_tt);
}

int igraphmodule_PyObject_to_eigen_which_t(PyObject *o,
                                           igraph_eigen_which_t *result) {
  PyObject *key, *value;
  Py_ssize_t pos = 0;
  igraph_eigen_which_t *w = result;

  static igraphmodule_enum_translation_table_entry_t
    eigen_which_position_tt[] = {
    { "LM", IGRAPH_EIGEN_LM},
    { "SM", IGRAPH_EIGEN_SM},
    { "LA", IGRAPH_EIGEN_LA},
    { "SA", IGRAPH_EIGEN_SA},
    { "BE", IGRAPH_EIGEN_BE},
    { "LR", IGRAPH_EIGEN_LR},
    { "SR", IGRAPH_EIGEN_SR},
    { "LI", IGRAPH_EIGEN_LI},
    { "SI", IGRAPH_EIGEN_SI},
    { "ALL", IGRAPH_EIGEN_ALL},
    { "INTERVAL", IGRAPH_EIGEN_INTERVAL},
    { "SELECT", IGRAPH_EIGEN_SELECT}
  };

  static igraphmodule_enum_translation_table_entry_t
    lapack_dgeevc_balance_tt[] = {
    { "none", IGRAPH_LAPACK_DGEEVX_BALANCE_NONE },
    { "perm", IGRAPH_LAPACK_DGEEVX_BALANCE_PERM },
    { "scale", IGRAPH_LAPACK_DGEEVX_BALANCE_SCALE },
    { "both", IGRAPH_LAPACK_DGEEVX_BALANCE_BOTH }
  };

  w->pos = IGRAPH_EIGEN_LM;
  w->howmany = 1;
  w->il = w->iu = -1;
  w->vl = -IGRAPH_INFINITY;
  w->vu = IGRAPH_INFINITY;
  w->vestimate = 0;
  w->balance = IGRAPH_LAPACK_DGEEVX_BALANCE_NONE;

  if (o != Py_None && !PyDict_Check(o)) {
    PyErr_SetString(PyExc_TypeError, "Python dictionary expected");
    return -1;
  }

  if (o != Py_None) {
    while (PyDict_Next(o, &pos, &key, &value)) {
      char *kv;
      PyObject *temp_bytes;
      if (!PyUnicode_Check(key)) {
        PyErr_SetString(PyExc_TypeError, "Dict key must be string");
        return -1;
      }
      temp_bytes = PyUnicode_AsEncodedString(key, "ascii", "ignore");
      if (temp_bytes == 0) {
        /* Exception set already by PyUnicode_AsEncodedString */
        return -1;
      }
      kv = PyBytes_AsString(temp_bytes);
      if (kv == 0) {
        /* Exception set already by PyBytes_AsString */
        return -1;
      }
      kv = strdup(kv);
      if (kv == 0) {
        PyErr_SetString(PyExc_MemoryError, "Not enough memory");
      }
      Py_DECREF(temp_bytes);
      if (!strcasecmp(kv, "pos")) {
        int w_pos_int = w->pos;
        if (igraphmodule_PyObject_to_enum(value, eigen_which_position_tt, &w_pos_int)) {
          return -1;
        }
        w->pos = w_pos_int;
      } else if (!strcasecmp(kv, "howmany")) {
        if (PyLong_AsInt_OutArg(value, &w->howmany)) {
          return -1;
        }
      } else if (!strcasecmp(kv, "il")) {
        if (PyLong_AsInt_OutArg(value, &w->il)) {
          return -1;
        }
      } else if (!strcasecmp(kv, "iu")) {
        if (PyLong_AsInt_OutArg(value, &w->iu)) {
          return -1;
        }
      } else if (!strcasecmp(kv, "vl")) {
        w->vl = PyFloat_AsDouble(value);
      } else if (!strcasecmp(kv, "vu")) {
        w->vu = PyFloat_AsDouble(value);
      } else if (!strcasecmp(kv, "vestimate")) {
        if (PyLong_AsInt_OutArg(value, &w->vestimate)) {
          return -1;
        }
      } else if (!strcasecmp(kv, "balance")) {
        int w_balance_as_int = w->balance;
        if (igraphmodule_PyObject_to_enum(value, lapack_dgeevc_balance_tt, &w_balance_as_int)) {
          return -1;
        }
        w->balance = w_balance_as_int;
      } else {
        PyErr_SetString(PyExc_TypeError, "Unknown eigen parameter");
        if (kv != 0) {
          free(kv);
        }
        return -1;
      }
      if (kv != 0) {
        free(kv);
      }
    }
  }
  return 0;
}

/**
 * \ingroup python_interface_conversion
 * \brief Converts a Python object to an igraph \c igraph_barabasi_algorithm_t
 */
int igraphmodule_PyObject_to_barabasi_algorithm_t(PyObject *o,
  igraph_barabasi_algorithm_t *result) {
  static igraphmodule_enum_translation_table_entry_t barabasi_algorithm_tt[] = {
        {"bag", IGRAPH_BARABASI_BAG},
        {"psumtree", IGRAPH_BARABASI_PSUMTREE},
        {"psumtree_multiple", IGRAPH_BARABASI_PSUMTREE_MULTIPLE},
        {0,0}
    };
  TRANSLATE_ENUM_WITH(barabasi_algorithm_tt);
}

/**
 * \ingroup python_interface_conversion
 * \brief Converts a Python object to an igraph \c igraph_connectedness_t
 */
int igraphmodule_PyObject_to_connectedness_t(PyObject *o,
  igraph_connectedness_t *result) {
  static igraphmodule_enum_translation_table_entry_t connectedness_tt[] = {
        {"weak", IGRAPH_WEAK},
        {"strong", IGRAPH_STRONG},
        {0,0}
    };
  TRANSLATE_ENUM_WITH(connectedness_tt);
}

/**
 * \ingroup python_interface_conversion
 * \brief Converts a Python object to an igraph \c igraph_vconn_nei_t
 */
int igraphmodule_PyObject_to_vconn_nei_t(PyObject *o,
  igraph_vconn_nei_t *result) {
  static igraphmodule_enum_translation_table_entry_t vconn_nei_tt[] = {
        {"error", IGRAPH_VCONN_NEI_ERROR},
        {"negative", IGRAPH_VCONN_NEI_NEGATIVE},
        {"number_of_nodes", IGRAPH_VCONN_NEI_NUMBER_OF_NODES},
        {"nodes", IGRAPH_VCONN_NEI_NUMBER_OF_NODES},
        {"ignore", IGRAPH_VCONN_NEI_IGNORE},
        {0,0}
    };
  TRANSLATE_ENUM_WITH(vconn_nei_tt);
}

/**
 * \ingroup python_interface_conversion
 * \brief Converts a Python object to an igraph \c igraph_bliss_sh_t
 */
int igraphmodule_PyObject_to_bliss_sh_t(PyObject *o,
  igraph_bliss_sh_t *result) {
  static igraphmodule_enum_translation_table_entry_t bliss_sh_tt[] = {
        {"f", IGRAPH_BLISS_F},
        {"fl", IGRAPH_BLISS_FL},
        {"fs", IGRAPH_BLISS_FS},
        {"fm", IGRAPH_BLISS_FM},
        {"flm", IGRAPH_BLISS_FLM},
        {"fsm", IGRAPH_BLISS_FSM},
        {0,0}
    };
  TRANSLATE_ENUM_WITH(bliss_sh_tt);
}

/**
 * \ingroup python_interface_conversion
 * \brief Converts a Python object to an igraph \c igraph_chung_lu_t
 */
int igraphmodule_PyObject_to_chung_lu_t(PyObject *o, igraph_chung_lu_t *result) {
  static igraphmodule_enum_translation_table_entry_t chung_lu_tt[] = {
        {"original", IGRAPH_CHUNG_LU_ORIGINAL},
        {"maxent", IGRAPH_CHUNG_LU_MAXENT},
        {"nr", IGRAPH_CHUNG_LU_NR},
        {0,0}
    };
  TRANSLATE_ENUM_WITH(chung_lu_tt);
}

/**
 * \ingroup python_interface_conversion
 * \brief Converts a Python object to an igraph \c igraph_coloring_greedy_t
 */
int igraphmodule_PyObject_to_coloring_greedy_t(PyObject *o, igraph_coloring_greedy_t *result) {
  static igraphmodule_enum_translation_table_entry_t coloring_greedy_tt[] = {
        {"colored_neighbors", IGRAPH_COLORING_GREEDY_COLORED_NEIGHBORS},
        {"dsatur", IGRAPH_COLORING_GREEDY_DSATUR},
        {0,0}
    };
  TRANSLATE_ENUM_WITH(coloring_greedy_tt);
}

/**
 * \ingroup python_interface_conversion
 * \brief Converts a Python object to an igraph \c igraph_community_comparison_t
 */
int igraphmodule_PyObject_to_community_comparison_t(PyObject *o,
                  igraph_community_comparison_t *result) {
  static igraphmodule_enum_translation_table_entry_t commcmp_tt[] = {
        {"vi", IGRAPH_COMMCMP_VI},
        {"meila", IGRAPH_COMMCMP_VI},
        {"nmi", IGRAPH_COMMCMP_NMI},
        {"danon", IGRAPH_COMMCMP_NMI},
        {"split-join", IGRAPH_COMMCMP_SPLIT_JOIN},
        {"split_join", IGRAPH_COMMCMP_SPLIT_JOIN},
        {"rand", IGRAPH_COMMCMP_RAND},
        {"adjusted_rand", IGRAPH_COMMCMP_ADJUSTED_RAND},
        {0,0}
    };
  TRANSLATE_ENUM_WITH(commcmp_tt);
}

/**
 * \ingroup python_interface_conversion
 * \brief Converts a Python object to an igraph \c igraph_degseq_t
 */
int igraphmodule_PyObject_to_degseq_t(PyObject *o,
  igraph_degseq_t *result) {
  static igraphmodule_enum_translation_table_entry_t degseq_tt[] = {
        /* legacy names before 0.10 */
        {"simple", IGRAPH_DEGSEQ_CONFIGURATION},
        {"no_multiple", IGRAPH_DEGSEQ_FAST_HEUR_SIMPLE},
        {"viger-latapy", IGRAPH_DEGSEQ_VL},
        /* up-to-date names as of igraph 0.10 */
        {"configuration", IGRAPH_DEGSEQ_CONFIGURATION},
        {"vl", IGRAPH_DEGSEQ_VL},
        {"viger_latapy", IGRAPH_DEGSEQ_VL},
        {"fast_heur_simple", IGRAPH_DEGSEQ_FAST_HEUR_SIMPLE},
        {"configuration_simple", IGRAPH_DEGSEQ_CONFIGURATION_SIMPLE},
        {"edge_switching_simple", IGRAPH_DEGSEQ_EDGE_SWITCHING_SIMPLE},
        {0,0}
    };
  TRANSLATE_ENUM_WITH(degseq_tt);
}

/**
 * \ingroup python_interface_conversion
 * \brief Converts a Python object to an igraph \c igraph_fas_algorithm_t
 */
int igraphmodule_PyObject_to_fas_algorithm_t(PyObject *o,
  igraph_fas_algorithm_t *result) {
  static igraphmodule_enum_translation_table_entry_t fas_algorithm_tt[] = {
        {"approx_eades", IGRAPH_FAS_APPROX_EADES},
        {"eades", IGRAPH_FAS_APPROX_EADES},
        {"exact", IGRAPH_FAS_EXACT_IP},
        {"exact_ip", IGRAPH_FAS_EXACT_IP},
        {"ip", IGRAPH_FAS_EXACT_IP},
        {"ip_ti", IGRAPH_FAS_EXACT_IP_TI},
        {"ip_cg", IGRAPH_FAS_EXACT_IP_CG},
        {0,0}
    };
  TRANSLATE_ENUM_WITH(fas_algorithm_tt);
}

/**
 * \ingroup python_interface_conversion
 * \brief Converts a Python object to an igraph \c igraph_fvs_algorithm_t
 */
int igraphmodule_PyObject_to_fvs_algorithm_t(PyObject *o,
  igraph_fvs_algorithm_t *result) {
  static igraphmodule_enum_translation_table_entry_t fvs_algorithm_tt[] = {
        {"ip", IGRAPH_FVS_EXACT_IP},
        {0,0}
    };
  TRANSLATE_ENUM_WITH(fvs_algorithm_tt);
}

/**
 * \ingroup python_interface_conversion
 * \brief Converts a Python object to an igraph \c igraph_get_adjacency_t
 */
int igraphmodule_PyObject_to_get_adjacency_t(PyObject *o,
  igraph_get_adjacency_t *result) {
  static igraphmodule_enum_translation_table_entry_t get_adjacency_tt[] = {
        {"lower", IGRAPH_GET_ADJACENCY_LOWER},
        {"upper", IGRAPH_GET_ADJACENCY_UPPER},
        {"both", IGRAPH_GET_ADJACENCY_BOTH},
        {0,0}
    };
  TRANSLATE_ENUM_WITH(get_adjacency_tt);
}

/**
 * \brief Converts a Python object to an igraph \c igraph_laplacian_normalization_t
 */
int igraphmodule_PyObject_to_laplacian_normalization_t(
  PyObject *o, igraph_laplacian_normalization_t *result
) {
  static igraphmodule_enum_translation_table_entry_t laplacian_normalization_tt[] = {
        {"unnormalized", IGRAPH_LAPLACIAN_UNNORMALIZED},
        {"symmetric", IGRAPH_LAPLACIAN_SYMMETRIC},
        {"left", IGRAPH_LAPLACIAN_LEFT},
        {"right", IGRAPH_LAPLACIAN_RIGHT},
        {0,0}
    };

  if (o == Py_True) {
    *result = IGRAPH_LAPLACIAN_SYMMETRIC;
    return 0;
  }

  if (o == Py_False) {
    *result = IGRAPH_LAPLACIAN_UNNORMALIZED;
    return 0;
  }

  TRANSLATE_ENUM_WITH(laplacian_normalization_tt);
}

/**
 * \brief Converts a Python object to an igraph \c igraph_layout_grid_t
 */
int igraphmodule_PyObject_to_layout_grid_t(PyObject *o, igraph_layout_grid_t *result) {
  static igraphmodule_enum_translation_table_entry_t layout_grid_tt[] = {
    {"auto",   IGRAPH_LAYOUT_AUTOGRID},
    {"grid",   IGRAPH_LAYOUT_GRID},
    {"nogrid", IGRAPH_LAYOUT_NOGRID},
    {0,0}
  };

  if (o == Py_True) {
    *result = IGRAPH_LAYOUT_GRID;
    return 0;
  }

  if (o == Py_False) {
    *result = IGRAPH_LAYOUT_NOGRID;
    return 0;
  }

  TRANSLATE_ENUM_WITH(layout_grid_tt);
}

/**
 * \brief Converts a Python object to an igraph \c igraph_loops_t
 */
int igraphmodule_PyObject_to_loops_t(PyObject *o, igraph_loops_t *result) {
  static igraphmodule_enum_translation_table_entry_t loops_tt[] = {
    {"ignore", IGRAPH_NO_LOOPS},
    {"once",   IGRAPH_LOOPS_ONCE},
    {"twice",  IGRAPH_LOOPS_TWICE},
    {0,0}
  };

  if (o == Py_True) {
    *result = IGRAPH_LOOPS_TWICE;
    return 0;
  }

  if (o == Py_False) {
    *result = IGRAPH_NO_LOOPS;
    return 0;
  }

  TRANSLATE_ENUM_WITH(loops_tt);
}

/**
 * \brief Converts a Python object to an igraph \c igraph_lpa_variant_t
 */
int igraphmodule_PyObject_to_lpa_variant_t(PyObject *o, igraph_lpa_variant_t *result) {
  static igraphmodule_enum_translation_table_entry_t lpa_variant_tt[] = {
    {"dominance", IGRAPH_LPA_DOMINANCE},
    {"retention", IGRAPH_LPA_RETENTION},
    {"fast", IGRAPH_LPA_FAST},
    {0,0}
  };

  TRANSLATE_ENUM_WITH(lpa_variant_tt);
}

/**
 * \brief Converts a Python object to an igraph \c igraph_mst_algorithm_t
 */
int igraphmodule_PyObject_to_mst_algorithm_t(PyObject *o, igraph_mst_algorithm_t *result) {
  static igraphmodule_enum_translation_table_entry_t mst_algorithm_tt[] = {
    {"auto", IGRAPH_MST_AUTOMATIC},
    {"automatic", IGRAPH_MST_AUTOMATIC},
    {"unweighted", IGRAPH_MST_UNWEIGHTED},
    {"prim", IGRAPH_MST_PRIM},
    {"kruskal", IGRAPH_MST_KRUSKAL},
    {0,0}
  };

  TRANSLATE_ENUM_WITH(mst_algorithm_tt);
}

/**
 * \ingroup python_interface_conversion
 * \brief Converts a Python object to an igraph \c igraph_random_walk_stuck_t
 */
int igraphmodule_PyObject_to_random_walk_stuck_t(PyObject *o,
  igraph_random_walk_stuck_t *result) {
  static igraphmodule_enum_translation_table_entry_t random_walk_stuck_tt[] = {
        {"return", IGRAPH_RANDOM_WALK_STUCK_RETURN},
        {"error", IGRAPH_RANDOM_WALK_STUCK_ERROR},
        {0,0}
  };
  TRANSLATE_ENUM_WITH(random_walk_stuck_tt);
}

/**
 * \brief Converts a Python object to an igraph \c igraph_reciprocity_t
 */
int igraphmodule_PyObject_to_reciprocity_t(PyObject *o, igraph_reciprocity_t *result) {
  static igraphmodule_enum_translation_table_entry_t reciprocity_tt[] = {
    {"default", IGRAPH_RECIPROCITY_DEFAULT},
    {"ratio", IGRAPH_RECIPROCITY_RATIO},
    {0,0}
  };
  TRANSLATE_ENUM_WITH(reciprocity_tt);
}

/**
 * \brief Converts a Python object to an igraph \c igraphmodule_shortest_path_algorithm_t
 */
int igraphmodule_PyObject_to_shortest_path_algorithm_t(PyObject *o, igraphmodule_shortest_path_algorithm_t *result) {
  static igraphmodule_enum_translation_table_entry_t shortest_path_algorithm_tt[] = {
    {"auto", IGRAPHMODULE_SHORTEST_PATH_ALGORITHM_AUTO},
    {"dijkstra", IGRAPHMODULE_SHORTEST_PATH_ALGORITHM_DIJKSTRA},
    {"bellman_ford", IGRAPHMODULE_SHORTEST_PATH_ALGORITHM_BELLMAN_FORD},
    {"johnson", IGRAPHMODULE_SHORTEST_PATH_ALGORITHM_JOHNSON},
    {0,0}
  };
  TRANSLATE_ENUM_WITH(shortest_path_algorithm_tt);
}

/**
 * \brief Converts a Python object to an igraph \c igraph_spinglass_implementation_t
 */
int igraphmodule_PyObject_to_spinglass_implementation_t(PyObject *o, igraph_spinglass_implementation_t *result) {
  static igraphmodule_enum_translation_table_entry_t spinglass_implementation_tt[] = {
    {"original", IGRAPH_SPINCOMM_IMP_ORIG},
    {"negative", IGRAPH_SPINCOMM_IMP_NEG},
    {0,0}
  };
  TRANSLATE_ENUM_WITH(spinglass_implementation_tt);
}

/**
 * \brief Converts a Python object to an igraph \c igraph_spincomm_update_t
 */
int igraphmodule_PyObject_to_spincomm_update_t(PyObject *o, igraph_spincomm_update_t *result) {
  static igraphmodule_enum_translation_table_entry_t spincomm_update_tt[] = {
    {"simple", IGRAPH_SPINCOMM_UPDATE_SIMPLE},
    {"config", IGRAPH_SPINCOMM_UPDATE_CONFIG},
    {0,0}
  };
  TRANSLATE_ENUM_WITH(spincomm_update_tt);
}

/**
 * \ingroup python_interface_conversion
 * \brief Converts a Python object to an igraph \c igraph_star_mode_t
 */
int igraphmodule_PyObject_to_star_mode_t(PyObject *o,
  igraph_star_mode_t *result) {
  static igraphmodule_enum_translation_table_entry_t star_mode_tt[] = {
        {"in", IGRAPH_STAR_IN},
        {"out", IGRAPH_STAR_OUT},
        {"mutual", IGRAPH_STAR_MUTUAL},
        {"undirected", IGRAPH_STAR_UNDIRECTED},
        {0,0}
    };
  TRANSLATE_ENUM_WITH(star_mode_tt);
}

/**
 * \ingroup python_interface_conversion
 * \brief Converts a Python object to an igraph \c igraph_subgraph_implementation_t
 */
int igraphmodule_PyObject_to_subgraph_implementation_t(PyObject *o,
  igraph_subgraph_implementation_t *result) {
  static igraphmodule_enum_translation_table_entry_t subgraph_impl_tt[] = {
        {"auto", IGRAPH_SUBGRAPH_AUTO},
        {"copy_and_delete", IGRAPH_SUBGRAPH_COPY_AND_DELETE},
        {"old", IGRAPH_SUBGRAPH_COPY_AND_DELETE},
        {"create_from_scratch", IGRAPH_SUBGRAPH_CREATE_FROM_SCRATCH},
        {"new", IGRAPH_SUBGRAPH_CREATE_FROM_SCRATCH},
        {0,0}
    };
  TRANSLATE_ENUM_WITH(subgraph_impl_tt);
}

/**
 * \ingroup python_interface_conversion
 * \brief Converts a Python object to an igraph \c igraph_to_directed_t
 */
int igraphmodule_PyObject_to_to_directed_t(PyObject *o,
  igraph_to_directed_t *result) {
  static igraphmodule_enum_translation_table_entry_t to_directed_tt[] = {
        {"acyclic",   IGRAPH_TO_DIRECTED_ACYCLIC},
        {"arbitrary", IGRAPH_TO_DIRECTED_ARBITRARY},
        {"mutual",    IGRAPH_TO_DIRECTED_MUTUAL},
        {"random",    IGRAPH_TO_DIRECTED_RANDOM},
        {0,0}
  };

  if (o == Py_True) {
    *result = IGRAPH_TO_DIRECTED_MUTUAL;
    return 0;
  }

  if (o == Py_False) {
    *result = IGRAPH_TO_DIRECTED_ARBITRARY;
    return 0;
  }

  TRANSLATE_ENUM_WITH(to_directed_tt);
}

/**
 * \ingroup python_interface_conversion
 * \brief Converts a Python object to an igraph \c igraph_to_undirected_t
 */
int igraphmodule_PyObject_to_to_undirected_t(PyObject *o,
  igraph_to_undirected_t *result) {
  static igraphmodule_enum_translation_table_entry_t to_undirected_tt[] = {
        {"each",     IGRAPH_TO_UNDIRECTED_EACH},
        {"collapse", IGRAPH_TO_UNDIRECTED_COLLAPSE},
        {"mutual",   IGRAPH_TO_UNDIRECTED_MUTUAL},
        {0,0}
  };

  if (o == Py_True) {
    *result = IGRAPH_TO_UNDIRECTED_COLLAPSE;
    return 0;
  }

  if (o == Py_False) {
    *result = IGRAPH_TO_UNDIRECTED_EACH;
    return 0;
  }

  TRANSLATE_ENUM_WITH(to_undirected_tt);
}

/**
 * \ingroup python_interface_conversion
 * \brief Converts a Python object to an \c igraph_transitivity_mode_t
 */
int igraphmodule_PyObject_to_transitivity_mode_t(PyObject *o,
  igraph_transitivity_mode_t *result) {
  static igraphmodule_enum_translation_table_entry_t transitivity_mode_tt[] = {
        {"zero", IGRAPH_TRANSITIVITY_ZERO},
        {"0", IGRAPH_TRANSITIVITY_ZERO},
        {"nan", IGRAPH_TRANSITIVITY_NAN},
        {0,0}
    };

  TRANSLATE_ENUM_WITH(transitivity_mode_tt);
}

/**
 * \ingroup python_interface_conversion
 * \brief Converts a Python object to an igraph \c igraph_tree_mode_t
 */
int igraphmodule_PyObject_to_tree_mode_t(PyObject *o,
  igraph_tree_mode_t *result) {
  static igraphmodule_enum_translation_table_entry_t tree_mode_tt[] = {
        {"in", IGRAPH_TREE_IN},
        {"out", IGRAPH_TREE_OUT},
        {"all", IGRAPH_TREE_UNDIRECTED},
        {"undirected", IGRAPH_TREE_UNDIRECTED},
        {"tree_in", IGRAPH_TREE_IN},
        {"tree_out", IGRAPH_TREE_OUT},
        {"tree_all", IGRAPH_TREE_UNDIRECTED},
        {0,0}
    };

  TRANSLATE_ENUM_WITH(tree_mode_tt);
}

/**
 * \brief Extracts a pointer to the internal \c igraph_t from a graph object
 *
 * Raises suitable Python exceptions when needed.
 *
 * \param object the Python object to be converted. If it is Py_None, the
 *               result pointer is untouched (so it should be null by default).
 * \param result the pointer is stored here
 *
 * \return 0 if everything was OK, 1 otherwise
 */
int igraphmodule_PyObject_to_igraph_t(PyObject *o, igraph_t **result) {
  if (o == Py_None)
    return 0;

  if (!PyObject_TypeCheck(o, igraphmodule_GraphType)) {
    PyErr_Format(PyExc_TypeError, "expected graph object, got %R", Py_TYPE(o));
    return 1;
  }

  *result = &((igraphmodule_GraphObject*)o)->g;
  return 0;
}

/**
 * \brief Converts a PyLong to an igraph \c igraph_int_t
 *
 * Raises suitable Python exceptions when needed.
 *
 * This function differs from the next one because it is less generic,
 * i.e. the Python object has to be a PyLong
 *
 * \param object the PyLong to be converted
 * \param v the result is stored here
 * \return 0 if everything was OK, 1 otherwise
 */
int PyLong_to_integer_t(PyObject* obj, igraph_int_t* v) {
  if (IGRAPH_INTEGER_SIZE == 64) {
    /* here the assumption is that sizeof(long long) == 64 bits; anyhow, this
     * is the widest integer type that we can convert a PyLong to so we cannot
     * do any better than this */
    long long int dummy = PyLong_AsLongLong(obj);
    if (PyErr_Occurred()) {
      return 1;
    }
    *v = dummy;
  } else {
    /* this is either 32-bit igraph, or some weird, officially not-yet-supported
     * igraph flavour. Let's try to be on the safe side and assume 32-bit. long
     * ints are at least 32 bits so we will fit, otherwise Python will raise
     * an OverflowError on its own */
    long int dummy = PyLong_AsLong(obj);
    if (PyErr_Occurred()) {
      return 1;
    }
    *v = dummy;
  }
  return 0;
}

/**
 * \brief Converts a Python object to an igraph \c igraph_int_t
 *
 * Raises suitable Python exceptions when needed.
 *
 * \param object the Python object to be converted
 * \param v the result is stored here
 * \return 0 if everything was OK, 1 otherwise
 */
int igraphmodule_PyObject_to_integer_t(PyObject *object, igraph_int_t *v) {
  int retval;
  igraph_int_t num;

  if (object == NULL) {
  } else if (PyLong_Check(object)) {
    retval = PyLong_to_integer_t(object, &num);
    if (retval)
      return retval;
    *v = num;
    return 0;
  } else if (PyNumber_Check(object)) {
    /* try to recast as PyLong */
    PyObject *i = PyNumber_Long(object);
    if (i == NULL)
      return 1;
    /* as above, plus decrement the reference for the temp variable */
    retval = PyLong_to_integer_t(i, &num);
    Py_DECREF(i);
    if (retval)
      return retval;
    *v = num;
    return 0;
  }
  PyErr_BadArgument();
  return 1;
}

/**
 * \brief Converts a Python object to an igraph \c igraph_int_t when it is
 * used as a limit on the number of results for some function.
 * 
 * This is different from \ref igraphmodule_PyObject_to_integer_t such that it
 * converts None and positive infinity to \c IGRAPH_UNLIMITED, and it does not
 * accept negative values.
 *
 * Raises suitable Python exceptions when needed.
 *
 * \param object the Python object to be converted
 * \param v the result is stored here
 * \return 0 if everything was OK, 1 otherwise
 */
int igraphmodule_PyObject_to_max_results_t(PyObject *object, igraph_int_t *v) {
  int retval;
  igraph_int_t num;

  if (object != NULL) {
    if (object == Py_None) {
      *v = IGRAPH_UNLIMITED;
      return 0;
    }

    if (PyNumber_Check(object)) {
      PyObject *flt = PyNumber_Float(object);
      if (flt == NULL) {
        return 1;
      }

      if (PyFloat_AsDouble(flt) == IGRAPH_INFINITY) {
        Py_DECREF(flt);
        *v = IGRAPH_UNLIMITED;
        return 0;
      }

      Py_DECREF(flt);
    }
  }

  retval = igraphmodule_PyObject_to_integer_t(object, &num);
  if (retval) {
    return retval;
  }

  if (num < 0) {
    PyErr_SetString(PyExc_ValueError, "expected non-negative integer, None or infinity");
    return 1;
  }

  *v = num;
  return 0;
}

/**
 * \brief Converts a Python object to an igraph \c igraph_real_t
 *
 * Raises suitable Python exceptions when needed.
 *
 * \param object the Python object to be converted; \c NULL is accepted but
 *        will keep the input value of v
 * \param v the result is returned here
 * \return 0 if everything was OK, 1 otherwise
 */
int igraphmodule_PyObject_to_real_t(PyObject *object, igraph_real_t *v) {
  igraph_real_t value;

  if (object == NULL) {
    return 0;
  } else if (PyLong_Check(object)) {
    value = PyLong_AsDouble(object);
  } else if (PyFloat_Check(object)) {
    value = PyFloat_AsDouble(object);
  } else if (PyNumber_Check(object)) {
    PyObject *i = PyNumber_Float(object);
    if (i == NULL) {
      return 1;
    }
    value = PyFloat_AsDouble(i);
    Py_DECREF(i);
  } else {
    PyErr_BadArgument();
    return 1;
  }

  if (PyErr_Occurred()) {
    return 1;
  } else {
    *v = value;
    return 0;
  }
}

/**
 * \ingroup python_interface_conversion
 * \brief Converts a Python object to an igraph \c igraph_vector_t
 * The incoming \c igraph_vector_t should be uninitialized. Raises suitable
 * Python exceptions when needed.
 *
 * \param list the Python list to be converted
 * \param v the \c igraph_vector_t containing the result
 * \param need_non_negative if true, checks whether all elements are non-negative
 * \return 0 if everything was OK, 1 otherwise
 */
int igraphmodule_PyObject_to_vector_t(PyObject *list, igraph_vector_t *v, igraph_bool_t need_non_negative) {
  PyObject *item, *it;
  Py_ssize_t size_hint;
  int ok;
  igraph_int_t number;

  if (PyBaseString_Check(list)) {
    /* It is highly unlikely that a string (although it is a sequence) will
     * provide us with integers */
    PyErr_SetString(PyExc_TypeError, "expected a sequence or an iterable containing integers");
    return 1;
  }

  /* if the list is a sequence, we can pre-allocate the vector to its length */
  if (PySequence_Check(list)) {
    size_hint = PySequence_Size(list);
    if (size_hint < 0) {
      /* should not happen but let's try to recover */
      size_hint = 0;
    }
  } else {
    size_hint = 0;
  }

  /* initialize the result vector */
  if (igraph_vector_init(v, 0)) {
    igraphmodule_handle_igraph_error();
    return 1;
  }

  /* if we have a size hint, allocate the required space */
  if (size_hint > 0) {
    if (igraph_vector_reserve(v, size_hint)) {
      igraphmodule_handle_igraph_error();
      igraph_vector_destroy(v);
      return 1;
    }
  }

  /* try to use an iterator first */
  it = PyObject_GetIter(list);
  if (it) {
    while ((item = PyIter_Next(it)) != 0) {
      ok = true;

      if (igraphmodule_PyObject_to_integer_t(item, &number)) {
        PyErr_SetString(PyExc_ValueError, "iterable must yield integers");
        ok=0;
      } else {
        if (need_non_negative && number < 0) {
          PyErr_SetString(PyExc_ValueError, "iterable must yield non-negative integers");
          ok=0;
        }
      }

      Py_DECREF(item);

      if (!ok) {
        igraph_vector_destroy(v);
        Py_DECREF(it);
        return 1;
      }

      if (igraph_vector_push_back(v, number)) {
        igraphmodule_handle_igraph_error();
        igraph_vector_destroy(v);
        Py_DECREF(it);
        return 1;
      }
    }
    Py_DECREF(it);
  } else {
    /* list is not iterable; maybe it's a single number? */
    PyErr_Clear();
    if (igraphmodule_PyObject_to_integer_t(list, &number)) {
      PyErr_SetString(PyExc_TypeError, "sequence or iterable expected");
      igraph_vector_destroy(v);
      return 1;
    } else {
      if (need_non_negative && number < 0) {
        PyErr_SetString(PyExc_ValueError, "non-negative integers expected");
        igraph_vector_destroy(v);
        return 1;
      }
      if (igraph_vector_push_back(v, number)) {
        igraphmodule_handle_igraph_error();
        igraph_vector_destroy(v);
        return 1;
      }
    }
  }

  return 0;
}


/**
 * \ingroup python_interface_conversion
 * \brief Converts a Python list of floats to an igraph \c igraph_vector_t
 * The incoming \c igraph_vector_t should be uninitialized. Raises suitable
 * Python exceptions when needed.
 *
 * \param list the Python list to be converted
 * \param v the \c igraph_vector_t containing the result
 * \return 0 if everything was OK, 1 otherwise
 */
int igraphmodule_PyObject_float_to_vector_t(PyObject *list, igraph_vector_t *v) {
  PyObject *item, *it;
  Py_ssize_t size_hint;
  int ok;
  igraph_real_t number;

  if (PyBaseString_Check(list)) {
    /* It is highly unlikely that a string (although it is a sequence) will
     * provide us with numbers */
    PyErr_SetString(PyExc_TypeError, "expected a sequence or an iterable containing numbers");
    return 1;
  }

  /* if the list is a sequence, we can pre-allocate the vector to its length */
  if (PySequence_Check(list)) {
    size_hint = PySequence_Size(list);
    if (size_hint < 0) {
      /* should not happen but let's try to recover */
      size_hint = 0;
    }
  } else {
    size_hint = 0;
  }

  /* initialize the result vector */
  if (igraph_vector_init(v, 0)) {
    igraphmodule_handle_igraph_error();
    return 1;
  }

  /* if we have a size hint, allocate the required space */
  if (size_hint > 0) {
    if (igraph_vector_reserve(v, size_hint)) {
      igraphmodule_handle_igraph_error();
      igraph_vector_destroy(v);
      return 1;
    }
  }

  /* try to use an iterator first */
  it = PyObject_GetIter(list);
  if (it) {
    while ((item = PyIter_Next(it)) != 0) {
      ok = true;

      if (igraphmodule_PyObject_to_real_t(item, &number)) {
        PyErr_SetString(PyExc_ValueError, "iterable must yield numbers");
        ok=0;
      }

      Py_DECREF(item);

      if (!ok) {
        igraph_vector_destroy(v);
        Py_DECREF(it);
        return 1;
      }

      if (igraph_vector_push_back(v, number)) {
        igraphmodule_handle_igraph_error();
        igraph_vector_destroy(v);
        Py_DECREF(it);
        return 1;
      }
    }
    Py_DECREF(it);
  } else {
    /* list is not iterable; maybe it's a single number? */
    PyErr_Clear();
    if (igraphmodule_PyObject_to_real_t(list, &number)) {
      PyErr_SetString(PyExc_TypeError, "sequence or iterable expected");
      igraph_vector_destroy(v);
      return 1;
    } else {
      igraph_vector_push_back(v, number);
    }
  }

  return 0;
}

/**
 * \ingroup python_interface_conversion
 * \brief Converts a Python list of ints to an igraph \c igraph_vector_int_t
 * The incoming \c igraph_vector_int_t should be uninitialized.
 * Raises suitable Python exceptions when needed.
 *
 * This function is almost identical to
 * \ref igraphmodule_PyObject_to_vector_t . Make sure you fix bugs
 * in both cases (if any).
 *
 * \param list the Python list to be converted
 * \param v the \c igraph_vector_int_t containing the result
 * \return 0 if everything was OK, 1 otherwise
 */
int igraphmodule_PyObject_to_vector_int_t(PyObject *list, igraph_vector_int_t *v) {
  PyObject *it = 0, *item;
  igraph_int_t value = 0;
  Py_ssize_t i, j, k;
  int ok;

  if (PyBaseString_Check(list)) {
    /* It is highly unlikely that a string (although it is a sequence) will
     * provide us with integers or integer pairs */
    PyErr_SetString(PyExc_TypeError, "expected a sequence or an iterable containing integers");
    return 1;
  }

  if (!PySequence_Check(list)) {
    /* try to use an iterator */
    it = PyObject_GetIter(list);
    if (it) {
      if (igraph_vector_int_init(v, 0)) {
        igraphmodule_handle_igraph_error();
        Py_DECREF(it);
        return 1;
      }

      while ((item = PyIter_Next(it)) != 0) {
        if (!PyNumber_Check(item)) {
          PyErr_SetString(PyExc_TypeError, "iterable must return numbers");
          ok = false;
        } else {
          ok = (igraphmodule_PyObject_to_integer_t(item, &value) == 0);
        }

        if (ok == 0) {
          igraph_vector_int_destroy(v);
          Py_DECREF(item);
          Py_DECREF(it);
          return 1;
        }

        if (igraph_vector_int_push_back(v, value)) {
          igraphmodule_handle_igraph_error();
          igraph_vector_int_destroy(v);
          Py_DECREF(item);
          Py_DECREF(it);
          return 1;
        }

        Py_DECREF(item);
      }

      Py_DECREF(it);
    } else {
      PyErr_SetString(PyExc_TypeError, "sequence or iterable expected");
      return 1;
    }

    return 0;
  }

  j = PySequence_Size(list);

  if (igraph_vector_int_init(v, j)) {
    igraphmodule_handle_igraph_error();
    Py_XDECREF(it);
    return 1;
  }

  for (i = 0, k = 0; i < j; i++) {
    item = PySequence_GetItem(list, i);
    if (item) {
      if (!PyNumber_Check(item)) {
        PyErr_SetString(PyExc_TypeError, "sequence elements must be integers");
        ok = false;
      } else {
        ok = (igraphmodule_PyObject_to_integer_t(item, &value) == 0);
      }

      Py_XDECREF(item);

      if (!ok) {
        igraph_vector_int_destroy(v);
        return 1;
      }

      VECTOR(*v)[k]=value;
      k++;
    } else {
      /* this should not happen, but we return anyway.
       * an IndexError exception was set by PyList_GetItem
       * at this point */
      igraph_vector_int_destroy(v);
      return 1;
    }
  }

  return 0;
}

/**
 * \ingroup python_interface_conversion
 * \brief Converts a Python list of objects to an igraph \c igraph_vector_bool_t
 * The incoming \c igraph_vector_bool_t should be uninitialized. Raises suitable
 * Python exceptions when needed.
 *
 * \param list the Python list to be converted
 * \param v the \c igraph_vector_bool_t containing the result
 * \return 0 if everything was OK, 1 otherwise
 */
int igraphmodule_PyObject_to_vector_bool_t(PyObject *list,
    igraph_vector_bool_t *v) {
  PyObject *item;
  Py_ssize_t i, j;

  if (PyBaseString_Check(list)) {
    /* It is highly unlikely that a string (although it is a sequence) will
     * provide us with integers or integer pairs */
    PyErr_SetString(PyExc_TypeError, "expected a sequence or an iterable");
    return 1;
  }

  if (!PySequence_Check(list)) {
    /* try to use an iterator */
    PyObject *it = PyObject_GetIter(list);
    if (it) {
      PyObject *item;
      igraph_vector_bool_init(v, 0);
      while ((item = PyIter_Next(it)) != 0) {
        if (igraph_vector_bool_push_back(v, PyObject_IsTrue(item))) {
          igraphmodule_handle_igraph_error();
          igraph_vector_bool_destroy(v);
          Py_DECREF(item);
          Py_DECREF(it);
          return 1;
        }
        Py_DECREF(item);
      }
      Py_DECREF(it);
      return 0;
    } else {
      PyErr_SetString(PyExc_TypeError, "sequence or iterable expected");
      return 1;
    }
    return 0;
  }

  j=PySequence_Size(list);
  igraph_vector_bool_init(v, j);
  for (i=0; i<j; i++) {
    item=PySequence_GetItem(list, i);
    if (item) {
      VECTOR(*v)[i]=PyObject_IsTrue(item);
      Py_DECREF(item);
    } else {
      /* this should not happen, but we return anyway.
       * an IndexError exception was set by PySequence_GetItem
       * at this point */
      igraph_vector_bool_destroy(v);
      return 1;
    }
  }
  return 0;
}

/**
 * \ingroup python_interface_conversion
 * \brief Converts an igraph \c igraph_int_t to a Python integer
 *
 * \param value the \c igraph_int_t value to be converted
 * \return the Python integer as a \c PyObject*, or \c NULL if an
 * error occurred
 */
PyObject* igraphmodule_integer_t_to_PyObject(igraph_int_t value) {
#if IGRAPH_INTEGER_SIZE == 32
  /* minimum size of a long is 32 bits so we are okay */
  return PyLong_FromLong(value);
#elif IGRAPH_INTEGER_SIZE == 64
  /* minimum size of a long long is 64 bits so we are okay */
  return PyLong_FromLongLong(value);
#else
#  error "Unknown igraph_int_t size"
#endif
}

/**
 * \ingroup python_interface_conversion
 * \brief Converts an igraph \c igraph_real_t to a Python float or integer
 *
 * \param value the \c igraph_real_t value to be converted
 * \return the Python float or integer as a \c PyObject*, or \c NULL if an
 * error occurred
 */
PyObject* igraphmodule_real_t_to_PyObject(igraph_real_t value, igraphmodule_conv_t type) {
  if (!isfinite(value) || isnan(value)) {
    return PyFloat_FromDouble(value);
  }

  if (type == IGRAPHMODULE_TYPE_INT) {
    return PyLong_FromDouble(value);
  } else if (type == IGRAPHMODULE_TYPE_FLOAT) {
    return PyFloat_FromDouble(value);
  } else if (type == IGRAPHMODULE_TYPE_FLOAT_IF_FRACTIONAL_ELSE_INT) {
    if (ceil(value) != value) {
      return PyFloat_FromDouble(value);
    } else {
      return PyLong_FromDouble(value);
    }
  } else {
    Py_RETURN_NONE;
  }
}

/**
 * \ingroup python_interface_conversion
 * \brief Converts an igraph \c igraph_vector_bool_t to a Python boolean list
 *
 * \param v the \c igraph_vector_bool_t containing the vector to be converted
 * \return the Python boolean list as a \c PyObject*, or \c NULL if an
 * error occurred
 */
PyObject* igraphmodule_vector_bool_t_to_PyList(const igraph_vector_bool_t *v) {
  PyObject *list, *item;
  Py_ssize_t n, i;

  n = igraph_vector_bool_size(v);
  if (n < 0) {
    return igraphmodule_handle_igraph_error();
  }

  list = PyList_New(n);
  if (!list) {
    return NULL;
  }

  for (i = 0; i < n; i++) {
    item = VECTOR(*v)[i] ? Py_True : Py_False;
    Py_INCREF(item);
    PyList_SetItem(list, i, item);  /* will not fail */
  }

  return list;
}

/**
 * \ingroup python_interface_conversion
 * \brief Converts an igraph \c igraph_vector_t to a Python integer list
 *
 * \param v the \c igraph_vector_t containing the vector to be converted
 * \return the Python integer list as a \c PyObject*, or \c NULL if an error occurred
 */
PyObject* igraphmodule_vector_t_to_PyList(const igraph_vector_t *v, igraphmodule_conv_t type) {
  PyObject *list, *item;
  Py_ssize_t n, i;

  n = igraph_vector_size(v);
  if (n < 0) {
    return igraphmodule_handle_igraph_error();
  }

  list = PyList_New(n);
  if (!list) {
    return NULL;
  }

  for (i = 0; i < n; i++) {
    item = igraphmodule_real_t_to_PyObject(VECTOR(*v)[i], type);
    if (!item) {
      Py_DECREF(list);
      return NULL;
    }
    PyList_SetItem(list, i, item);  /* will not fail */
  }

  return list;
}

/**
 * \ingroup python_interface_conversion
 * \brief Converts an igraph \c igraph_vector_int_t to a Python integer list
 *
 * \param v the \c igraph_vector_int_t containing the vector to be converted
 * \return the Python integer list as a \c PyObject*, or \c NULL if an error occurred
 */
PyObject* igraphmodule_vector_int_t_to_PyList(const igraph_vector_int_t *v) {
  PyObject *list, *item;
  Py_ssize_t n, i;

  n = igraph_vector_int_size(v);
  if (n < 0) {
    return igraphmodule_handle_igraph_error();
  }

  list = PyList_New(n);
  if (!list) {
    return NULL;
  }

  for (i = 0; i < n; i++) {
    item = igraphmodule_integer_t_to_PyObject(VECTOR(*v)[i]);
    if (!item) {
      Py_DECREF(list);
      return NULL;
    }
    PyList_SetItem(list, i, item);  /* will not fail */
  }

  return list;
}

/**
 * \ingroup python_interface_conversion
 * \brief Converts an igraph \c igraph_vector_int_t to a Python integer list, with nan
 *
 * This function works like \ref igraphmodyle_vector_int_t_to_PyList but it maps
 * one distinguished value in the vector to NaN.
 *
 * \param v the \c igraph_vector_int_t containing the vector to be converted
 * \return the Python integer list as a \c PyObject*, or \c NULL if an error occurred
 */
PyObject* igraphmodule_vector_int_t_to_PyList_with_nan(const igraph_vector_int_t *v, const igraph_int_t nanvalue) {
  PyObject *list, *item;
  Py_ssize_t n, i;
  igraph_int_t val;

  n = igraph_vector_int_size(v);
  if (n < 0) {
    return igraphmodule_handle_igraph_error();
  }

  list = PyList_New(n);
  if (!list) {
    return NULL;
  }

  for (i = 0; i < n; i++) {
    val = VECTOR(*v)[i];
    if (val == nanvalue) {
      item = PyFloat_FromDouble(NAN);
    } else {
      item = igraphmodule_integer_t_to_PyObject(VECTOR(*v)[i]);
    }
    if (!item) {
      Py_DECREF(list);
      return NULL;
    }
    PyList_SetItem(list, i, item);  /* will not fail */
  }

  return list;
}

/**
 * \ingroup python_interface_conversion
 * \brief Converts an igraph \c igraph_vector_t to a Python integer tuple
 *
 * \param v the \c igraph_vector_t containing the vector to be converted
 * \param type the type of conversion. If equals to IGRAPHMODULE_TYPE_INT,
 *        returns an integer tuple, else returns a float tuple.
 * \return the Python integer or float tuple as a \c PyObject*, or \c NULL if an error occurred
 */
PyObject* igraphmodule_vector_t_to_PyTuple(const igraph_vector_t *v, igraphmodule_conv_t type) {
  PyObject *tuple, *item;
  Py_ssize_t n, i;

  n = igraph_vector_size(v);
  if (n < 0) {
    return igraphmodule_handle_igraph_error();
  }

  tuple = PyTuple_New(n);
  if (!tuple) {
    return NULL;
  }

  for (i = 0; i < n; i++) {
    item = igraphmodule_real_t_to_PyObject(VECTOR(*v)[i], type);
    if (!item) {
      Py_DECREF(tuple);
      return NULL;
    }

    PyTuple_SetItem(tuple, i, item);  /* will not fail */
  }

  return tuple;
}

/**
 * \ingroup python_interface_conversion
 * \brief Converts an igraph \c igraph_vector_int_t to a Python integer tuple
 *
 * \param v the \c igraph_vector_int_t containing the vector to be converted
 * \return the Python integer tuple as a \c PyObject*, or \c NULL if an error occurred
 */
PyObject* igraphmodule_vector_int_t_to_PyTuple(const igraph_vector_int_t *v) {
  PyObject *tuple, *item;
  Py_ssize_t n, i;

  n = igraph_vector_int_size(v);
  if (n < 0) {
    return igraphmodule_handle_igraph_error();
  }

  tuple = PyTuple_New(n);
  if (!tuple) {
    return NULL;
  }

  for (i = 0; i < n; i++) {
    item = igraphmodule_integer_t_to_PyObject(VECTOR(*v)[i]);
    if (!item) {
      Py_DECREF(tuple);
      return NULL;
    }
    PyTuple_SetItem(tuple, i, item);  /* will not fail */
  }

  return tuple;
}

/**
 * \ingroup python_interface_conversion
 * \brief Converts an igraph \c igraph_vector_int_t to a Python list of fixed-length tuples
 *
 * \param v the \c igraph_vector_t containing the vector to be converted
 * \return the Python integer pair list as a \c PyObject*, or \c NULL if an error occurred
 */
PyObject* igraphmodule_vector_int_t_to_PyList_of_fixed_length_tuples(
  const igraph_vector_int_t *v, Py_ssize_t tuple_len
) {
  PyObject *list, *tuple, *item;
  Py_ssize_t n, i, j, k;

  if (tuple_len < 1) {
    PyErr_SetString(PyExc_SystemError,
      "invalid invocation of igraphmodule_vector_int_t_to_PyList_of_fixed_length_tuples(), "
      "tuple length must be positive"
    );
  }

  n = igraph_vector_int_size(v);
  if (n < 0) {
    PyErr_SetString(PyExc_ValueError, "igraph vector has negative length");
    return NULL;
  }
  if (n % tuple_len != 0) {
    PyErr_Format(PyExc_ValueError, "igraph vector length must be divisible by %zd", tuple_len);
    return NULL;
  }

  /* create a new Python list */
  n /= tuple_len;
  list = PyList_New(n);
  if (!list) {
    return NULL;
  }

  /* populate the list with data */
  for (i = 0, k = 0; i < n; i++) {
    tuple = PyTuple_New(tuple_len);
    for (j = 0; j < tuple_len; k++, j++) {
      item = igraphmodule_integer_t_to_PyObject(VECTOR(*v)[k]);
      if (!item) {
        Py_DECREF(tuple);
        Py_DECREF(list);
        return NULL;
      }
      PyTuple_SetItem(tuple, j, item); /* will not fail */
      /* reference to 'item' is now owned by 'tuple' */
    }
    PyList_SetItem(list, i, tuple);   /* will not fail */
    /* reference to 'tuple' is now owned by 'list' */
  }

  return list;
}

/**
 * \ingroup python_interface_conversion
 * \brief Converts a Python iterable of non-negative integer pairs (i.e. an
 * edge list) to an igraph \c igraph_vector_t
 *
 * The incoming \c igraph_vector_int_t should be uninitialized. Raises suitable
 * Python exceptions when needed.
 *
 * \param list the Python list to be converted
 * \param v the \c igraph_vector_int_t containing the result
 * \param graph  the graph that will be used to interpret vertex names
 *               if a string is yielded by the Python iterable. \c NULL
 *               means that vertex names are not allowed.
 * \param list_is_owned  output argument that will be set to 1 if the
 *        vector containing the result "owns" its memory area and can be
 *        freed. Zero means that the vector is only a view into some memory
 *        area owned by someone else and the vector may not be destroyed by
 *        the caller.
 * \return 0 if everything was OK, 1 otherwise
 */
int igraphmodule_PyObject_to_edgelist(
    PyObject *list, igraph_vector_int_t *v, igraph_t *graph,
    igraph_bool_t* list_is_owned
) {
  PyObject *item, *i1, *i2, *it, *expected;
  int ok;
  igraph_int_t idx1=0, idx2=0;

  if (PyBaseString_Check(list)) {
    /* It is highly unlikely that a string (although it is a sequence) will
     * provide us with integers or integer pairs */
    PyErr_SetString(PyExc_TypeError, "expected a sequence or an iterable containing integer or string pairs");
    return 1;
  }

  /* We also accept a memoryview, although we don't advertise that in the
   * public API yet as the exact layout of the memory area has to match the
   * way items are laid out in an igraph_vector_int_t, and that's an implementation
   * detail that we don't want to commit ourselves to */
  if (PyMemoryView_Check(list)) {
    item = PyObject_GetAttrString(list, "itemsize");
    expected = PyLong_FromSize_t(sizeof(igraph_int_t));
    ok = item && PyObject_RichCompareBool(item, expected, Py_EQ);
    Py_XDECREF(expected);
    Py_XDECREF(item);
    if (!ok) {
      PyErr_SetString(
        PyExc_TypeError, "item size of buffer must match the size of igraph_int_t"
      );
      return 1;
    }

    item = PyObject_GetAttrString(list, "ndim");
    expected = PyLong_FromSize_t(2);
    ok = item && PyObject_RichCompareBool(item, expected, Py_EQ);
    Py_XDECREF(expected);
    Py_XDECREF(item);
    if (!ok) {
      PyErr_SetString(PyExc_TypeError, "edge list buffers must be two-dimensional");
      return 1;
    }

    item = PyObject_GetAttrString(list, "shape");
    it = item && PySequence_Check(item) ? PySequence_GetItem(item, 1) : 0;
    expected = PyLong_FromSize_t(2);
    ok = it && PyObject_RichCompareBool(it, expected, Py_EQ);
    Py_XDECREF(expected);
    Py_XDECREF(item);
    Py_XDECREF(it);
    if (!ok) {
      PyErr_SetString(PyExc_TypeError, "edge list buffers must have two columns");
      return 1;
    }

    item = PyObject_GetAttrString(list, "c_contiguous");
    ok = item == Py_True;
    Py_XDECREF(item);
    if (!ok) {
      PyErr_SetString(PyExc_TypeError, "edge list buffers must be contiguous");
      return 1;
    }

    /* If we are allowed to use the entire Python API, we can extract the buffer
     * from the memoryview here and return a _view_ into the buffer so we can
     * avoid copying. However, if we need to use the limited Python API, we
     * cannot get access to the buffer so we need to convert the memoryview
     * into a list first, and then cast that list into a _real_ igraph vector.
     */
    {
#ifdef PY_IGRAPH_ALLOW_ENTIRE_PYTHON_API
      Py_buffer *buffer = PyMemoryView_GET_BUFFER(item);
      igraph_vector_int_view(v, buffer->buf, buffer->len / buffer->itemsize);

      if (list_is_owned) {
        *list_is_owned = 0;
      }
#else
      PyObject *unfolded_list = PyObject_CallMethod(list, "tolist", 0);
      if (!unfolded_list) {
        return 1;
      }

      if (igraphmodule_PyObject_to_edgelist(unfolded_list, v, graph, list_is_owned)) {
        Py_DECREF(unfolded_list);
        return 1;
      }

      Py_DECREF(unfolded_list);
#endif
    }

    return 0;
  }

  it = PyObject_GetIter(list);
  if (!it)
    return 1;

  igraph_vector_int_init(v, 0);
  if (list_is_owned) {
    *list_is_owned = 1;
  }

  while ((item = PyIter_Next(it)) != 0) {
    ok = true;
    if (!PySequence_Check(item) || PySequence_Size(item) != 2) {
      PyErr_SetString(PyExc_TypeError, "iterable must return pairs of integers or strings");
      ok = false;
    } else {
      i1 = PySequence_GetItem(item, 0);
      i2 = i1 ? PySequence_GetItem(item, 1) : 0;
      ok = (i1 != 0 && i2 != 0);
      ok = ok && !igraphmodule_PyObject_to_vid(i1, &idx1, graph);
      ok = ok && !igraphmodule_PyObject_to_vid(i2, &idx2, graph);
      Py_XDECREF(i1); Py_XDECREF(i2); /* PySequence_ITEM returned new ref */
    }

    Py_DECREF(item);

    if (ok) {
      if (igraph_vector_int_push_back(v, idx1)) {
        igraphmodule_handle_igraph_error();
        ok = false;
      }
      if (ok && igraph_vector_int_push_back(v, idx2)) {
        igraphmodule_handle_igraph_error();
        ok = false;
      }
    }

    if (!ok) {
      igraph_vector_int_destroy(v);
      Py_DECREF(it);
      return 1;
    }
  }

  Py_DECREF(it);
  return 0;
}

/**
 * \ingroup python_interface_conversion
 * \brief Converts an attribute name or a sequence to a vector_t
 *
 * This function is useful for the interface of igraph C calls accepting
 * edge or vertex weights. The function checks the given Python object. If
 * it is None, returns a null pointer instead of an \c igraph_vector_t.
 * If it is a sequence, it converts the sequence to a newly allocated
 * \c igraph_vector_t and return a pointer to it. Otherwise it interprets the
 * object as an attribute name and returns the attribute values corresponding
 * to the name as an \c igraph_vector_t, or returns a null pointer if the attribute
 * does not exist.
 *
 * Note that if the function returned a pointer to an \c igraph_vector_t,
 * it is the caller's responsibility to destroy the object and free its
 * pointer after having finished using it.
 *
 * \param o the Python object being converted.
 * \param self a Python Graph object being used when attributes are queried
 * \param vptr the pointer to the allocated vector is returned here.
 * \param attr_type the type of the attribute being handled
 * \return 0 if everything was OK, nonzero otherwise.
 */
int igraphmodule_attrib_to_vector_t(PyObject *o, igraphmodule_GraphObject *self,
    igraph_vector_t **vptr, int attr_type) {
  igraph_vector_t *result;

  *vptr = 0;
  if (attr_type != ATTRIBUTE_TYPE_EDGE && attr_type != ATTRIBUTE_TYPE_VERTEX) {
    return 1;
  }

  if (o == Py_None) {
    return 0;
  }

  if (PyUnicode_Check(o)) {
    /* Check whether the attribute exists and is numeric */
    igraph_attribute_type_t at;
    igraph_attribute_elemtype_t et;
    igraph_int_t n;
    char *name = PyUnicode_CopyAsString(o);

    if (attr_type == ATTRIBUTE_TYPE_VERTEX) {
      et = IGRAPH_ATTRIBUTE_VERTEX;
      n = igraph_vcount(&self->g);
    } else {
      et = IGRAPH_ATTRIBUTE_EDGE;
      n = igraph_ecount(&self->g);
    }

    if (igraphmodule_i_attribute_get_type(&self->g, &at, et, name)) {
      /* exception was set by igraphmodule_i_attribute_get_type */
      free(name);
      return 1;
    }
    if (at != IGRAPH_ATTRIBUTE_NUMERIC) {
      PyErr_SetString(PyExc_ValueError, "attribute values must be numeric");
      free(name);
      return 1;
    }
    /* Now that the attribute type has been checked, allocate the target
     * vector */
    result = (igraph_vector_t*)calloc(1, sizeof(igraph_vector_t));
    if (result == 0) {
      PyErr_NoMemory();
      free(name);
      return 1;
    }
    if (igraph_vector_init(result, 0)) {
      igraphmodule_handle_igraph_error();
      free(name);
      free(result);
      return 1;
    }
    if (igraph_vector_reserve(result, n)) {
      igraphmodule_handle_igraph_error();
      igraph_vector_destroy(result);
      free(name);
      free(result);
      return 1;
    }
    if (attr_type == ATTRIBUTE_TYPE_VERTEX) {
      if (igraphmodule_i_get_numeric_vertex_attr(&self->g, name,
          igraph_vss_all(), result)) {
        /* exception has already been set, so return */
        igraph_vector_destroy(result);
        free(name);
        free(result);
        return 1;
      }
    } else {
      if (igraphmodule_i_get_numeric_edge_attr(&self->g, name,
          igraph_ess_all(IGRAPH_EDGEORDER_ID), result)) {
        /* exception has already been set, so return */
        igraph_vector_destroy(result);
        free(name);
        free(result);
        return 1;
      }
    }
    free(name);
    *vptr = result;
  } else if (PySequence_Check(o)) {
    result = (igraph_vector_t*)calloc(1, sizeof(igraph_vector_t));
    if (result == 0) {
      PyErr_NoMemory();
      return 1;
    }
    if (igraphmodule_PyObject_float_to_vector_t(o, result)) {
      igraph_vector_destroy(result);
      free(result);
      return 1;
    }
    *vptr = result;
  } else {
    PyErr_SetString(PyExc_TypeError, "unhandled type");
    return 1;
  }
  return 0;
}

/**
 * \ingroup python_interface_conversion
 * \brief Converts an attribute name or a sequence to a vector_int_t
 *
 * Similar to igraphmodule_attrib_to_vector_t. Make sure you fix bugs
 * in all two places (if any).
 *
 * Note that if the function returned a pointer to an \c igraph_vector_int_t,
 * it is the caller's responsibility to destroy the object and free its
 * pointer after having finished using it.
 *
 * \param o the Python object being converted.
 * \param self a Python Graph object being used when attributes are queried
 * \param vptr the pointer to the allocated vector is returned here.
 * \param attr_type the type of the attribute being handled
 * \return 0 if everything was OK, nonzero otherwise.
 */
int igraphmodule_attrib_to_vector_int_t(PyObject *o, igraphmodule_GraphObject *self,
    igraph_vector_int_t **vptr, int attr_type) {
  igraph_vector_int_t *result;

  *vptr = 0;

  if (attr_type != ATTRIBUTE_TYPE_EDGE && attr_type != ATTRIBUTE_TYPE_VERTEX)
    return 1;

  if (o == Py_None)
    return 0;

  if (PyUnicode_Check(o)) {
    igraph_vector_t* dummy = 0;
    igraph_int_t i, n;

    if (igraphmodule_attrib_to_vector_t(o, self, &dummy, attr_type)) {
      return 1;
    }

    if (dummy == 0) {
      return 0;
    }

    n = igraph_vector_size(dummy);

    result = (igraph_vector_int_t*)calloc(1, sizeof(igraph_vector_int_t));
    if (result == 0) {
      igraph_vector_destroy(dummy); free(dummy);
      PyErr_NoMemory();
      return 1;
    }

    if (igraph_vector_int_init(result, n)) {
      igraphmodule_handle_igraph_error();
      igraph_vector_destroy(dummy);
      free(dummy);
      free(result);
      return 1;
    }

    for (i = 0; i < n; i++) {
      VECTOR(*result)[i] = (igraph_int_t) VECTOR(*dummy)[i];
    }

    igraph_vector_destroy(dummy); free(dummy);
    *vptr = result;
  } else if (PySequence_Check(o)) {
    result = (igraph_vector_int_t*)calloc(1, sizeof(igraph_vector_int_t));
    if (result == 0) {
      PyErr_NoMemory();
      return 1;
    }

    if (igraphmodule_PyObject_to_vector_int_t(o, result)) {
      igraph_vector_int_destroy(result);
      free(result);
      return 1;
    }

    *vptr = result;
  } else {
    PyErr_SetString(PyExc_TypeError, "unhandled type");
    return 1;
  }

  return 0;
}

/**
 * \ingroup python_interface_conversion
 * \brief Converts an attribute name or a sequence to a vector_bool_t
 *
 * This function is useful for the interface of igraph C calls accepting
 * bipartite type vectors. The function checks the given Python object. If
 * it is None, returns a null pointer instead of an \c igraph_vector_bool_t.
 * If it is a sequence, it converts the sequence to a newly allocated
 * \c igraph_vector_bool_t and return a pointer to it. Otherwise it interprets the
 * object as an attribute name and returns the attribute values corresponding
 * to the name as an \c igraph_vector_bool_t, or returns a null pointer if the attribute
 * does not exist.
 *
 * Anything that evaluates to true using PyObject_IsTrue will be converted to
 * true in the resulting vector. Only numeric attributes are supported.
 *
 * Note that if the function returned a pointer to an \c igraph_vector_bool_t,
 * it is the caller's responsibility to destroy the object and free its
 * pointer after having finished using it.
 *
 * \param o the Python object being converted.
 * \param self a Python Graph object being used when attributes are queried
 * \param vptr the pointer to the allocated vector is returned here.
 * \param attr_type the type of the attribute being handled
 * \return 0 if everything was OK, nonzero otherwise.
 */
int igraphmodule_attrib_to_vector_bool_t(PyObject *o, igraphmodule_GraphObject *self,
    igraph_vector_bool_t **vptr, int attr_type) {
  igraph_vector_bool_t *result;

  *vptr = 0;
  if (attr_type != ATTRIBUTE_TYPE_EDGE && attr_type != ATTRIBUTE_TYPE_VERTEX)
    return 1;

  if (o == Py_None)
    return 0;

  if (PyUnicode_Check(o)) {
    igraph_int_t i, n;

    /* First, check if the attribute is a "real" boolean */
    igraph_attribute_type_t at;
    igraph_attribute_elemtype_t et;
    char *name = PyUnicode_CopyAsString(o);

    if (attr_type == ATTRIBUTE_TYPE_VERTEX) {
      et = IGRAPH_ATTRIBUTE_VERTEX;
      n = igraph_vcount(&self->g);
    } else {
      et = IGRAPH_ATTRIBUTE_EDGE;
      n = igraph_ecount(&self->g);
    }

    if (igraphmodule_i_attribute_get_type(&self->g, &at, et, name)) {
      /* exception was set by igraphmodule_i_attribute_get_type */
      free(name);
      return 1;
    }

    if (at == IGRAPH_ATTRIBUTE_BOOLEAN) {
      /* The attribute is a real Boolean attribute. Allocate the target
       * vector */
      result = (igraph_vector_bool_t*)calloc(1, sizeof(igraph_vector_bool_t));
      if (result == 0) {
        PyErr_NoMemory();
        free(name);
        return 1;
      }
      if (igraph_vector_bool_init(result, 0)) {
        igraphmodule_handle_igraph_error();
        free(name);
        free(result);
        return 1;
      }
      if (igraph_vector_bool_reserve(result, n)) {
        igraph_vector_bool_destroy(result);
        igraphmodule_handle_igraph_error();
        free(name);
        free(result);
        return 1;
      }
      if (attr_type == ATTRIBUTE_TYPE_VERTEX) {
        if (igraphmodule_i_get_boolean_vertex_attr(&self->g, name,
            igraph_vss_all(), result)) {
          /* exception has already been set, so return */
          igraph_vector_bool_destroy(result);
          free(name);
          free(result);
          return 1;
        }
      } else {
        if (igraphmodule_i_get_boolean_edge_attr(&self->g, name,
            igraph_ess_all(IGRAPH_EDGEORDER_ID), result)) {
          /* exception has already been set, so return */
          igraph_vector_bool_destroy(result);
          free(name);
          free(result);
          return 1;
        }
      }
      free(name);
      *vptr = result;
    } else if (at == IGRAPH_ATTRIBUTE_NUMERIC) {
      /* The attribute is a numeric attribute, so we fall back to
       * attrib_to_vector_t and then convert the result */
      igraph_vector_t *dummy = 0;
      free(name);
      if (igraphmodule_attrib_to_vector_t(o, self, &dummy, attr_type)) {
        return 1;
      }
      if (dummy == 0) {
        return 0;
      }

      n = igraph_vector_size(dummy);
      result = (igraph_vector_bool_t*)calloc(1, sizeof(igraph_vector_bool_t));
      if (result == 0) {
        igraph_vector_destroy(dummy); free(dummy);
        PyErr_NoMemory();
        return 1;
      }
      if (igraph_vector_bool_init(result, n)) {
        igraphmodule_handle_igraph_error();        
        igraph_vector_destroy(dummy); free(dummy);
        igraph_vector_bool_destroy(result); free(result);
        return 1;
      }
      for (i = 0; i < n; i++) {
        VECTOR(*result)[i] = (VECTOR(*dummy)[i] != 0 &&
            VECTOR(*dummy)[i] == VECTOR(*dummy)[i]);
      }
      igraph_vector_destroy(dummy); free(dummy);
      *vptr = result;
    } else {
      /* The attribute is not numeric and not Boolean. Throw an exception. */
      PyErr_SetString(PyExc_ValueError, "attribute values must be Boolean or numeric");
      free(name);
      return 1;
    }

  } else if (PySequence_Check(o)) {
    result = (igraph_vector_bool_t*)calloc(1, sizeof(igraph_vector_bool_t));
    if (result == 0) {
      PyErr_NoMemory();
      return 1;
    }
    if (igraphmodule_PyObject_to_vector_bool_t(o, result)) {
      free(result);
      return 1;
    }
    *vptr = result;
  } else {
    PyErr_SetString(PyExc_TypeError, "unhandled type");
    return 1;
  }

  return 0;
}

/**
 * \ingroup python_interface_conversion
 * \brief Converts two igraph \c igraph_vector_int_t vectors to a Python list of integer pairs
 *
 * \param v1 the \c igraph_vector_int_t containing the 1st vector to be converted
 * \param v2 the \c igraph_vector_int_t containing the 2nd vector to be converted
 * \return the Python integer pair list as a \c PyObject*, or \c NULL if an error occurred
 */
PyObject* igraphmodule_vector_int_t_pair_to_PyList(const igraph_vector_int_t *v1,
    const igraph_vector_int_t *v2) {
  PyObject *list, *pair, *first, *second;
  Py_ssize_t i, n;

  n = igraph_vector_int_size(v1);
  if (n < 0 || igraph_vector_int_size(v2) != n) {
    return igraphmodule_handle_igraph_error();
  }

  /* create a new Python list */
  list = PyList_New(n);
  if (!list) {
    return NULL;
  }

  /* populate the list with data */
  for (i = 0; i < n; i++) {
    first = igraphmodule_integer_t_to_PyObject(VECTOR(*v1)[i]);
    if (!first) {
      Py_DECREF(list);
      return NULL;
    }

    second = igraphmodule_integer_t_to_PyObject(VECTOR(*v2)[i]);
    if (!second) {
      Py_DECREF(first);
      Py_DECREF(list);
      return NULL;
    }

    pair = PyTuple_Pack(2, first, second);
    if (pair == NULL) {
      Py_DECREF(second);
      Py_DECREF(first);
      Py_DECREF(list);
      return NULL;
    }

    Py_DECREF(first);
    Py_DECREF(second);
    first = second = 0;

    PyList_SetItem(list, i, pair);  /* will not fail */
  }

  return list;
}

/**
 * \ingroup python_interface_conversion
 * \brief Converts an igraph \c igraph_matrix_t to a Python list of lists
 *
 * \param m the \c igraph_matrix_t containing the matrix to be converted
 * \param type the type of conversion. If equals to IGRAPHMODULE_TYPE_INT,
 *        returns an integer matrix, else returns a float matrix.
 * \return the Python list of lists as a \c PyObject*, or \c NULL if an error occurred
 */
PyObject* igraphmodule_matrix_t_to_PyList(const igraph_matrix_t *m,
    igraphmodule_conv_t type) {
  PyObject *list, *row, *item;
  Py_ssize_t nr, nc, i, j;

  nr = igraph_matrix_nrow(m);
  nc = igraph_matrix_ncol(m);
  if (nc < 0 || nc < 0) {
    return igraphmodule_handle_igraph_error();
  }

  // create a new Python list
  list = PyList_New(nr);
  if (!list) {
    return NULL;
  }

  // populate the list with data
  for (i = 0; i < nr; i++) {
    row = PyList_New(nc);
    if (!row) {
      Py_DECREF(list);
      return NULL;
    }

    for (j = 0; j < nc; j++) {
      item = igraphmodule_real_t_to_PyObject(MATRIX(*m, i, j), type);
      if (!item) {
        Py_DECREF(row);
        Py_DECREF(list);
        return NULL;
      }

      PyList_SetItem(row, j, item);  /* will not fail */
    }

    PyList_SetItem(list, i, row);  /* will not fail */
  }

  // return the list
  return list;
}

/**
 * \ingroup python_interface_conversion
 * \brief Converts an igraph \c igraph_matrix_int_t to a Python list of lists
 *
 * \param m the \c igraph_matrix_int_t containing the matrix to be converted
 * \return the Python list of lists as a \c PyObject*, or \c NULL if an error occurred
 */
PyObject* igraphmodule_matrix_int_t_to_PyList(const igraph_matrix_int_t *m) {
   PyObject *list, *row, *item;
   Py_ssize_t nr, nc, i, j;

   nr = igraph_matrix_int_nrow(m);
   nc = igraph_matrix_int_ncol(m);
   if (nr < 0 || nc < 0) {
     return igraphmodule_handle_igraph_error();
   }

   // create a new Python list
   list = PyList_New(nr);
   if (!list) {
     return NULL;
   }

   // populate the list with data
   for (i = 0; i < nr; i++) {
    row = PyList_New(nc);
    if (!row) {
      Py_DECREF(list);
      return NULL;
    }

    for (j = 0; j < nc; j++) {
      // convert to integers except nan or infinity
      item = igraphmodule_integer_t_to_PyObject(MATRIX(*m, i, j));
      if (!item) {
        Py_DECREF(row);
        Py_DECREF(list);
        return NULL;
      }

      PyList_SetItem(row, j, item);  /* will not fail */
    }

    PyList_SetItem(list, i, row);  /* will not fail */
  }

  // return the list
  return list;
}

/**
 * \ingroup python_interface_conversion
 * \brief Converts an igraph \c igraph_matrix_list_t to a Python list of lists of lists
 *
 * \param v the \c igraph_matrix_list_t containing the matrix list to be converted
 * \return the Python list as a \c PyObject*, or \c NULL if an error occurred
 */
PyObject* igraphmodule_matrix_list_t_to_PyList(const igraph_matrix_list_t *m) {
  PyObject *list, *item;
  Py_ssize_t n, i;

  n = igraph_matrix_list_size(m);
  if (n < 0) {
    return igraphmodule_handle_igraph_error();
  }

  list = PyList_New(n);
  if (!list) {
    return NULL;
  }

  for (i = 0; i < n; i++) {
    item = igraphmodule_matrix_t_to_PyList(igraph_matrix_list_get_ptr(m, i),
        IGRAPHMODULE_TYPE_FLOAT);
    if (item == NULL) {
      Py_DECREF(list);
      return NULL;
    }
    PyList_SetItem(list, i, item);  /* will not fail */
  }

  return list;
}

/**
 * \ingroup python_interface_conversion
 * \brief Converts an igraph \c igraph_vector_ptr_t to a Python list of lists
 *
 * \param v the \c igraph_vector_ptr_t containing the vector pointer to be converted
 * \return the Python list as a \c PyObject*, or \c NULL if an error occurred
 */
PyObject* igraphmodule_vector_ptr_t_to_PyList(const igraph_vector_ptr_t *v,
    igraphmodule_conv_t type) {
  PyObject *list, *item;
  Py_ssize_t n, i;

  n = igraph_vector_ptr_size(v);
  if (n < 0) {
    return igraphmodule_handle_igraph_error();
  }

  list = PyList_New(n);
  if (!list) {
    return NULL;
  }

  for (i = 0; i < n; i++) {
    item = igraphmodule_vector_t_to_PyList((igraph_vector_t*)VECTOR(*v)[i], type);
    if (item == NULL) {
      Py_DECREF(list);
      return NULL;
    }
    PyList_SetItem(list, i, item);  /* will not fail */
  }

  return list;
}

/**
 * \ingroup python_interface_conversion
 * \brief Converts an igraph \c igraph_vector_ptr_t to a Python list of lists
 *
 * \param v the \c igraph_vector_ptr_t containing the vector pointer to be converted
 * \return the Python list as a \c PyObject*, or \c NULL if an error occurred
 */
PyObject* igraphmodule_vector_int_ptr_t_to_PyList(const igraph_vector_ptr_t *v) {
  PyObject *list, *item;
  Py_ssize_t n, i;

  n = igraph_vector_ptr_size(v);
  if (n < 0) {
    return igraphmodule_handle_igraph_error();
  }

  list = PyList_New(n);
  if (!list) {
    return NULL;
  }

  for (i = 0; i < n; i++) {
    item = igraphmodule_vector_int_t_to_PyList((igraph_vector_int_t*)VECTOR(*v)[i]);
    if (item == NULL) {
      Py_DECREF(list);
      return NULL;
    }
    PyList_SetItem(list, i, item);  /* will not fail */
  }

  return list;
}

/**
 * \ingroup python_interface_conversion
 * \brief Converts an igraph \c igraph_vector_list_t to a Python list of lists
 *
 * \param v the \c igraph_vector_list_t containing the vector list to be converted
 * \return the Python list as a \c PyObject*, or \c NULL if an error occurred
 */
PyObject* igraphmodule_vector_list_t_to_PyList(const igraph_vector_list_t *v) {
  PyObject *list, *item;
  Py_ssize_t n, i;

  n = igraph_vector_list_size(v);
  if (n < 0) {
    return igraphmodule_handle_igraph_error();
  }

  list = PyList_New(n);
  if (!list) {
    return NULL;
  }

  for (i = 0; i < n; i++) {
    item = igraphmodule_vector_t_to_PyList(igraph_vector_list_get_ptr(v, i),
        IGRAPHMODULE_TYPE_FLOAT);
    if (item == NULL) {
      Py_DECREF(list);
      return NULL;
    }
    PyList_SetItem(list, i, item);  /* will not fail */
  }

  return list;
}

/**
 * \ingroup python_interface_conversion
 * \brief Converts an igraph \c igraph_vector_int_list_t to a Python list of lists
 *
 * \param v the \c igraph_vector_int_list_t containing the vector list to be converted
 * \return the Python list as a \c PyObject*, or \c NULL if an error occurred
 */
PyObject* igraphmodule_vector_int_list_t_to_PyList(const igraph_vector_int_list_t *v) {
  PyObject *list, *item;
  Py_ssize_t n, i;

  n = igraph_vector_int_list_size(v);
  if (n < 0) {
    return igraphmodule_handle_igraph_error();
  }

  list = PyList_New(n);
  if (!list) {
    return NULL;
  }

  for (i = 0; i < n; i++) {
    item = igraphmodule_vector_int_t_to_PyList(igraph_vector_int_list_get_ptr(v, i));
    if (item == NULL) {
      Py_DECREF(list);
      return NULL;
    }
    PyList_SetItem(list, i, item);  /* will not fail */
  }

  return list;
}


/**
 * \ingrup python_interface_conversion
 * \brief Converts an igraph \c igraph_vector_int_list_t to a Python list of tuples
 *
 * \param v the \c igraph_vector_int_list_t containing the vector list to be converted
 * \return the Python list as a \c PyObject*, or \c NULL if an error occurred
 */
PyObject* igraphmodule_vector_int_list_t_to_PyList_of_tuples(const igraph_vector_int_list_t *v) {
  PyObject *list, *item;
  Py_ssize_t n, i;

  n = igraph_vector_int_list_size(v);
  if (n < 0) {
    return igraphmodule_handle_igraph_error();
  }

  list = PyList_New(n);
  if (!list) {
    return NULL;
  }

  for (i = 0; i < n; i++) {
    item = igraphmodule_vector_int_t_to_PyTuple(igraph_vector_int_list_get_ptr(v, i));
    if (item == NULL) {
      Py_DECREF(list);
      return NULL;
    }
    PyList_SetItem(list, i, item);  /* will not fail */
  }

  return list;

}


/**
 * \ingroup python_interface_conversion
 * \brief Converts an \c igraph_graph_list_t into a Python list of graphs
 *
 * This function transfers ownership of the graphs to Python and empties the
 * graph list in parallel. You can (and should) call \c igraph_graph_list_destroy
 * regularly after the conversion is done.
 *
 * \param v the \c igraph_graph_list_t containing the list to be converted; the
 *     list will become empty after executing this function
 * \param type the GraphBase subclass you want your graphs to use. When called from
 *   a GraphBase method, this is typically Py_TYPE(self)
 * \return the Python list as a \c PyObject*, or \c NULL if an error occurred
 */
PyObject* igraphmodule_graph_list_t_to_PyList(igraph_graph_list_t *v, PyTypeObject* type) {
  PyObject *list;
  Py_ssize_t n, i;
  igraph_t g;
  igraphmodule_GraphObject *o;

  /* We have to create a Python igraph object for every graph returned */
  n = igraph_graph_list_size(v);
  list = PyList_New(n);
  for (i = n - 1; i >= 0; i--) {
    /* Remove the last graph from the list and take ownership of it temporarily */
    if (igraph_graph_list_remove(v, i, &g)) {
      igraphmodule_handle_igraph_error();
      Py_DECREF(list);
      return NULL;
    }

    /* Transfer ownership of the graph to Python */
    o = (igraphmodule_GraphObject*) igraphmodule_Graph_subclass_from_igraph_t(type, &g);
    if (o == NULL) {
      igraph_destroy(&g);
      Py_DECREF(list);
      return NULL;
    }

    /* Put the graph into the result list; the list will take ownership */
    if (PyList_SetItem(list, i, (PyObject *) o)) {
      Py_DECREF(o);
      Py_DECREF(list);
      return NULL;
    }
  }

  if (!igraph_graph_list_empty(v)) {
    PyErr_SetString(PyExc_RuntimeError, "expected empty graph list after conversion");
    Py_DECREF(list);
    return NULL;
  }

  return list;
}


/**
 * \ingroup python_interface_conversion
 * \brief Converts a Python list of lists to an \c igraph_matrix_t
 *
 * \param o the Python object representing the list of lists
 * \param m the address of an uninitialized \c igraph_matrix_t
 * \param arg_name  name of the argument we are attempting to convert, if
 *        applicable. May be used in error messages.
 * \return 0 if everything was OK, 1 otherwise. Sets appropriate exceptions.
 */
int igraphmodule_PyObject_to_matrix_t(
  PyObject* o, igraph_matrix_t *m, const char *arg_name
) {
  return igraphmodule_PyObject_to_matrix_t_with_minimum_column_count(o, m, 0, arg_name);
}

/**
 * \ingroup python_interface_conversion
 * \brief Converts a Python list of lists to an \c igraph_matrix_t, ensuring
 * that the matrix has at least the given number of columns
 *
 * \param o the Python object representing the list of lists
 * \param m the address of an uninitialized \c igraph_matrix_t
 * \param num_cols the minimum number of columns in the matrix
 * \param arg_name  name of the argument we are attempting to convert, if
 *        applicable. May be used in error messages.
 * \return 0 if everything was OK, 1 otherwise. Sets appropriate exceptions.
 */
int igraphmodule_PyObject_to_matrix_t_with_minimum_column_count(
  PyObject *o, igraph_matrix_t *m, int min_cols, const char *arg_name
) {
  Py_ssize_t nr, nc, n, i, j;
  PyObject *row, *item;
  igraph_real_t value;

  /* calculate the matrix dimensions */
  if (!PySequence_Check(o) || PyUnicode_Check(o)) {
    if (arg_name) {
      PyErr_Format(PyExc_TypeError, "matrix expected in '%s'", arg_name);
    } else {
      PyErr_SetString(PyExc_TypeError, "matrix expected");
    }
    return 1;
  }

  nr = PySequence_Size(o);
  if (nr < 0) {
    return 1;
  }

  nc = min_cols > 0 ? min_cols : 0;
  for (i = 0; i < nr; i++) {
    row = PySequence_GetItem(o, i);
    if (!PySequence_Check(row)) {
      Py_DECREF(row);
      if (arg_name) {
        PyErr_Format(PyExc_TypeError, "matrix expected in '%s'", arg_name);
      } else {
        PyErr_SetString(PyExc_TypeError, "matrix expected");
      }
      return 1;
    }
    n = PySequence_Size(row);
    Py_DECREF(row);
    if (n < 0) {
      return 1;
    }
    if (n > nc) {
      nc = n;
    }
  }

  if (igraph_matrix_init(m, nr, nc)) {
    igraphmodule_handle_igraph_error();
    return 1;
  }

  for (i = 0; i < nr; i++) {
    row = PySequence_GetItem(o, i);
    n = PySequence_Size(row);
    for (j = 0; j < n; j++) {
      item = PySequence_GetItem(row, j);
      if (!item) {
        igraph_matrix_destroy(m);
        return 1;
      }
      if (igraphmodule_PyObject_to_real_t(item, &value)) {
        igraph_matrix_destroy(m);
        Py_DECREF(item);
        return 1;
      }
      Py_DECREF(item);
      MATRIX(*m, i, j) = value;
    }
    Py_DECREF(row);
  }

  return 0;
}

/**
 * \ingroup python_interface_conversion
 * \brief Converts a Python list of lists to an \c igraph_matrix_int_t
 *
 * \param o the Python object representing the list of lists
 * \param m the address of an uninitialized \c igraph_matrix_int_t
 * \param arg_name  name of the argument we are attempting to convert, if
 *        applicable. May be used in error messages.
 * \return 0 if everything was OK, 1 otherwise. Sets appropriate exceptions.
 */
int igraphmodule_PyObject_to_matrix_int_t(
  PyObject* o, igraph_matrix_int_t *m, const char* arg_name
) {
  return igraphmodule_PyObject_to_matrix_int_t_with_minimum_column_count(o, m, 0, arg_name);
}

/**
 * \ingroup python_interface_conversion
 * \brief Converts a Python list of lists to an \c igraph_matrix_int_t, ensuring
 * that the matrix has at least the given number of columns
 *
 * \param o the Python object representing the list of lists
 * \param m the address of an uninitialized \c igraph_matrix_int_t
 * \param num_cols the minimum number of columns in the matrix
 * \param arg_name  name of the argument we are attempting to convert, if
 *        applicable. May be used in error messages.
 * \return 0 if everything was OK, 1 otherwise. Sets appropriate exceptions.
 */
int igraphmodule_PyObject_to_matrix_int_t_with_minimum_column_count(
  PyObject *o, igraph_matrix_int_t *m, int min_cols, const char* arg_name
) {
  Py_ssize_t nr, nc, n, i, j;
  PyObject *row, *item;
  igraph_int_t value;

  /* calculate the matrix dimensions */
  if (!PySequence_Check(o) || PyUnicode_Check(o)) {
    if (arg_name) {
      PyErr_Format(PyExc_TypeError, "integer matrix expected in '%s'", arg_name);
    } else {
      PyErr_SetString(PyExc_TypeError, "integer matrix expected");
    }
    return 1;
  }

  nr = PySequence_Size(o);
  if (nr < 0) {
    return 1;
  }

  nc = min_cols > 0 ? min_cols : 0;
  for (i = 0; i < nr; i++) {
    row = PySequence_GetItem(o, i);
    if (!PySequence_Check(row)) {
      Py_DECREF(row);
      if (arg_name) {
        PyErr_Format(PyExc_TypeError, "integer matrix expected in '%s'", arg_name);
      } else {
        PyErr_SetString(PyExc_TypeError, "integer matrix expected");
      }
      return 1;
    }
    n = PySequence_Size(row);
    Py_DECREF(row);
    if (n < 0) {
      return 1;
    }
    if (n > nc) {
      nc = n;
    }
  }

  if (igraph_matrix_int_init(m, nr, nc)) {
    igraphmodule_handle_igraph_error();
    return 1;
  }

  for (i = 0; i < nr; i++) {
    row = PySequence_GetItem(o, i);
    n = PySequence_Size(row);
    for (j = 0; j < n; j++) {
      item = PySequence_GetItem(row, j);
      if (!item) {
        igraph_matrix_int_destroy(m);
        return 1;
      }
      if (igraphmodule_PyObject_to_integer_t(item, &value)) {
        igraph_matrix_int_destroy(m);
        Py_DECREF(item);
        return 1;
      }
      Py_DECREF(item);
      MATRIX(*m, i, j) = value;
    }
    Py_DECREF(row);
  }

  return 0;
}

/**
 * \ingroup python_interface_conversion
 * \brief Converts a Python list of lists to an \c igraph_vector_ptr_t
 *        containing \c igraph_vector_t items.
 *
 * The returned vector will have an item destructor that destroys the
 * contained vectors, so it is important to call \c igraph_vector_ptr_destroy_all
 * on it instead of \c igraph_vector_ptr_destroy when the vector is no longer
 * needed.
 *
 * \param o the Python object representing the list of lists
 * \param m the address of an uninitialized \c igraph_vector_ptr_t
 * \return 0 if everything was OK, 1 otherwise. Sets appropriate exceptions.
 */
int igraphmodule_PyObject_to_vector_ptr_t(PyObject* list, igraph_vector_ptr_t* vec,
    igraph_bool_t need_non_negative) {
  PyObject *it, *item;
  igraph_vector_t *subvec;

  if (PyUnicode_Check(list)) {
    PyErr_SetString(PyExc_TypeError, "expected iterable (but not string)");
    return 1;
  }

  it = PyObject_GetIter(list);
  if (!it) {
    return 1;
  }

  if (igraph_vector_ptr_init(vec, 0)) {
    igraphmodule_handle_igraph_error();
    Py_DECREF(it);
    return 1;
  }

  IGRAPH_VECTOR_PTR_SET_ITEM_DESTRUCTOR(vec, igraph_vector_destroy);
  while ((item = PyIter_Next(it)) != 0) {
    subvec = IGRAPH_CALLOC(1, igraph_vector_t);
    if (subvec == 0) {
      Py_DECREF(item);
      Py_DECREF(it);
      PyErr_NoMemory();
      return 1;
    }

    if (igraphmodule_PyObject_to_vector_t(item, subvec, need_non_negative)) {
      Py_DECREF(item);
      Py_DECREF(it);
      igraph_vector_destroy(subvec);
      free(subvec);
      igraph_vector_ptr_destroy_all(vec);
      return 1;
    }

    Py_DECREF(item);

    if (igraph_vector_ptr_push_back(vec, subvec)) {
      Py_DECREF(it);
      igraph_vector_destroy(subvec);
      free(subvec);
      igraph_vector_ptr_destroy_all(vec);
      return 1;
    }

    /* ownership of 'subvec' taken by 'vec' here */
  }

  Py_DECREF(it);
  return 0;
}

/**
 * \ingroup python_interface_conversion
 * \brief Converts a Python list of lists to an \c igraph_vector_ptr_t
 *        containing \c igraph_vector_int_t items.
 *
 * The returned vector will have an item destructor that destroys the
 * contained vectors, so it is important to call \c igraph_vector_ptr_destroy_all
 * on it instead of \c igraph_vector_ptr_destroy when the vector is no longer
 * needed.
 *
 * \param o the Python object representing the list of lists
 * \param m the address of an uninitialized \c igraph_vector_ptr_t
 * \return 0 if everything was OK, 1 otherwise. Sets appropriate exceptions.
 */
int igraphmodule_PyObject_to_vector_int_ptr_t(PyObject* list, igraph_vector_ptr_t* vec) {
  PyObject *it, *item;
  igraph_vector_int_t *subvec;

  if (PyUnicode_Check(list)) {
    PyErr_SetString(PyExc_TypeError, "expected iterable (but not string)");
    return 1;
  }

  it = PyObject_GetIter(list);
  if (!it) {
    return 1;
  }

  if (igraph_vector_ptr_init(vec, 0)) {
    igraphmodule_handle_igraph_error();
    Py_DECREF(it);
    return 1;
  }

  IGRAPH_VECTOR_PTR_SET_ITEM_DESTRUCTOR(vec, igraph_vector_int_destroy);
  while ((item = PyIter_Next(it)) != 0) {
    subvec = IGRAPH_CALLOC(1, igraph_vector_int_t);
    if (subvec == 0) {
      Py_DECREF(item);
      Py_DECREF(it);
      PyErr_NoMemory();
      return 1;
    }

    if (igraphmodule_PyObject_to_vector_int_t(item, subvec)) {
      Py_DECREF(item);
      Py_DECREF(it);
      igraph_vector_int_destroy(subvec);
      free(subvec);
      igraph_vector_ptr_destroy_all(vec);
      return 1;
    }

    Py_DECREF(item);

    if (igraph_vector_ptr_push_back(vec, subvec)) {
      Py_DECREF(it);
      igraph_vector_int_destroy(subvec);
      free(subvec);
      igraph_vector_ptr_destroy_all(vec);
      return 1;
    }

    /* ownership of 'subvec' taken by 'vec' here */
  }

  Py_DECREF(it);
  return 0;
}

/**
 * \ingroup python_interface_conversion
 * \brief Converts a Python list of lists to an \c igraph_vector_list_t
 *        (containing \c igraph_vector_t items).
 *
 * \param o the Python object representing the list of lists
 * \param m the address of an uninitialized \c igraph_vector_list_t
 * \return 0 if everything was OK, 1 otherwise. Sets appropriate exceptions.
 */
int igraphmodule_PyObject_to_vector_list_t(PyObject* list, igraph_vector_list_t* veclist) {
  PyObject *it, *item;
  igraph_vector_t vec;

  if (PyUnicode_Check(list)) {
    PyErr_SetString(PyExc_TypeError, "expected iterable (but not string)");
    return 1;
  }

  it = PyObject_GetIter(list);
  if (!it) {
    return 1;
  }

  if (igraph_vector_list_init(veclist, 0)) {
    igraphmodule_handle_igraph_error();
    Py_DECREF(it);
    return 1;
  }

  while ((item = PyIter_Next(it)) != 0) {
    if (igraphmodule_PyObject_to_vector_t(item, &vec, 0)) {
      Py_DECREF(item);
      Py_DECREF(it);
      igraph_vector_destroy(&vec);
      igraph_vector_list_destroy(veclist);
      return 1;
    }

    Py_DECREF(item);

    if (igraph_vector_list_push_back(veclist, &vec)) {
      Py_DECREF(it);
      igraph_vector_destroy(&vec);
      igraph_vector_list_destroy(veclist);
      return 1;
    }

    /* ownership of 'vec' taken by 'veclist' here */
  }

  Py_DECREF(it);
  return 0;
}

/**
 * \ingroup python_interface_conversion
 * \brief Converts a Python list of lists to an \c igraph_vector_int_list_t
 *        (containing \c igraph_vector_int_t items).
 *
 * \param o the Python object representing the list of lists
 * \param m the address of an uninitialized \c igraph_vector_int_list_t
 * \return 0 if everything was OK, 1 otherwise. Sets appropriate exceptions.
 */
int igraphmodule_PyObject_to_vector_int_list_t(PyObject* list, igraph_vector_int_list_t* veclist) {
  PyObject *it, *item;
  igraph_vector_int_t vec;

  if (PyUnicode_Check(list)) {
    PyErr_SetString(PyExc_TypeError, "expected iterable (but not string)");
    return 1;
  }

  it = PyObject_GetIter(list);
  if (!it) {
    return 1;
  }

  if (igraph_vector_int_list_init(veclist, 0)) {
    igraphmodule_handle_igraph_error();
    Py_DECREF(it);
    return 1;
  }

  while ((item = PyIter_Next(it)) != 0) {
    if (igraphmodule_PyObject_to_vector_int_t(item, &vec)) {
      Py_DECREF(item);
      Py_DECREF(it);
      igraph_vector_int_destroy(&vec);
      igraph_vector_int_list_destroy(veclist);
      return 1;
    }

    Py_DECREF(item);

    if (igraph_vector_int_list_push_back(veclist, &vec)) {
      Py_DECREF(it);
      igraph_vector_int_destroy(&vec);
      igraph_vector_int_list_destroy(veclist);
      return 1;
    }

    /* ownership of 'vec' taken by 'veclist' here */
  }

  Py_DECREF(it);
  return 0;
}


/**
 * \ingroup python_interface_conversion
 * \brief Converts an \c igraph_strvector_t to a Python string list
 *
 * \param v the \c igraph_strvector_t containing the vector to be converted
 * \return the Python string list as a \c PyObject*, or \c NULL if an error occurred
 */
PyObject* igraphmodule_strvector_t_to_PyList(igraph_strvector_t *v) {
  PyObject *list, *item;
  Py_ssize_t n, i;
  const char* ptr;

  n = igraph_strvector_size(v);
  if (n < 0) {
    return igraphmodule_handle_igraph_error();
  }

  /* create a new Python list */
  list = PyList_New(n);
  if (!list) {
    return NULL;
  }

  /* populate the list with data */
  for (i = 0; i < n; i++) {
    ptr = igraph_strvector_get(v, i);

    item = PyUnicode_FromString(ptr);
    if (!item) {
      Py_DECREF(list);
      return NULL;
    }

    PyList_SetItem(list, i, item);  /* will not fail */
  }

  /* return the list */
  return list;
}

/**
 * \ingroup python_interface_conversion
 * \brief Converts a Python string list to an \c igraph_strvector_t
 *
 * \param v the Python list as a \c PyObject*
 * \param result an \c igraph_strvector_t containing the result
 * The incoming \c igraph_strvector_t should be uninitialized. Raises suitable
 * Python exceptions when needed.
 * \return 0 if everything was OK, 1 otherwise
 */
int igraphmodule_PyList_to_strvector_t(PyObject* v, igraph_strvector_t *result) {
  Py_ssize_t n;

  if (!PyList_Check(v)) {
    PyErr_SetString(PyExc_TypeError, "expected list");
    return 1;
  }

  n = PyList_Size(v);

  /* initialize the string vector */
  if (igraph_strvector_init(result, n)) {
    return 1;
  }

  return igraphmodule_PyList_to_existing_strvector_t(v, result);
}

int igraphmodule_PyList_to_existing_strvector_t(PyObject* v, igraph_strvector_t *result) {
  Py_ssize_t n, i;
  PyObject *o;

  if (!PyList_Check(v)) {
    PyErr_SetString(PyExc_TypeError, "expected list");
    return 1;
  }

  n = PyList_Size(v);

  if (igraph_strvector_resize(result, n)) {
    return 1;
  }

  /* populate the vector with data */
  for (i = 0; i < n; i++) {
    PyObject *item = PyList_GetItem(v, i);
    char* ptr;
    igraph_bool_t will_free = false;

    if (PyUnicode_Check(item)) {
      ptr = PyUnicode_CopyAsString(item);
      if (ptr == 0) {
        igraph_strvector_destroy(result);
        return 1;
      }
      will_free = true;
    } else {
      o = PyObject_Str(item);
      if (o == 0) {
        igraph_strvector_destroy(result);
        return 1;
      }
      ptr = PyUnicode_CopyAsString(o);
      Py_DECREF(o);
      if (ptr == 0) {
        igraph_strvector_destroy(result);
        return 1;
      }
      will_free = true;
    }

    if (igraph_strvector_set(result, i, ptr)) {
      if (will_free) {
        free(ptr);
      }
      igraph_strvector_destroy(result);
      return 1;
    }

    if (will_free) {
      free(ptr);
    }
  }

  return 0;
}

/**
 * \ingroup python_interface_conversion
 * \brief Appends the contents of a Python iterator returning graphs to
 * an \c igraph_vectorptr_t
 *
 * The incoming \c igraph_vector_ptr_t should be INITIALIZED.
 * Raises suitable Python exceptions when needed.
 *
 * \param it the Python iterator
 * \param v the \c igraph_vector_ptr_t which will contain the result
 * \return 0 if everything was OK, 1 otherwise
 */
int igraphmodule_append_PyIter_of_graphs_to_vector_ptr_t(PyObject *it,
    igraph_vector_ptr_t *v) {
  PyObject *t;

  while ((t=PyIter_Next(it))) {
    if (!PyObject_TypeCheck(t, igraphmodule_GraphType)) {
      PyErr_SetString(PyExc_TypeError, "iterable argument must contain graphs");
      Py_DECREF(t);
      return 1;
    }
    igraph_vector_ptr_push_back(v, &((igraphmodule_GraphObject*)t)->g);
    Py_DECREF(t);
  }

  return 0;
}

/**
 * \ingroup python_interface_conversion
 * \brief Appends the contents of a Python iterator returning graphs to
 * an \c igraph_vectorptr_t, and also stores the class of the first graph
 *
 * The incoming \c igraph_vector_ptr_t should be INITIALIZED.
 * Raises suitable Python exceptions when needed.
 *
 * \param it the Python iterator
 * \param v the \c igraph_vector_ptr_t which will contain the result
 * \return 0 if everything was OK, 1 otherwise
 */
int igraphmodule_append_PyIter_of_graphs_to_vector_ptr_t_with_type(PyObject *it,
    igraph_vector_ptr_t *v,
    PyTypeObject **g_type) {
  PyObject *t;
  int first = 1;

  while ((t = PyIter_Next(it))) {
    if (!PyObject_TypeCheck(t, igraphmodule_GraphType)) {
      PyErr_SetString(PyExc_TypeError, "iterable argument must contain graphs");
      Py_DECREF(t);
      return 1;
    }
    if (first) {
      *g_type = Py_TYPE(t);
      first = 0;
    }
    igraph_vector_ptr_push_back(v, &((igraphmodule_GraphObject*)t)->g);
    Py_DECREF(t);
  }

  return 0;
}

/**
 * \ingroup python_interface_conversion
 * \brief Tries to interpret a Python object as a single vertex ID
 *
 * \param o      the Python object
 * \param vid    the vertex ID will be stored here
 * \param graph  the graph that will be used to interpret vertex names
 *               if a string was given in o. It may also be a null pointer
 *               if we don't need name lookups.
 * \return 0 if everything was OK, 1 otherwise
 */
int igraphmodule_PyObject_to_vid(PyObject *o, igraph_int_t *vid, igraph_t *graph) {
  if (o == 0) {
    PyErr_SetString(PyExc_TypeError, "only non-negative integers, strings or igraph.Vertex objects can be converted to vertex IDs");
    return 1;
  } else if (PyLong_Check(o)) {
    /* Single vertex ID */
    if (igraphmodule_PyObject_to_integer_t(o, vid)) {
      return 1;
    }
  } else if (graph != 0 && PyBaseString_Check(o)) {
    /* Single vertex ID from vertex name */
    if (igraphmodule_get_vertex_id_by_name(graph, o, vid)) {
      return 1;
    }
  } else if (igraphmodule_Vertex_Check(o)) {
    /* Single vertex ID from Vertex object */
    igraphmodule_VertexObject *vo = (igraphmodule_VertexObject*)o;
    *vid = igraphmodule_Vertex_get_index_igraph_integer(vo);
  } else {
    /* Other numeric type that can be converted to an index */
    PyObject* num = PyNumber_Index(o);
    if (num) {
      if (PyLong_Check(num)) {
        if (igraphmodule_PyObject_to_integer_t(num, vid)) {
          Py_DECREF(num);
          return 1;
        }
      } else {
        PyErr_SetString(PyExc_TypeError, "PyNumber_Index() returned invalid type");
        Py_DECREF(num);
        return 1;
      }
      Py_DECREF(num);
    } else {
      PyErr_SetString(PyExc_TypeError, "only non-negative integers, strings or igraph.Vertex objects can be converted to vertex IDs");
      return 1;
    }
  }

  if (*vid < 0) {
    PyErr_Format(PyExc_ValueError, "vertex IDs must be non-negative, got: %" IGRAPH_PRId, *vid);
    return 1;
  }

  return 0;
}

/**
 * \ingroup python_interface_conversion
 * \brief Tries to interpret a Python object as a single vertex ID, leaving
 * the input vertex ID unmodified if the Python object is NULL or None
 *
 * \param o      the Python object
 * \param vid    the vertex ID will be stored here
 * \param graph  the graph that will be used to interpret vertex names
 *               if a string was given in o. It may also be a null pointer
 *               if we don't need name lookups.
 * \return 0 if everything was OK, 1 otherwise
 */
int igraphmodule_PyObject_to_optional_vid(PyObject *o, igraph_int_t *vid, igraph_t *graph) {
  if (o == 0 || o == Py_None) {
    return 0;
  } else {
    return igraphmodule_PyObject_to_vid(o, vid, graph);
  }
}

/**
 * \ingroup python_interface_conversion
 * \brief Tries to interpret a Python object as a list of vertex IDs.
 *
 * \param o      the Python object
 * \param result the vertex IDs will be stored here
 * \param graph  the graph that will be used to interpret vertex names
 *               if a string was given in o. It may also be a null pointer
 *               if we don't need name lookups.
 * \return 0 if everything was OK, 1 otherwise
 */
int igraphmodule_PyObject_to_vid_list(PyObject* o, igraph_vector_int_t* result, igraph_t* graph) {
    PyObject *iterator;
    PyObject *item;
    igraph_int_t vid;

    if (PyBaseString_Check(o)) {
      /* exclude strings; they are iterable but cannot yield meaningful vertex IDs */
      PyErr_SetString(PyExc_TypeError, "cannot convert string to a list of vertex IDs");
      return 1;
    }

    iterator = PyObject_GetIter(o);
    if (iterator == NULL) {
      PyErr_SetString(PyExc_TypeError, "conversion to vertex sequence failed");
      return 1;
    }

    if (igraph_vector_int_init(result, 0)) {
      Py_DECREF(iterator);
      igraphmodule_handle_igraph_error();
      return 1;
    }

    while ((item = PyIter_Next(iterator))) {
      vid = -1;

      if (igraphmodule_PyObject_to_vid(item, &vid, graph)) {
        Py_DECREF(item);
        break;
      }

      Py_DECREF(item);

      if (igraph_vector_int_push_back(result, vid)) {
        igraphmodule_handle_igraph_error();
        /* no need to destroy 'result' here; will be done outside the loop due
         * to PyErr_Occurred */
        break;
      }
    }

    Py_DECREF(iterator);

    if (PyErr_Occurred()) {
      igraph_vector_int_destroy(result);
      return 1;
    }

    return 0;
}

/**
 * \ingroup python_interface_conversion
 * \brief Tries to interpret a Python object as a vertex selector
 *
 * \param o      the Python object
 * \param vs     the \c igraph_vs_t which will contain the result
 * \param graph  an \c igraph_t object which will be used to interpret vertex
 *               names (if the supplied Python object contains strings)
 * \param return_single will be 1 if the selector selected only a single vertex,
 *                      0 otherwise
 * \param single_vid    if the selector selected only a single vertex, the ID
 *                      of the selected vertex will also be returned here.
 *
 * \return 0 if everything was OK, 1 otherwise
 */
int igraphmodule_PyObject_to_vs_t(PyObject *o, igraph_vs_t *vs,
    igraph_t *graph, igraph_bool_t *return_single, igraph_int_t *single_vid) {
  igraph_int_t vid;
  igraph_vector_int_t vector;

  if (o == 0 || o == Py_None) {
    /* Returns a vertex sequence for all vertices */
    if (return_single)
      *return_single = 0;
    igraph_vs_all(vs);
    return 0;
  }

  if (igraphmodule_VertexSeq_Check(o)) {
    /* Returns a vertex sequence from a VertexSeq object */
    igraphmodule_VertexSeqObject *vso = (igraphmodule_VertexSeqObject*)o;

    if (igraph_vs_copy(vs, &vso->vs)) {
      igraphmodule_handle_igraph_error();
      return 1;
    }

    if (return_single) {
      *return_single = 0;
    }

    return 0;
  }

  if (PySlice_Check(o) && graph != 0) {
    /* Returns a vertex sequence from a slice */
    Py_ssize_t no_of_vertices = igraph_vcount(graph);
    Py_ssize_t start, stop, step, slicelength, i;

    if (PySlice_GetIndicesEx(o, no_of_vertices, &start, &stop, &step, &slicelength))
      return 1;

    if (start == 0 && slicelength == no_of_vertices) {
      igraph_vs_all(vs);
    } else {
      if (igraph_vector_int_init(&vector, slicelength)) {
        igraphmodule_handle_igraph_error();
        return 1;
      }

      for (i = 0; i < slicelength; i++, start += step) {
        VECTOR(vector)[i] = start;
      }

      if (igraph_vs_vector_copy(vs, &vector)) {
        igraphmodule_handle_igraph_error();
        igraph_vector_int_destroy(&vector);
        return 1;
      }

      igraph_vector_int_destroy(&vector);
    }

    if (return_single) {
      *return_single = 0;
    }

    return 0;
  }

  if (igraphmodule_PyObject_to_vid(o, &vid, graph)) {
    /* Object cannot be converted to a single vertex ID,
     * assume it is a sequence or iterable */

    if (PyBaseString_Check(o)) {
      /* Special case: strings and unicode objects are sequences, but they
       * will not yield valid vertex IDs */
      return 1;
    }

    /* Clear the exception set by igraphmodule_PyObject_to_vid */
    PyErr_Clear();

    if (igraphmodule_PyObject_to_vid_list(o, &vector, graph)) {
      return 1;
    }

    if (igraph_vs_vector_copy(vs, &vector)) {
      igraphmodule_handle_igraph_error();
      igraph_vector_int_destroy(&vector);
      return 1;
    }

    igraph_vector_int_destroy(&vector);

    if (return_single) {
      *return_single = 0;
    }

    return 0;
  }

  /* The object can be converted into a single vertex ID */
  if (return_single)
    *return_single = true;
  if (single_vid)
    *single_vid = vid;

  igraph_vs_1(vs, vid);

  return 0;
}

/**
 * \ingroup python_interface_conversion
 * \brief Tries to interpret a Python object as a single edge ID
 *
 * \param o      the Python object
 * \param eid    the edge ID will be stored here
 * \param graph  the graph that will be used to interpret vertex names and
 *               indices if o is a tuple. It may also be a null pointer
 *               if we don't want to handle tuples.
 * \return 0 if everything was OK, 1 otherwise
 */
int igraphmodule_PyObject_to_eid(PyObject *o, igraph_int_t *eid, igraph_t *graph) {
  int retval;
  igraph_int_t vid1, vid2;

  if (!o) {
    PyErr_SetString(PyExc_TypeError,
        "only non-negative integers, igraph.Edge objects or tuples of vertex IDs can be "
        "converted to edge IDs");
    return 1;
  } else if (PyLong_Check(o)) {
    /* Single edge ID */
    if (igraphmodule_PyObject_to_integer_t(o, eid)) {
      return 1;
    }
  } else if (igraphmodule_Edge_Check(o)) {
    /* Single edge ID from Edge object */
    igraphmodule_EdgeObject *eo = (igraphmodule_EdgeObject*)o;
    *eid = igraphmodule_Edge_get_index_as_igraph_integer(eo);
  } else if (graph != 0 && PyTuple_Check(o)) {
    PyObject *o1, *o2;

    o1 = PyTuple_GetItem(o, 0);
    if (!o1) {
      return 1;
    }

    o2 = PyTuple_GetItem(o, 1);
    if (!o2) {
      return 1;
    }

    if (igraphmodule_PyObject_to_vid(o1, &vid1, graph)) {
      return 1;
    }
    if (igraphmodule_PyObject_to_vid(o2, &vid2, graph)) {
      return 1;
    }

    retval = igraph_get_eid(graph, eid, vid1, vid2, 1, 0);
    if (retval == IGRAPH_EINVVID) {
      PyErr_Format(
        PyExc_ValueError,
        "no edge from vertex #%" IGRAPH_PRId " to #%" IGRAPH_PRId "; no such vertex ID",
        vid1, vid2
      );
      return 1;
    } else if (retval) {
      igraphmodule_handle_igraph_error();
      return 1;
    }

    if (*eid < 0) {
      PyErr_Format(
        PyExc_ValueError,
        "no edge from vertex #%" IGRAPH_PRId " to #%" IGRAPH_PRId,
        vid1, vid2
      );
      return 1;
    }
  } else {
    /* Other numeric type that can be converted to an index */
    PyObject* num = PyNumber_Index(o);
    if (num) {
      if (PyLong_Check(num)) {
        if (igraphmodule_PyObject_to_integer_t(num, eid)) {
          Py_DECREF(num);
          return 1;
        }
      } else {
        PyErr_SetString(PyExc_TypeError, "PyNumber_Index() returned invalid type");
        Py_DECREF(num);
        return 1;
      }
      Py_DECREF(num);
    } else {
      PyErr_SetString(PyExc_TypeError,
          "only non-negative integers, igraph.Edge objects or tuples of vertex IDs can be "
          "converted to edge IDs");
      return 1;
    }
  }

  if (*eid < 0) {
    PyErr_Format(PyExc_ValueError, "edge IDs must be non-negative, got: %" IGRAPH_PRId, *eid);
    return 1;
  }

  return 0;
}

/**
 * \ingroup python_interface_conversion
 * \brief Tries to interpret a Python object as an edge selector
 *
 * \param o the Python object
 * \param vs the \c igraph_es_t which will contain the result
 * \param graph  an \c igraph_t object which will be used to interpret vertex
 *               names and tuples (if the supplied Python object contains them)
 * \param return_single will be 1 if the selector selected only a single edge,
 * 0 otherwise
 * \return 0 if everything was OK, 1 otherwise
 */
int igraphmodule_PyObject_to_es_t(PyObject *o, igraph_es_t *es, igraph_t *graph,
                  igraph_bool_t *return_single) {
  igraph_int_t eid;
  igraph_vector_int_t vector;

  if (o == 0 || o == Py_None) {
    /* Returns an edge sequence for all edges */
    if (return_single)
      *return_single = 0;
    igraph_es_all(es, IGRAPH_EDGEORDER_ID);
    return 0;
  }

  if (igraphmodule_EdgeSeq_Check(o)) {
    /* Returns an edge sequence from an EdgeSeq object */
    igraphmodule_EdgeSeqObject *eso = (igraphmodule_EdgeSeqObject*)o;
    if (igraph_es_copy(es, &eso->es)) {
      igraphmodule_handle_igraph_error();
      return 1;
    }
    if (return_single)
      *return_single = 0;
    return 0;
  }

  if (igraphmodule_PyObject_to_eid(o, &eid, graph)) {
    /* Object cannot be converted to a single edge ID,
     * assume it is a sequence or iterable */

    PyObject *iterator;
    PyObject *item;

    /* Clear the exception set by igraphmodule_PyObject_to_eid */
    PyErr_Clear();

    iterator = PyObject_GetIter(o);

    if (iterator == NULL) {
      PyErr_SetString(PyExc_TypeError, "conversion to edge sequence failed");
      return 1;
    }

    if (igraph_vector_int_init(&vector, 0)) {
      igraphmodule_handle_igraph_error();
      return 1;
    }

    while ((item = PyIter_Next(iterator))) {
      eid = -1;

      if (igraphmodule_PyObject_to_eid(item, &eid, graph)) {
        break;
      }

      Py_DECREF(item);

      if (igraph_vector_int_push_back(&vector, eid)) {
        igraphmodule_handle_igraph_error();
        /* no need to destroy 'vector' here; will be done outside the loop due
         * to PyErr_Occurred */
        break;
      }
    }

    Py_DECREF(iterator);

    if (PyErr_Occurred()) {
      igraph_vector_int_destroy(&vector);
      return 1;
    }

    if (igraph_vector_int_size(&vector) > 0) {
      igraph_es_vector_copy(es, &vector);
    } else {
      igraph_es_none(es);
    }

    igraph_vector_int_destroy(&vector);

    if (return_single) {
      *return_single = 0;
    }

    return 0;
  }

  /* The object can be converted into a single edge ID */
  if (return_single) {
    *return_single = true;
  }

  /*
  if (single_eid)
    *single_eid = eid;
  */

  igraph_es_1(es, eid);

  return 0;
}

/**
 * \ingroup python_interface_conversion
 * \brief Tries to interpret a Python object as a numeric attribute value list
 *
 * \param o the Python object
 * \param v the \c igraph_vector_t which will contain the result
 * \param g a \c igraphmodule_GraphObject object or \c NULL - used when the
 * provided Python object is not a list and we're trying to interpret it as
 * an attribute name.
 * \param type the attribute type (graph = 0, vertex = 1, edge = 2) to be used
 * \param def default value if the attribute name supplied is \c None
 * if \c o is not a list.
 * \return 0 if everything was OK, 1 otherwise
 *
 * If the Python object is not a list, tries to interpret it as an attribute
 * name.
 */
int igraphmodule_PyObject_to_attribute_values(PyObject *o,
                          igraph_vector_t *v,
                          igraphmodule_GraphObject* g,
                          int type, igraph_real_t def) {
  PyObject* list = o;
  Py_ssize_t i, n;

  if (o == NULL) {
    return 1;
  }

  if (o == Py_None) {
    if (type == ATTRHASH_IDX_VERTEX) {
      n = igraph_vcount(&g->g);
    } else if (type == ATTRHASH_IDX_EDGE) {
      n = igraph_ecount(&g->g);
    } else {
      n = 1;
    }

    if (igraph_vector_init(v, n)) {
      return 1;
    }

    igraph_vector_fill(v, def);
    return 0;
  }

  if (!PyList_Check(o)) {
    list = PyDict_GetItem(((PyObject**)g->g.attr)[type], o);
    if (!list) {
      if (!PyErr_Occurred())
    PyErr_SetString(PyExc_KeyError, "Attribute does not exist");
      return 1;
    }
  }

  n = PyList_Size(list);
  if (igraph_vector_init(v, n)) {
    return 1;
  }

  for (i = 0; i < n; i++) {
    PyObject *item = PyList_GetItem(list, i);
    if (!item) {
      igraph_vector_destroy(v);
      return 1;
    }

    if (PyLong_Check(item)) {
      VECTOR(*v)[i] = PyLong_AsLong(item);
    } else if (PyFloat_Check(item)) {
      VECTOR(*v)[i] = PyFloat_AsDouble(item);
    } else {
      VECTOR(*v)[i] = def;
    }
  }

  return 0;
}

int igraphmodule_PyObject_to_vpath_or_epath(PyObject *object, igraph_bool_t *use_edges) {
  if (object == 0 || object == Py_None) {
    *use_edges = 0;
    return 0;
  }

  if (!PyUnicode_Check(object)) {
    PyErr_SetString(PyExc_ValueError, "output argument must be \"vpath\" or \"epath\"");
    return 1;
  }

  if (PyUnicode_IsEqualToASCIIString(object, "vpath")) {
    *use_edges = 0;
    return 0;
  } else if (PyUnicode_IsEqualToASCIIString(object, "epath")) {
    *use_edges = 1;
    return 0;
  } else {
    PyErr_SetString(PyExc_ValueError, "output argument must be \"vpath\" or \"epath\"");
    return 1;
  }
}

int igraphmodule_PyObject_to_drl_options_t(PyObject *obj,
    igraph_layout_drl_options_t *options) {
  int retval;

  if (obj == Py_None) {
    retval = igraph_layout_drl_options_init(options, IGRAPH_LAYOUT_DRL_DEFAULT);
  } else if (PyUnicode_Check(obj)) {
    /* We have a string, so we are using a preset */
    igraph_layout_drl_default_t def=IGRAPH_LAYOUT_DRL_DEFAULT;
    if (PyUnicode_IsEqualToASCIIString(obj, "default"))
      def=IGRAPH_LAYOUT_DRL_DEFAULT;
    else if (PyUnicode_IsEqualToASCIIString(obj, "coarsen"))
      def=IGRAPH_LAYOUT_DRL_COARSEN;
    else if (PyUnicode_IsEqualToASCIIString(obj, "coarsest"))
      def=IGRAPH_LAYOUT_DRL_COARSEST;
    else if (PyUnicode_IsEqualToASCIIString(obj, "refine"))
      def=IGRAPH_LAYOUT_DRL_REFINE;
    else if (PyUnicode_IsEqualToASCIIString(obj, "final"))
      def=IGRAPH_LAYOUT_DRL_FINAL;
    else {
      PyErr_SetString(PyExc_ValueError, "unknown DrL template name. Must be one of: default, coarsen, coarsest, refine, final");
      return 1;
    }
    retval = igraph_layout_drl_options_init(options, def);
  } else {
    retval = igraph_layout_drl_options_init(options, IGRAPH_LAYOUT_DRL_DEFAULT);
#define CONVERT_DRL_OPTION(OPTION, TYPE) do { \
      PyObject *o1; \
      if (PyMapping_Check(obj)) { \
        o1 = PyMapping_GetItemString(obj, #OPTION); \
        igraphmodule_PyObject_to_##TYPE##_t(o1, &options->OPTION); \
        Py_XDECREF(o1); \
      } \
      o1 = PyObject_GetAttrString(obj, #OPTION); \
      igraphmodule_PyObject_to_##TYPE##_t(o1, &options->OPTION); \
      Py_XDECREF(o1); \
    } while (0)
#define CONVERT_DRL_OPTION_BLOCK(NAME) do { \
    CONVERT_DRL_OPTION(NAME##_iterations, integer); \
    CONVERT_DRL_OPTION(NAME##_temperature, real); \
    CONVERT_DRL_OPTION(NAME##_attraction, real); \
    CONVERT_DRL_OPTION(NAME##_damping_mult, real); \
    } while (0)

    if (!retval) {
      CONVERT_DRL_OPTION(edge_cut, real);
      CONVERT_DRL_OPTION_BLOCK(init);
      CONVERT_DRL_OPTION_BLOCK(liquid);
      CONVERT_DRL_OPTION_BLOCK(expansion);
      CONVERT_DRL_OPTION_BLOCK(cooldown);
      CONVERT_DRL_OPTION_BLOCK(crunch);
      CONVERT_DRL_OPTION_BLOCK(simmer);

      PyErr_Clear();
    }

#undef CONVERT_DRL_OPTION
#undef CONVERT_DRL_OPTION_BLOCK
  }

  if (retval) {
    igraphmodule_handle_igraph_error();
    return 1;
  }

  return 0;
}


int igraphmodule_i_PyObject_pair_to_attribute_combination_record_t(
    PyObject* name, PyObject* value,
    igraph_attribute_combination_record_t *result) {
  if (igraphmodule_PyObject_to_attribute_combination_type_t(value, &result->type))
    return 1;

  if (result->type == IGRAPH_ATTRIBUTE_COMBINE_FUNCTION) {
    result->func = (void*) value;
  } else {
    result->func = 0;
  }

  if (name == Py_None)
    result->name = 0;
  else if (!PyUnicode_Check(name)) {
    PyErr_SetString(PyExc_TypeError, "keys must be strings or None in attribute combination specification dicts");
    return 1;
  } else {
    result->name = PyUnicode_CopyAsString(name);
  }

  return 0;
}

/**
 * \brief Converts a Python object to an \c igraph_attribute_combination_t
 *
 * Raises suitable Python exceptions when needed.
 *
 * An \c igraph_attribute_combination_t specifies how the attributes of multiple
 * vertices/edges should be combined when they are collapsed into a single vertex
 * or edge (e.g., when simplifying a graph). For each attribute, one can specify
 * a Python callable object to call or one of a list of recognised strings which
 * map to simple functions. The recognised strings are as follows:
 *
 *   - \c "ignore"  - the attribute will be ignored
 *   - \c "sum"     - the attribute values will be added
 *   - \c "prod"    - the product of the attribute values will be taken
 *   - \c "min"     - the minimum attribute value will be used
 *   - \c "max"     - the maximum attribute value will be used
 *   - \c "random"  - a random value will be selected
 *   - \c "first"   - the first value encountered will be selected
 *   - \c "last"    - the last value encountered will be selected
 *   - \c "mean"    - the mean of the attributes will be selected
 *   - \c "median"  - the median of the attributes will be selected
 *   - \c "concat"  - the attribute values will be concatenated
 *
 * The Python object being converted must either be a string, a callable or a dict.
 * If a string is given, it is considered as an \c igraph_attribute_combination_t
 * object that combines all attributes according to the function given by that
 * string. If a callable is given, it is considered as an
 * \c igraph_attribute_combination_t that combines all attributes by calling the
 * callable and taking its return value. If a dict is given, its key-value pairs
 * are iterated, the keys specify the attribute names (a key of None means all
 * explicitly not specified attributes), the values specify the functions to
 * call for those attributes.
 *
 * \param object the Python object to be converted
 * \param result the result is returned here. It must be an uninitialized
 *   \c igraph_attribute_combination_t object, it will be initialized accordingly.
 *   It is the responsibility of the caller to
 * \return 0 if everything was OK, 1 otherwise
 */
int igraphmodule_PyObject_to_attribute_combination_t(PyObject* object,
    igraph_attribute_combination_t *result) {
  igraph_attribute_combination_record_t rec;

  if (igraph_attribute_combination_init(result)) {
    igraphmodule_handle_igraph_error();
    return 1;
  }

  if (object == Py_None) {
    return 0;
  }

  rec.type = IGRAPH_ATTRIBUTE_COMBINE_IGNORE;

  if (PyDict_Check(object)) {
    /* a full-fledged dict was passed */
    PyObject *key, *value;
    Py_ssize_t pos = 0;

    while (PyDict_Next(object, &pos, &key, &value)) {
      if (igraphmodule_i_PyObject_pair_to_attribute_combination_record_t(key, value, &rec)) {
        igraph_attribute_combination_destroy(result);
        return 1;
      }
      igraph_attribute_combination_add(result, rec.name, rec.type, rec.func);
      free((char*)rec.name);   /* was allocated in pair_to_attribute_combination_record_t above */
    }
  } else {
    /* assume it is a string or callable */
    if (igraphmodule_i_PyObject_pair_to_attribute_combination_record_t(Py_None, object, &rec)) {
      igraph_attribute_combination_destroy(result);
      return 1;
    }

    igraph_attribute_combination_add(result, 0, rec.type, rec.func);
    free((char*)rec.name);   /* was allocated in pair_to_attribute_combination_record_t above */
  }

  return 0;
}

/**
 * \ingroup python_interface_conversion
 * \brief Converts a Python object to an igraph \c igraph_pagerank_algo_t
 */
int igraphmodule_PyObject_to_pagerank_algo_t(PyObject *o, igraph_pagerank_algo_t *result) {
  static igraphmodule_enum_translation_table_entry_t pagerank_algo_tt[] = {
        {"prpack", IGRAPH_PAGERANK_ALGO_PRPACK},
        {"arpack", IGRAPH_PAGERANK_ALGO_ARPACK},
        {0,0}
    };
  TRANSLATE_ENUM_WITH(pagerank_algo_tt);
}

/**
 * \ingroup python_interface_conversion
 * \brief Converts a Python object to an igraph \c igraph_metric_t
 */
int igraphmodule_PyObject_to_metric_t(PyObject *o, igraph_metric_t *result) {
  static igraphmodule_enum_translation_table_entry_t metric_tt[] = {
        {"euclidean", IGRAPH_METRIC_EUCLIDEAN},
        {"l2", IGRAPH_METRIC_L2}, /* alias to the previous */
        {"manhattan", IGRAPH_METRIC_MANHATTAN},
        {"l1", IGRAPH_METRIC_L1}, /* alias to the previous */
        {0,0}
    };
  TRANSLATE_ENUM_WITH(metric_tt);
}

/**
 * \ingroup python_interface_conversion
 * \brief Converts a Python object to an igraph \c igraph_edge_type_sw_t
 */
int igraphmodule_PyObject_to_edge_type_sw_t(PyObject *o, igraph_edge_type_sw_t *result) {
  static igraphmodule_enum_translation_table_entry_t edge_type_sw_tt[] = {
        {"simple", IGRAPH_SIMPLE_SW},
        {"loops", IGRAPH_LOOPS_SW},
        {"multi", IGRAPH_MULTI_SW},
        {"all", IGRAPH_LOOPS_SW | IGRAPH_MULTI_SW},
        {0,0}
    };
  TRANSLATE_ENUM_STRICTLY_WITH(edge_type_sw_tt);
}

/**
 * \ingroup python_interface_conversion
 * \brief Converts a Python object to an igraph \c igraph_realize_degseq_t
 */
int igraphmodule_PyObject_to_realize_degseq_t(PyObject *o, igraph_realize_degseq_t *result) {
  static igraphmodule_enum_translation_table_entry_t realize_degseq_tt[] = {
        {"smallest", IGRAPH_REALIZE_DEGSEQ_SMALLEST},
        {"largest", IGRAPH_REALIZE_DEGSEQ_LARGEST},
        {"index", IGRAPH_REALIZE_DEGSEQ_INDEX},
        {0,0}
    };
  TRANSLATE_ENUM_STRICTLY_WITH(realize_degseq_tt);
}

/**
 * \ingroup python_interface_conversion
 * \brief Converts a Python object to an igraph \c igraph_random_tree_t
 */
int igraphmodule_PyObject_to_random_tree_t(PyObject *o, igraph_random_tree_t *result) {
  static igraphmodule_enum_translation_table_entry_t random_tree_tt[] = {
        {"prufer", IGRAPH_RANDOM_TREE_PRUFER},
        {"lerw", IGRAPH_RANDOM_TREE_LERW},
        {0,0}
    };
  TRANSLATE_ENUM_STRICTLY_WITH(random_tree_tt);
}
