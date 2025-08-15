import pandas as pd
import requests
import io
import os
import igraph as ig

def load_got_network(local_path: str = './game_of_thrones/got-s1-edges.csv', url: str = None):
    """
    Loads the Game of Thrones network dataset from a local CSV file. If the file is not found,
    it downloads the data from a public GitHub repository. The function can also export
    the resulting graph to a GraphML file.

    Args:
        local_path (str, optional): The path to the local CSV file.
                                    Defaults to './game_of_thrones/got-s1-edges.csv'.
        url (str, optional): The URL of the raw CSV data. This is used as a fallback.
                             Defaults to "https://raw.githubusercontent.com/mathbeveridge/gameofthrones/master/data/got-s1-edges.csv".

    Returns:
        igraph.Graph: An igraph Graph object representing the network.
    """
    if url is None:
        url = "https://raw.githubusercontent.com/mathbeveridge/gameofthrones/master/data/got-s1-edges.csv"

    if os.path.exists(local_path):
        print(f"Loading data from local file: {local_path}")
        df_s1_edges = pd.read_csv(local_path)
    else:
        print(f"Local file not found at {local_path}. Attempting to download from GitHub...")
        try:
            response = requests.get(url)
            response.raise_for_status() 
            season1_edges_data = io.StringIO(response.text)
            df_s1_edges = pd.read_csv(season1_edges_data)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from {url}: {e}")
            print("Please ensure you have an active internet connection or download the file manually.")
            return None

    if 'Weight' in df_s1_edges.columns:
        edges_for_tuplelist = df_s1_edges[['Source', 'Target', 'Weight']].values.tolist()
        g_s1 = ig.Graph.TupleList(edges_for_tuplelist, directed=False, weights=True)
        print("Graph created with edge weights.")
    else:
        g_s1 = ig.Graph.TupleList(df_s1_edges[['Source', 'Target']].itertuples(index=False), directed=False)
        print("Graph created without edge weights.")

    return g_s1


def export_graph_to_graphml(graph: ig.Graph, export_path: str):
    """
    Exports the given igraph Graph object to a GraphML file.

    Args:
        graph (igraph.Graph): The igraph Graph object to export.
        export_path (str): The path where the GraphML file should be saved.
    """
    if export_path:
        os.makedirs(os.path.dirname(export_path), exist_ok=True)
        graph.write_graphml(export_path)
        print(f"Graph exported to {export_path}")
    else:
        print("No export path provided. Graph not exported.")

if __name__ == "__main__":
    local_path = './game_of_thrones/got-s1-edges.csv'
    export_path = './game_of_thrones/GoT.graphml'
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    full_local_path = os.path.join(script_dir, local_path)
    full_export_path = os.path.join(script_dir, export_path)

    g_s1 = load_got_network(local_path=full_local_path)
    if g_s1:
        export_graph_to_graphml(g_s1, full_export_path)
    else:
        print("Failed to load the Game of Thrones network.")
    