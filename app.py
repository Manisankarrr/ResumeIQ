"""
Hugging Face Spaces entry point.

Starts the FastAPI backend as a background subprocess, waits for it to
initialise, then launches the Streamlit frontend on port 7860.
"""

import subprocess
import sys
import time


def main():
    # 1. Start FastAPI backend in the background
    backend = subprocess.Popen(
        [sys.executable, "-m", "api.main"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # 2. Give the backend a few seconds to boot
    time.sleep(3)

    # 3. Launch Streamlit on the port Hugging Face expects
    sys.argv = [
        "streamlit",
        "run",
        "ui/app.py",
        "--server.port=7860",
        "--server.address=0.0.0.0",
    ]

    from streamlit.web.cli import main as st_main

    st_main()


if __name__ == "__main__":
    main()
