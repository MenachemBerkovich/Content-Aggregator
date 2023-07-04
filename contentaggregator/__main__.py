"""_summary_#TODO
"""

import os
import subprocess
import multiprocessing

from contentaggregator.lib import distributionsystem


def start_server() -> subprocess.CompletedProcess:
    """Starts the local server to listen on the port 3000 (default by pynecone)."""
    try:
        print("Server starting...")
        # Use shell; Because 'pc run' is not executable like 'ls' command, but a part of the shell itself
        subprocess.run("pc run", shell=True, check=True)
        print("Server stopped...")
    # Handle errors by log them.
    except Exception as e:
        print(e)


def start_distribution_system() -> None:
    """Starts the distribution system to work while True."""
    try:
        postman = distributionsystem.Messenger()
        postman.run()
    except Exception as e:
        # Log it
        print(e)


if "website" not in os.getcwd():
    current_file_path = os.path.realpath(__file__)
    os.chdir(os.path.join(current_file_path[: current_file_path.rfind("/")], "website"))

server_process = multiprocessing.Process(target=start_server)
distribution_process = multiprocessing.Process(target=start_distribution_system)
server_process.start()
distribution_process.start()
server_process.join()
distribution_process.join()
# it will be one procces of the multiproccesing with check=True and try ecxept statments for logging booting of the server and so on...
# for 'port in use' pc ecxeption, consider use Popen object and handle it specifically, and Dynamicly.
