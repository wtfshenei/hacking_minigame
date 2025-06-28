import sys
import time

def loading_bar(duration):
    """
    Display a horizontal loading bar for the given duration (in seconds).
    """
    total_blocks = 30
    interval = duration / total_blocks

    sys.stdout.write("[")
    sys.stdout.flush()

    for _ in range(total_blocks):
        time.sleep(interval)
        sys.stdout.write("█")
        sys.stdout.flush()

    sys.stdout.write("]\n")
    sys.stdout.flush()