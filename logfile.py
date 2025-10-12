from collections import deque

logfile_name = "motion.log"


def reverse_readline(filename, count):
    with open(filename, 'r') as file:
        lines = deque(file, maxlen=count)
        # Remove trailing backslash from each line
        return [line.rstrip() for line in lines]
