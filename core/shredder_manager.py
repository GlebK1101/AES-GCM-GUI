import os
import secrets
import string

def _obfuscate_path(path):
    """
    Renames a file or folder to a random string.
    Returns the new path (or the old one if renaming failed).
    """
    dir_name = os.path.dirname(path)
    alphabet = string.ascii_letters + string.digits
    
    # Try to generate a unique name (up to 5 attempts)
    for _ in range(5):
        random_name = "".join(secrets.choice(alphabet) for _ in range(16))
        new_path = os.path.join(dir_name, random_name)
        
        if not os.path.exists(new_path):
            try:
                os.rename(path, new_path)
                return new_path
            except OSError:
                # If file is busy or no permissions, keep the old name
                return path
    return path


def wipe_file(path: str, passes: int = 1, status_callback=None):
    """
    Overwrites the file with random data or zeros a specified number of times,
    and then deletes it.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")

    # File size
    file_size = os.path.getsize(path)
    chunk_size = 64 * 1024 # 64 KB

    with open(path, "rb+") as f:
        for i in range(passes):
            if status_callback:
                status_callback(f"Pass {i+1}/{passes} for: {os.path.basename(path)}")
            
            # Go to the beginning of the file
            f.seek(0)
            
            remaining = file_size
            while remaining > 0:
                write_len = min(remaining, chunk_size)
                
                # The last pass is done with zeros (to hide entropy),
                # intermediate passes with random noise
                if i == passes - 1:
                    data = b'\x00' * write_len
                else:
                    data = os.urandom(write_len)
                
                f.write(data)
                remaining -= write_len
            
            # Flush buffers to disk
            f.flush()
            os.fsync(f.fileno())

    # 1. Rename the file (hide the name)
    final_path = _obfuscate_path(path)
    print(f"New name of file: {final_path}")
    
    # 2. Remove the file
    os.remove(final_path)

def wipe_directory(dir_path: str, passes: int = 1, status_callback=None):
    """
    Recursively removes all contents of the folder, overwriting each file.
    """
    if not os.path.exists(dir_path):
        raise FileNotFoundError(f"Folder not found: {dir_path}")

    # Walk the tree bottom-up (to remove files before folders)
    for root, dirs, files in os.walk(dir_path, topdown=False):
        for name in files:
            file_path = os.path.join(root, name)
            try:
                wipe_file(file_path, passes, status_callback)
            except Exception as e:
                if status_callback: 
                    status_callback(f"Error removing file {name}: {e}", is_error=True)

        for name in dirs:
            dir_to_remove = os.path.join(root, name)
            try:
                renamed_dir = _obfuscate_path(dir_to_remove)
                print(f"new name of dir: {renamed_dir}")
                os.rmdir(renamed_dir) 
            except Exception as e:
                if status_callback:
                    status_callback(f"Failed to remove folder {name}: {e}", is_error=True)

    # Remove the root folder itself
    try:
        renamed_root = _obfuscate_path(dir_path)
        os.rmdir(renamed_root)
    except Exception as e:
        if status_callback: status_callback(f"Error removing root {dir_path}: {e}", is_error=True)