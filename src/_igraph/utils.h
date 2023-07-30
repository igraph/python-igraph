/* -*- mode: C -*-  */
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

#ifndef IGRAPHMODULE_UTILS_H
#define IGRAPHMODULE_UTILS_H

#include "preamble.h"

#include <igraph_constants.h>
#include <igraph_types.h>
#include "convert.h"
#include "graphobject.h"

/************************ Miscellaneous functions *************************/

igraphmodule_shortest_path_algorithm_t igraphmodule_select_shortest_path_algorithm(
  const igraph_t* graph, const igraph_vector_t* weights, const igraph_vs_t* from_vs,
  igraph_neimode_t mode, igraph_bool_t allow_johnson
);

#endif
