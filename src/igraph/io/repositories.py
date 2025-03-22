import os
import tempfile
import requests
import zstandard as zstd
import igraph as ig

def _construct_graph_from_Netzschleuder(cls=ig.Graph, name: str = None, net: str = None) -> ig.Graph:
    """
    Downloads, decompresses, and loads a graph from Netzschleuder into an igraph.Graph.

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
    net = net or name  # Default net name

    # Check dataset existence
    dataset_url = f"{base_url}/{name}"
    if requests.head(dataset_url, timeout=5).status_code != 200:
        raise ValueError(f"Dataset '{name}' does not exist at {dataset_url}.")

    # Check network file existence
    file_url = f"{dataset_url}/files/{net}.gml.zst"
    if requests.head(file_url, timeout=5).status_code != 200:
        raise ValueError(f"Network file '{net}.gml.zst' does not exist at {file_url}.")

    try:
        # Download the compressed file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".zst") as tmp_zst_file:
            response = requests.get(file_url, stream=True, timeout=10)
            response.raise_for_status()
            tmp_zst_file.write(response.content)
            tmp_zst_path = tmp_zst_file.name

        # Decompress the file
        dctx = zstd.ZstdDecompressor()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".gml") as tmp_gml_file:
            with open(tmp_zst_path, "rb") as compressed:
                dctx.copy_stream(compressed, tmp_gml_file)
            tmp_gml_path = tmp_gml_file.name

        # Load graph using the given class
        graph = cls.Read_GML(tmp_gml_path)

    except requests.RequestException as e:
        raise RuntimeError(f"Network error: {e}")
    except zstd.ZstdError as e:
        raise RuntimeError(f"Decompression error: {e}")
    except Exception as e:
        raise RuntimeError(f"Error processing file: {e}")
    finally:
        os.remove(tmp_zst_path)
        os.remove(tmp_gml_path)

    return graph