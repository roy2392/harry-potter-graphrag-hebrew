import os
import shutil
import json
import yaml


def ensure_dir(directory):
    """
    Create a directory if it doesn't exist.

    Args:
    directory (str): The path to the directory.
    """
    if not os.path.exists(directory):
        os.makedirs(directory)


def list_files(directory, extension=None):
    """
    List all files in a directory, optionally filtering by extension.

    Args:
    directory (str): The path to the directory.
    extension (str, optional): File extension to filter by (e.g., '.pdf', '.txt').

    Returns:
    list: A list of file names.
    """
    if extension:
        return [f for f in os.listdir(directory) if f.endswith(extension)]
    return os.listdir(directory)


def safe_delete(path):
    """
    Safely delete a file or directory.

    Args:
    path (str): The path to the file or directory to delete.
    """
    if os.path.isfile(path):
        os.remove(path)
    elif os.path.isdir(path):
        shutil.rmtree(path)


def read_json(file_path):
    """
    Read a JSON file and return its contents.

    Args:
    file_path (str): The path to the JSON file.

    Returns:
    dict: The contents of the JSON file.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)


def write_json(data, file_path):
    """
    Write data to a JSON file.

    Args:
    data (dict): The data to write.
    file_path (str): The path to the JSON file.
    """
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def read_yaml(file_path):
    """
    Read a YAML file and return its contents.

    Args:
    file_path (str): The path to the YAML file.

    Returns:
    dict: The contents of the YAML file.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)


def write_yaml(data, file_path):
    """
    Write data to a YAML file.

    Args:
    data (dict): The data to write.
    file_path (str): The path to the YAML file.
    """
    with open(file_path, 'w', encoding='utf-8') as file:
        yaml.dump(data, file, default_flow_style=False)


def get_file_size(file_path):
    """
    Get the size of a file in bytes.

    Args:
    file_path (str): The path to the file.

    Returns:
    int: The size of the file in bytes.
    """
    return os.path.getsize(file_path)


def copy_file(src, dst):
    """
    Copy a file from source to destination.

    Args:
    src (str): The path to the source file.
    dst (str): The path to the destination file.
    """
    shutil.copy2(src, dst)


def move_file(src, dst):
    """
    Move a file from source to destination.

    Args:
    src (str): The path to the source file.
    dst (str): The path to the destination file.
    """
    shutil.move(src, dst)