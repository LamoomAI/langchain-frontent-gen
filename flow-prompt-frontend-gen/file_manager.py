# create_directory.py
import os

def create_overwrite_directory(base_path, directory_name) -> str:
    path = os.path.join(base_path, directory_name)
    os.makedirs(path, exist_ok=True)
    return path

def create_file(dir_path, file_name, content):
    file_path = os.path.join(dir_path, file_name)
    with open(file_path, 'w+') as file:
        file.write(content)
    print(f"File '{file_name}' created in '{dir_path}'.")