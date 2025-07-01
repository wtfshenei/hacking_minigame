import os
import sys
import time

# Cross-platform non-blocking, echoing input with timeout
try:
    import msvcrt

    def timed_input(prompt, timeout):
        """Prompt the user with a timeout in seconds; return input or None if timed out."""
        sys.stdout.write(prompt)
        sys.stdout.flush()
        input_str = ''
        start = time.time()
        while True:
            if msvcrt.kbhit():
                ch = msvcrt.getwch()
                # ignore arrow keys (prefix codes 0 or 0xe0)
                if ch in ('\x00', '\xe0'):
                    msvcrt.getwch()  # discard next code
                    continue
                # process entered character
                if ch in ('\r', '\n'):
                    sys.stdout.write('\n')
                    return input_str
                elif ch == '\b':
                    if input_str:
                        input_str = input_str[:-1]
                        sys.stdout.write('\b \b')
                else:
                    input_str += ch
                    sys.stdout.write(ch)
                sys.stdout.flush()
            if timeout is not None and time.time() - start >= timeout:
                sys.stdout.write('\n')
                return None
            time.sleep(0.1)

except ImportError:
    import termios
    import tty
    import fcntl

    def timed_input(prompt, timeout):
        """Prompt the user with a timeout in seconds on POSIX systems."""
        sys.stdout.write(prompt)
        sys.stdout.flush()
        input_str = ''
        start = time.time()
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        old_flags = fcntl.fcntl(fd, fcntl.F_GETFL)
        try:
            tty.setcbreak(fd)
            fcntl.fcntl(fd, fcntl.F_SETFL, old_flags | os.O_NONBLOCK)
            while True:
                try:
                    ch = sys.stdin.read(1)
                except (IOError, OSError):
                    ch = ''
                if ch:
                    # ignore arrow key escape sequences
                    if ch == '\x1b':  # ESC
                        # consume the rest of the sequence
                        sys.stdin.read(2)
                        continue
                    if ch in ('\n', '\r'):
                        sys.stdout.write('\n')
                        return input_str
                    elif ch == '\x7f':  # backspace
                        if input_str:
                            input_str = input_str[:-1]
                            sys.stdout.write('\b \b')
                    else:
                        input_str += ch
                        sys.stdout.write(ch)
                    sys.stdout.flush()
                if timeout is not None and time.time() - start >= timeout:
                    sys.stdout.write('\n')
                    return None
                time.sleep(0.1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            fcntl.fcntl(fd, fcntl.F_SETFL, old_flags)


def clear_screen():
    """Clear the console screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_intro():
    """Print the game introduction banner."""
    print("""
*** TERMINAL DE COFFRE-SYDNEY-S7E35810 ***
Tape 'help' pour voir les commandes disponibles.
""")
