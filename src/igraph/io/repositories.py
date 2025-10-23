import os
import tempfile
import urllib.request
try:
    import zstandard as zstd
except ImportError:
    os.system('pip install zstandard')
    import zstandard as zstd

def _construct_graph_from_Netzschleuder(cls, name: str = None, net: str = None):
    """
    Downloads, decompresses, and loads a graph from a .gml.zst file from Netzschleuder into an igraph.Graph.
    Parameters:
        cls (igraph.Graph, optional): The graph class to use (default: ig.Graph).
        name (str): The dataset name (e.g., "bison").
        net (str, optional): The specific network file (defaults to `name`).
    Returns:
        igraph.Graph: The loaded graph.
    Raises:
        ValueError: If the dataset or network file does not exist.
        RuntimeError: If there are issues with download or decompression.
    """
    if name is None:
        raise ValueError("Dataset name must be provided.")

    base_url = "https://networks.skewed.de/net"
    net = net or name

    # Check dataset existence
    dataset_url = f"{base_url}/{name}"
    try:
        with urllib.request.urlopen(dataset_url) as response:
            if response.status != 200:
                raise ValueError(f"Dataset '{name}' does not exist at {dataset_url}.")
    except:
        raise ValueError(f"Dataset '{name}' does not exist at {dataset_url}.")
        
    from igraph import Graph
    
    # Check network file existence
    file_url = f"{dataset_url}/files/{net}.gml.zst"
    try:
        with urllib.request.urlopen(file_url) as response:
            if response.status != 200:
                raise ValueError(f"Network file '{net}.gml.zst' does not exist at {file_url}.")
    except:
        raise ValueError(f"Network file '{net}.gml.zst' does not exist at {file_url}.")

    try:
        # Download the compressed file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".zst") as tmp_zst_file:
            with urllib.request.urlopen(file_url) as response:
                tmp_zst_file.write(response.read())
            tmp_zst_path = tmp_zst_file.name

        # Decompress the file
        dctx = zstd.ZstdDecompressor()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".gml") as tmp_gml_file:
            with open(tmp_zst_path, "rb") as compressed:
                dctx.copy_stream(compressed, tmp_gml_file)
            tmp_gml_path = tmp_gml_file.name

        # Load graph using the given class
        graph = cls.Read_GML(tmp_gml_path)

    except urllib.error.URLError as e:
        raise RuntimeError(f"Network error: {e}")
    except zstd.ZstdError as e:
        raise RuntimeError(f"Decompression error: {e}")
    except Exception as e:
        raise RuntimeError(f"Error processing file: {e}")
    finally:
        os.remove(tmp_zst_path)
        os.remove(tmp_gml_path)

    return graph
