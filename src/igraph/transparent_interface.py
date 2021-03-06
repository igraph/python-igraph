# vim:ts=4:sw=4:sts=4:et
# -*- coding: utf-8 -*-
"""Transparent interface to other graph libraries."""

__all__ = ('TransparentAPI', )

__docformat__ = "restructuredtext en"
__license__ = """
Copyright (C) 2006-2012  Tamás Nepusz <ntamas@gmail.com>
Pázmány Péter sétány 1/a, 1117 Budapest, Hungary

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
"""

from igraph import Graph

api_functions = {
    'adhesion': {
        'input': ('vertex', 'vertex', 'passthrough'),
        'target': Graph.adhesion,
    },
    'incident': {
        'input': ('vertex', 'passthrough'),
        'return': 'edges',
        'target': Graph.incident,
    }
    #TODO: obviously more
}


def infer_return_type(function):
    if function not in api_functions:
        raise AttributeError(
            "This function is not part of igraph's transparent API"
        )

    # Passthrough is the default
    return api_functions[function].get('return', 'passthrogh')


def infer_arg_type(function, pos=None, key=None):
    if function not in api_functions:
        raise AttributeError(
            "This function is not part of igraph's transparent API",
        )

    if (pos is None) and (key is None):
        raise ValueError('Either pos or key must be specified')

    if (pos is not None) and (key is not None):
        raise ValueError('Only one of pos or key must be specified')

    if key is not None:
        # Figure out the arg position for this one... this one is tricky
        docstring = api_functions[function]['target'].__doc__
        text_signature = docstring.split('\n')[0]
        if key + '=' not in text_signature:
            raise ValueError('Keyword argument not found')

        pos = text_signature[:text_signature.find(key + '=')].count('=')

    return api_functions[function]['input'][pos]


# The main issue is renaming vertices/edges for the function arguments
class TransparentAPIConverter:
    def __init__(self, function, args, kwargs):
        self.function = function
        self.args = args
        self.kwargs = kwargs

    @staticmethod
    def convert_input_networkx(graph, args):
        import networkx

        if not isinstance(graph, networkx.Graph):
            raise TypeError

        graph_conv = Graph.from_networkx(graph)

        # Prepare some structures
        vd = {v: i for i, v in enumerate(graph_conv.vs['_nx_name'])}

        # Converting arguments
        args_conv = []
        for arg in args:
            arg_conv = dict(arg)
            if arg['type'] == 'vertex':
                arg_conv['value'] = vd[arg['value']]
            elif arg['type'] == 'vertices':
                arg_conv['value'] = [vd[x] for x in arg['value']]
            args_conv.append(arg_conv)

        return {
            'graph': graph_conv,
            'args': args_conv,
            'input_format': 'networkx',
        }

    def convert_input(self, args_struct):
        converted = None
        convert_order = [
            self.convert_input_networkx,
        ]
        for convert_fun in convert_order:
            try:
                converted = convert_fun(self.graph, args_struct)
            except (ImportError, TypeError):
                continue
            break
        else:
            raise TypeError('Could not import graph into igraph')

        return converted

    def convert_output_networkx(self, result):
        def conv_vertex(idx):
            return self.graph_conv.vs[idx]['_nx_name']

        ret_type = infer_return_type(self.function)

        # Floats are never vertex indices and such. This covers many, many cases
        if ret_type == 'passthrough':
            return result

        # Subgraphs and such: just convert back
        if ret_type == 'graph':
            return result.to_networkx()

        # Vertex index, convert to vertex name
        if ret_type == 'vertex_index':
            return conv_vertex(result)

        # List of vertex indices, convert each to name
        if ret_type == 'vertex_indices':
            return [conv_vertex(x) for x in result]

        # Edge index, convert to edge name
        if ret_type == 'edge':
            edge = self.graph_conv.es[result]
            vertices = [edge.source, edge.target]
            vertices_conv = [conv_vertex(x) for x in vertices]
            # Networkx uses tuples (they need to be hashable)
            return tuple(vertices_conv)

        # List of edge indices
        if ret_type == 'edges':
            edges = []
            for res in result:
                edge = self.graph_conv.es[res]
                vertices = [edge.source, edge.target]
                vertices_conv = [conv_vertex(x) for x in vertices]
                # Networkx uses tuples (they need to be hashable)
                edges.append(tuple(vertices_conv))
            return edges

        # Default: do not convert
        print('WARNING: could not convert igraph function output back')
        return result

    def convert_output(self, result):
        '''Convert output of an igraph function back to the caller space'''

        convert_dict = {
            'networkx': self.convert_output_networkx,
            #'graph_tool': convert_output_graph_tool,
        }

        return convert_dict[self.input_format](result)

    def run_api_call(self):

        # For now, the first argument must be a graph
        self.graph = graph = self.args[0]
        args = [] if len(self.args) == 1 else self.args[1:]

        # Create args structure
        args_struct = []
        for i, arg in enumerate(args):
            argd = {
                'kw': None,
                'value': arg,
                'type': infer_arg_type(self.function, pos=i),
            }
            args_struct.append(argd)
        # Merge kwargs in the mix
        for key, arg in self.kwargs.items():
            argd = {
                'kw': key,
                'value': arg,
                'type': infer_arg_type(self.function, key=key),
            }
            args_struct.append(argd)

        # Convert graph and args
        converted = self.convert_input(args_struct)
        self.input_format = converted['input_format']
        self.graph_conv = graph_conv = converted['graph']
        args_conv = []
        kwargs_conv = {}
        for argd in converted['args']:
            if argd['kw'] is None:
                args_conv.append(argd['value'])
            else:
                kwargs_conv[argd['kw']] = argd['value']

        # Run function or method
        import inspect
        # Check if the target function is supposed to be a bound method
        function = api_functions[self.function]['target']
        if inspect.isfunction(function):
            result = function(graph_conv, *args_conv, **kwargs_conv)
        else:
            # Call bound version of method
            result = getattr(graph_conv, self.function)(*args_conv, **kwargs_conv)

        # Convert output if needed
        result_conv = self.convert_output(result)

        return result_conv


class TransparentAPI:
    """Transparent API to run igraph functions.

    For the list of supported functions, run:

    >>> from igraph import TransparentAPI
    >>> print(TransparentAPI.functions)
    """
    functions = list(api_functions.keys())

    def __repr__(self):
        return str(self.functions)


for funcname, dic in api_functions.items():
    def tmp_function(*args, **kwargs):
        return TransparentAPIConverter(funcname, args, kwargs).run_api_call()
    setattr(TransparentAPI, funcname, tmp_function)
