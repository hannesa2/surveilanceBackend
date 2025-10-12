import re
from collections import deque

logfile_name = "motion.log"


def reverse_readline(filename, count, search_string=None,
                     case_sensitive=True,
                     remove_backslash=True,
                     skip_last=0,
                     use_regex=False):
    """
    Read last n filtered lines from a file, optionally skipping lines at the end.

    Args:
        filename: Path to the file
        count: Number of lines to return
        search_string: String or pattern to search for
        case_sensitive: Whether search is case-sensitive
        remove_backslash: Remove trailing backslashes
        skip_last: Number of lines to skip from the end
        use_regex: Use regex for pattern matching
    """
    with open(filename, 'r') as file:
        # Filter lines
        if search_string:
            if use_regex:
                compiled = re.compile(search_string,
                                      0 if case_sensitive else re.IGNORECASE)
                filtered = (line for line in file if compiled.search(line))
            elif case_sensitive:
                filtered = (line for line in file if search_string in line)
            else:
                search_lower = search_string.lower()
                filtered = (line for line in file if search_lower in line.lower())
        else:
            filtered = file

        # Keep last (n + skip_last) filtered lines
        lines = list(deque(filtered, maxlen=count + skip_last))

        # Remove the last skip_last lines
        if skip_last > 0:
            lines = lines[:-skip_last] if len(lines) > skip_last else []

        # Optionally remove trailing backslashes
        if remove_backslash:
            lines = [line.rstrip() for line in lines]

        return lines
