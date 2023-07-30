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

#include "utils.h"

/************************ Miscellaneous functions *************************/

/**
 * Helper function that automatically selects a shortest path algorithm based on
 * a graph, its weight vector and the source vertex set (if any).
 */
igraphmodule_shortest_path_algorithm_t igraphmodule_select_shortest_path_algorithm(
  const igraph_t* graph, const igraph_vector_t* weights, const igraph_vs_t* from_vs,
  igraph_neimode_t mode, igraph_bool_t allow_johnson
) {
  igraph_error_t retval;
  igraph_integer_t vs_size;

  /* Select the most suitable algorithm */
  if (weights && igraph_vector_size(weights) > 0) {
    if (igraph_vector_min(weights) >= 0) {
      /* Only positive weights, use Dijkstra's algorithm */
      return IGRAPHMODULE_SHORTEST_PATH_ALGORITHM_DIJKSTRA;
    } else if (allow_johnson) {
      /* There are negative weights. For a small number of sources, use Bellman-Ford.
       * Otherwise, use Johnson's algorithm */
      if (from_vs) {
        retval = igraph_vs_size(graph, from_vs, &vs_size);
      } else {
        retval = IGRAPH_SUCCESS;
        vs_size = IGRAPH_INTEGER_MAX;
      }
      if (retval == IGRAPH_SUCCESS) {
        if (vs_size <= 100 || mode != IGRAPH_OUT) {
          return IGRAPHMODULE_SHORTEST_PATH_ALGORITHM_BELLMAN_FORD;
        } else {
          return IGRAPHMODULE_SHORTEST_PATH_ALGORITHM_JOHNSON;
        }
      } else {
        /* Error while calling igraph_vs_size(). Use Bellman-Ford. */
        return IGRAPHMODULE_SHORTEST_PATH_ALGORITHM_BELLMAN_FORD;
      }
    } else {
      /* Johnson's algorithm is disallowed, use Bellman-Ford */
      return IGRAPHMODULE_SHORTEST_PATH_ALGORITHM_BELLMAN_FORD;
    }
  } else {
    /* No weights or empty weight vector, use Dijstra, which should fall back to
     * an unweighted algorithm */
    return IGRAPHMODULE_SHORTEST_PATH_ALGORITHM_DIJKSTRA;
  }
}
