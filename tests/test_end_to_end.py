from contextlib import contextmanager
from multiprocessing import Process
import subprocess
import time
import os


dir_path = os.path.dirname(os.path.realpath(__file__))


@contextmanager
def grpc_server_process(port:int = 5000, host: str = "localhost") -> Process:
    """An image-manipulation server handle.

    Args:
        port_number: The port number at which the server will be listening to.
        host: The host / domain name of the server.

    Returns:
        The image manipulation server process handle.
    """

    def _start_mock_server():
        server_sub_process = subprocess.Popen(
            ["server", f"--host {host}", f"--port {port}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        _, _ = server_sub_process.communicate()

    server_process = Process(target=_start_mock_server)
    server_process.start()
    try:
        yield server_process
    finally: server_process.terminate()


def test_end_to_end_server_client(port: int = 5000, host: str = "localhost"): 
    """Test one full client-server call."""
    input_image_path = os.path.join(dir_path, "testing_data/image.png")
    time_at_start = time.time()
    output_image_path = os.path.join(dir_path, f"testing_data/op_{time_at_start}.png")
    # Start the server.
    with grpc_server_process() as server:
        client_sub_process = subprocess.Popen(
            [
                "client", 
                "--host", 
                f"{host}", 
                "--port", 
                f"{port}", 
                "--input", 
                f"{input_image_path}",
                "--output", 
                f"{output_image_path}",
                "--mean", 
                "--rotate",
                "NINETY_DEG"
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        # Run the client call.
        client_sub_process.communicate(timeout=10.0)
    assert os.path.exists(output_image_path), "output image doesn't exist."
