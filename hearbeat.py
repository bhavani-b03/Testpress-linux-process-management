import os
import sys
import time
import signal
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [PID:%(process)d] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

HEARTBEAT_INTERVAL = int(os.getenv("HEARTBEAT_INTERVAL", "5"))
SIMULATE_CRASH_AFTER = int(os.getenv("SIMULATE_CRASH_AFTER", "-1"))
TRIGGER_OOM = os.getenv("TRIGGER_OOM", "false").lower() == "true"

running = True
memory_leak_container = []

def handle_shutdown_signal(signum, frame):
    global running
    sig_name = signal.Signals(signum).name
    logging.info(f"Received signal {sig_name} ({signum}). Shutting down gracefully...")
    running = False

signal.signal(signal.SIGINT, handle_shutdown_signal)
signal.signal(signal.SIGTERM, handle_shutdown_signal)

logging.info("Starting Testpress Background Worker...")

count = 1
while running:
    logging.info(f"Heartbeat #{count} - Worker is healthy.")

    # Memory Leak Simulation for Experiment 6
    if TRIGGER_OOM:
        logging.info("Allocating 20MB of memory...")
        memory_leak_container.append('X' * (20 * 1024 * 1024))  # Allocates ~20MB per loop iteration

    if SIMULATE_CRASH_AFTER > 0 and count >= SIMULATE_CRASH_AFTER:
        logging.error("CRASH TRIGGERED! Exiting with error code 1...")
        sys.exit(1)

    count += 1
    time.sleep(HEARTBEAT_INTERVAL)

logging.info("Graceful shutdown complete. Goodbye!")
sys.exit(0)
