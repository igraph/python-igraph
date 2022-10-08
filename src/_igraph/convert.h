/* -*- mode: C -*-  */
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

/************************ Miscellaneous functions *************************/

/** \defgroup python_interface_conversion Converting between Python and igraph data types
 * \ingroup python_interface */

#ifndef PYTHON_CONVERT_H
#define PYTHON_CONVERT_H

#include "preamble.h"

#include <igraph_constants.h>
#include <igraph_types.h>
#include "graphobject.h"

typedef enum {
  IGRAPHMODULE_TYPE_INT = 0,
  IGRAPHMODULE_TYPE_FLOAT = 1,
  IGRAPHMODULE_TYPE_FLOAT_IF_FRACTIONAL_ELSE_INT = 2
} igraphmodule_conv_t;

typedef struct {
  const char* name;
  int value;
} igraphmodule_enum_translation_table_entry_t;

/* Conversion from PyObject to enum types */

int igraphmodule_PyObject_to_enum(PyObject *o,
  igraphmodule_enum_translation_table_entry_t *table, int *result);
int igraphmodule_PyObject_to_enum_strict(PyObject *o,
  igraphmodule_enum_translation_table_entry_t *table, int *result);
int igraphmodule_PyObject_to_add_weights_t(PyObject *o, igraph_add_weights_t *result);
int igraphmodule_PyObject_to_adjacency_t(PyObject *o, igraph_adjacency_t *result);
int igraphmodule_PyObject_to_attribute_combination_type_t(PyObject* o,
    igraph_attribute_combination_type_t *type);
int igraphmodule_PyObject_to_barabasi_algorithm_t(PyObject *o,
  igraph_barabasi_algorithm_t *result);
int igraphmodule_PyObject_to_bliss_sh_t(PyObject *o, igraph_bliss_sh_t *result);
int igraphmodule_PyObject_to_community_comparison_t(PyObject *obj,
                  igraph_community_comparison_t *result);
int igraphmodule_PyObject_to_connectedness_t(PyObject *o, igraph_connectedness_t *result);
int igraphmodule_PyObject_to_degseq_t(PyObject *o, igraph_degseq_t *result);
int igraphmodule_PyObject_to_fas_algorithm_t(PyObject *o, igraph_fas_algorithm_t *result);
int igraphmodule_PyObject_to_get_adjacency_t(PyObject *o, igraph_get_adjacency_t *result);
int igraphmodule_PyObject_to_laplacian_normalization_t(PyObject *o, igraph_laplacian_normalization_t *result);
int igraphmodule_PyObject_to_layout_grid_t(PyObject *o, igraph_layout_grid_t *result);
int igraphmodule_PyObject_to_loops_t(PyObject *o, igraph_loops_t *result);
int igraphmodule_PyObject_to_neimode_t(PyObject *o, igraph_neimode_t *result);
int igraphmodule_PyObject_to_pagerank_algo_t(PyObject *o, igraph_pagerank_algo_t *result);
int igraphmodule_PyObject_to_edge_type_sw_t(PyObject *o, igraph_edge_type_sw_t *result);
int igraphmodule_PyObject_to_realize_degseq_t(PyObject *o, igraph_realize_degseq_t *result);
int igraphmodule_PyObject_to_random_tree_t(PyObject *o, igraph_random_tree_t *result);
int igraphmodule_PyObject_to_random_walk_stuck_t(PyObject *o, igraph_random_walk_stuck_t *result);
int igraphmodule_PyObject_to_reciprocity_t(PyObject *o, igraph_reciprocity_t *result);
int igraphmodule_PyObject_to_rewiring_t(PyObject *o, igraph_rewiring_t *result);
int igraphmodule_PyObject_to_spinglass_implementation_t(PyObject *o, igraph_spinglass_implementation_t *result);
int igraphmodule_PyObject_to_spincomm_update_t(PyObject *o, igraph_spincomm_update_t *result);
int igraphmodule_PyObject_to_star_mode_t(PyObject *o, igraph_star_mode_t *result);
int igraphmodule_PyObject_to_subgraph_implementation_t(PyObject *o, igraph_subgraph_implementation_t *result);
int igraphmodule_PyObject_to_to_directed_t(PyObject *o, igraph_to_directed_t *result);
int igraphmodule_PyObject_to_to_undirected_t(PyObject *o, igraph_to_undirected_t *result);
int igraphmodule_PyObject_to_transitivity_mode_t(PyObject *o, igraph_transitivity_mode_t *result);
int igraphmodule_PyObject_to_tree_mode_t(PyObject *o, igraph_tree_mode_t *result);
int igraphmodule_PyObject_to_vconn_nei_t(PyObject *o, igraph_vconn_nei_t *result);

/* Conversion from PyObject to igraph types */

int igraphmodule_PyObject_to_integer_t(PyObject *object, igraph_integer_t *v);
int igraphmodule_PyObject_to_real_t(PyObject *object, igraph_real_t *v);
int igraphmodule_PyObject_to_igraph_t(PyObject *o, igraph_t **result);

int igraphmodule_PyObject_to_vector_t(PyObject *list, igraph_vector_t *v,
		igraph_bool_t need_non_negative);
int igraphmodule_PyObject_float_to_vector_t(PyObject *list, igraph_vector_t *v);
int igraphmodule_PyObject_to_vector_int_t(PyObject *list, igraph_vector_int_t *v);
int igraphmodule_PyObject_to_vector_bool_t(PyObject *list, igraph_vector_bool_t *v);
int igraphmodule_PyObject_to_vector_ptr_t(PyObject *list, igraph_vector_ptr_t *v,
		igraph_bool_t need_non_negative);
int igraphmodule_PyObject_to_vector_int_ptr_t(PyObject *list, igraph_vector_ptr_t *v);
int igraphmodule_PyObject_to_vector_list_t(PyObject *list, igraph_vector_list_t *v);
int igraphmodule_PyObject_to_vector_int_list_t(PyObject *list, igraph_vector_int_list_t *v);

int igraphmodule_PyObject_to_edgelist(
    PyObject *list, igraph_vector_int_t *v, igraph_t *graph,
    igraph_bool_t *list_is_owned
);

int igraphmodule_PyList_to_matrix_t(PyObject *o, igraph_matrix_t *m);
int igraphmodule_PyList_to_matrix_t_with_minimum_column_count(PyObject *o, igraph_matrix_t *m, int min_cols);
int igraphmodule_PyList_to_matrix_int_t(PyObject *o, igraph_matrix_int_t *m);
int igraphmodule_PyList_to_matrix_int_t_with_minimum_column_count(PyObject *o, igraph_matrix_int_t *m, int min_cols);
PyObject* igraphmodule_strvector_t_to_PyList(igraph_strvector_t *v);
int igraphmodule_PyList_to_strvector_t(PyObject* v, igraph_strvector_t *result);
int igraphmodule_PyList_to_existing_strvector_t(PyObject* v, igraph_strvector_t *result);
int igraphmodule_append_PyIter_of_graphs_to_vector_ptr_t(PyObject *it,
		igraph_vector_ptr_t *v);
int igraphmodule_append_PyIter_of_graphs_to_vector_ptr_t_with_type(PyObject *it,
		igraph_vector_ptr_t *v, PyTypeObject **g_type);
int igraphmodule_PyObject_to_vid(PyObject *o, igraph_integer_t *vid, igraph_t *graph);
int igraphmodule_PyObject_to_vs_t(PyObject *o, igraph_vs_t *vs,
                  igraph_t *graph, igraph_bool_t *return_single,
				  igraph_integer_t *single_vid);
int igraphmodule_PyObject_to_eid(PyObject *o, igraph_integer_t *eid, igraph_t *graph);
int igraphmodule_PyObject_to_es_t(PyObject *o, igraph_es_t *es, igraph_t *graph,
				  igraph_bool_t *return_single);
int igraphmodule_PyObject_to_attribute_values(PyObject *o,
					      igraph_vector_t *v,
					      igraphmodule_GraphObject* g,
					      int type,
					      igraph_real_t def);
int igraphmodule_PyObject_to_drl_options_t(PyObject *obj,
                  igraph_layout_drl_options_t *options);
int igraphmodule_PyObject_to_attribute_combination_t(PyObject* object,
    igraph_attribute_combination_t *type);
int igraphmodule_PyObject_to_eigen_algorithm_t(PyObject *object,
																							 igraph_eigen_algorithm_t *a);
int igraphmodule_PyObject_to_eigen_which_t(PyObject *object,
																					 igraph_eigen_which_t *w);
int igraphmodule_PyObject_to_vpath_or_epath(PyObject *object, igraph_bool_t *use_edges);

/* Conversion from attributes to igraph types */

int igraphmodule_attrib_to_vector_t(PyObject *o, igraphmodule_GraphObject *self,
  igraph_vector_t **vptr, int attr_type);
int igraphmodule_attrib_to_vector_int_t(PyObject *o, igraphmodule_GraphObject *self,
  igraph_vector_int_t **vptr, int attr_type);
int igraphmodule_attrib_to_vector_bool_t(PyObject *o, igraphmodule_GraphObject *self,
  igraph_vector_bool_t **vptr, int attr_type);

/* Conversion from igraph types to PyObjects */

PyObject* igraphmodule_integer_t_to_PyObject(igraph_integer_t value);
PyObject* igraphmodule_real_t_to_PyObject(igraph_real_t value, igraphmodule_conv_t type);

PyObject* igraphmodule_vector_bool_t_to_PyList(const igraph_vector_bool_t *v);
PyObject* igraphmodule_vector_t_to_PyList(const igraph_vector_t *v, igraphmodule_conv_t type);
PyObject* igraphmodule_vector_t_to_PyTuple(const igraph_vector_t *v,  igraphmodule_conv_t type);
PyObject* igraphmodule_vector_int_t_to_PyTuple(const igraph_vector_int_t *v);
PyObject* igraphmodule_vector_int_t_pair_to_PyList(const igraph_vector_int_t *v1,
        const igraph_vector_int_t *v2);
PyObject* igraphmodule_vector_int_t_to_PyList_of_fixed_length_tuples(
        const igraph_vector_int_t *v, Py_ssize_t tuple_len);
PyObject* igraphmodule_vector_int_t_to_PyList_with_nan(const igraph_vector_int_t *v, const igraph_integer_t nanvalue);
PyObject* igraphmodule_vector_ptr_t_to_PyList(const igraph_vector_ptr_t *v,
        igraphmodule_conv_t type);
PyObject* igraphmodule_vector_int_ptr_t_to_PyList(const igraph_vector_ptr_t *v);
PyObject* igraphmodule_vector_list_t_to_PyList(const igraph_vector_list_t *v); 
PyObject* igraphmodule_vector_int_list_t_to_PyList(const igraph_vector_int_list_t *v); 
PyObject* igraphmodule_vector_int_list_t_to_PyList_of_tuples(const igraph_vector_int_list_t *v); 
PyObject* igraphmodule_graph_list_t_to_PyList(igraph_graph_list_t *v, PyTypeObject *type);
PyObject* igraphmodule_vector_int_t_to_PyList(const igraph_vector_int_t *v);
PyObject* igraphmodule_matrix_t_to_PyList(const igraph_matrix_t *m,
        igraphmodule_conv_t type);
PyObject* igraphmodule_matrix_int_t_to_PyList(const igraph_matrix_int_t *m);
#endif
