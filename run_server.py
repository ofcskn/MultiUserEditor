import multiprocessing
import time
import sys
import os

from server.server import start_server

# Adjust import paths
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

def run_server():
    print("🔌 Starting server...")
    start_server()  # Your server's main loop

if __name__ == "__main__":
    server_process = multiprocessing.Process(target=run_server)
    server_process.start()
