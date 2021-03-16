import os.path


def path_for_view(view):
    window = view.window()
    current_file = view.file_name()
    if current_file is not None:
        return os.path.split(current_file)
    elif window.folders():
        return window.folders()[0], None
    else:
        raise ValueError("No file name or window folders.")
