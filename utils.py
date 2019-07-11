import os


def list_files_n_dirs(path: str):
    """Returns a list of files and directories from the path

    Args:
        path (str): directory path

    Returns:
        [list, list]: list of files and directories
    """
    files = []
    dirs = []
    file_sizes = []
    for (_, dir_names, file_names) in os.walk(path):
        files.extend(file_names)
        dirs.extend(dir_names)

        for file in file_names:
            file = os.path.join(path, file)
            file_sizes.append(file_size(file))
        return files, file_sizes, dirs


def convert_bytes(num):
    """Convert bytes to MB.... GB... etc

    Args:
        num (float): number of bytes
    """
    for x in ["bytes", "KB", "MB", "GB", "TB"]:
        if num < 1000.0:
            return "%3.1f %s" % (num, x)
        num /= 1000.0


def file_size(file_path):
    """Return the file size

    Args:
        file_path (str): file path
    """
    if os.path.isfile(file_path):
        file_info = os.stat(file_path)
        return convert_bytes(file_info.st_size)
