import multiprocessing
import time
import sys
import os

# Adjust import paths
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from server.server import start_server
from client.client import start_client 

def run_server():
    print("🔌 Starting server...")
    start_server()  # Your server's main loop

def run_client():
    print("🖥️ Starting client...")
    start_client()  # Your PySide6 GUI launcher

if __name__ == "__main__":
    server_process = multiprocessing.Process(target=run_server)
    server_process.start()

    # Optional: give server a moment to initialize
    time.sleep(1)

    try:
        run_client()
    finally:
        print("❌ Shutting down server...")
        server_process.terminate()
        server_process.join()
