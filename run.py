"""
Script to run both Django server and django-q2 cluster together.

Usage:
    uv run python run.py
    python run.py
"""

import signal
import subprocess
import sys
import threading

from loguru import logger

# Configure loguru with colors and formatting
logger.remove()  # Remove default handler
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    colorize=True,
    level="INFO",
)

# Global process references for signal handling
server_process = None
cluster_process = None


def signal_handler(sig, frame):
    """Handle Ctrl+C and termination signals gracefully"""
    logger.warning("Received shutdown signal, shutting down server and cluster...")
    if server_process:
        logger.info("Terminating server process...")
        server_process.terminate()
    if cluster_process:
        logger.info("Terminating cluster process...")
        cluster_process.terminate()
    sys.exit(0)


def print_output(process, prefix):
    """Print output from a process with color-coded prefix using loguru"""
    color_map = {
        "SERVER": "blue",
        "CLUSTER": "magenta",
    }
    color = color_map.get(prefix, "white")

    try:
        for line in iter(process.stdout.readline, ""):
            if line:
                line = line.rstrip()
                if line:
                    logger.opt(colors=True).info(
                        f"<{color}>[{prefix}]</{color}> {line}"
                    )
    except Exception as e:
        logger.error(f"Error reading output from {prefix}: {e}")


def run_migrations():
    """Run Django migrations before starting services"""
    logger.info("Running database migrations...")
    python_exe = sys.executable
    try:
        result = subprocess.run(
            [python_exe, "manage.py", "migrate", "--noinput"],
            capture_output=True,
            text=True,
            check=True,
        )
        logger.success("Migrations completed successfully")
        if result.stdout:
            logger.debug(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Migration failed: {e}")
        if e.stderr:
            logger.error(f"Error output: {e.stderr}")
        return False


def main():
    """Run both server and cluster as subprocesses"""
    global server_process, cluster_process

    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    logger.info("=" * 60)
    logger.info("Starting Django server and django-q2 cluster...")
    logger.info("Press Ctrl+C to stop both processes")
    logger.info("=" * 60)

    # Run migrations first
    if not run_migrations():
        logger.error("Failed to run migrations. Exiting.")
        sys.exit(1)

    # Determine the Python executable
    python_exe = sys.executable

    # Start Django server
    logger.info("Starting Django development server...")
    server_process = subprocess.Popen(
        [python_exe, "manage.py", "runserver", "0.0.0.0:8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    # Start django-q2 cluster
    logger.info("Starting django-q2 cluster...")
    cluster_process = subprocess.Popen(
        [python_exe, "manage.py", "qcluster"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    # Create threads to handle output from both processes
    server_thread = threading.Thread(
        target=print_output, args=(server_process, "SERVER"), daemon=True
    )
    cluster_thread = threading.Thread(
        target=print_output, args=(cluster_process, "CLUSTER"), daemon=True
    )

    server_thread.start()
    cluster_thread.start()

    logger.success("Both processes started successfully")
    logger.info("Server: http://0.0.0.0:8000")
    logger.info("API Docs: http://0.0.0.0:8000/api/docs/")

    # Wait for processes to complete
    try:
        server_process.wait()
        cluster_process.wait()
    except KeyboardInterrupt:
        signal_handler(None, None)


if __name__ == "__main__":
    main()
