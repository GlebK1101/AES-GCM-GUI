from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id
import os
import json
import secrets
import string
import shutil
from cryptography.exceptions import InvalidTag 

def random_filename(min_len: int = 16, max_len: int = 32) -> str: 
    if min_len < 1 or max_len < min_len:
        raise ValueError("Некорректные границы длины имени")
    
    length = secrets.randbelow(max_len - min_len + 1) + min_len
    alphabet = string.ascii_letters + string.digits + "_-"
    return "".join(secrets.choice(alphabet) for _ in range(length))

def get_kdf_params(config):
    """Auxiliary function to extract KDF parameters from config"""
    kdf_params = config.get('kdf_params', {})
    return {
        'length': kdf_params.get('length', 32),
        'iterations': kdf_params.get('iterations', 3),
        'memory_cost': kdf_params.get('memory_cost', 64 * 1024),
        'lanes': kdf_params.get('lanes', 1)
    }

def get_aad_bytes(config):
    """
    AAD processing: 
    If None or empty string -> return b"" (empty bytes).
    Otherwise -> encode string to UTF-8.
    """
    aad_val = config.get('general_params', {}).get('aad')
    
    if not aad_val: # Works for None and ""
        return b""
    return str(aad_val).encode("utf-8")

def encrypt_file(input_path: str, password: str, enc_ext: str = ".enc", config=None, output_dir=None, custom_name=None):
    if config is None:
        config = {}

    # 1. Data preparation
    aad = get_aad_bytes(config)
    
    fname_params = config.get('filename_params', {})
    p_min_len = fname_params.get('min_len', 16)
    p_max_len = fname_params.get('max_len', 32)

    password_bytes = password.encode("utf-8")

    # --- Form internal filename ---
    filename = os.path.basename(input_path)
    base, point, extension = filename.rpartition(".")
    if not point:
        name = filename
        ext = ""
    else:
        name = base
        ext = point + extension

    name_bytes = name.encode("utf-8")
    ext_bytes = ext.encode("utf-8")

    if len(name_bytes) > 65535:
        raise ValueError("Имя файла слишком длинное")
    if len(ext_bytes) > 255:
        raise ValueError("Расширение слишком длинное")

    # --- Reading data ---
    with open(input_path, "rb") as f:
        file_data = f.read()

    # --- Assemble plaintext ---
    plaintext = (
        len(name_bytes).to_bytes(2, "big") +
        name_bytes +
        len(ext_bytes).to_bytes(1, "big") +
        ext_bytes +
        file_data
    )

    # --- KDF (Key Generation) ---
    salt = os.urandom(16)
    kp = get_kdf_params(config)
    
    kdf = Argon2id(
        salt=salt,
        length=kp['length'],
        iterations=kp['iterations'],
        memory_cost=kp['memory_cost'],
        lanes=kp['lanes']
    )
    key = kdf.derive(password_bytes)

    # --- AES-GCM Encryption ---
    nonce = os.urandom(12)
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, plaintext, aad)

    # --- Saving result ---
    
    # 1. Determine target folder
    if output_dir and str(output_dir).strip():
        target_dir = output_dir
        if not os.path.exists(target_dir):
            raise FileNotFoundError(f"Указанная папка для сохранения не существует: {target_dir}")
    else:
        target_dir = os.path.dirname(input_path)
    
    # 2. Determine filename
    # If user specified a name - use it
    if custom_name and str(custom_name).strip():
        # Remove extension if user typed it (to avoid .enc.enc)
        final_name = str(custom_name).strip()
        if final_name.endswith(enc_ext):
            final_name = final_name[:-len(enc_ext)]
            
        output_path = os.path.join(target_dir, final_name + enc_ext)
        
        # EXISTENCE CHECK
        if os.path.exists(output_path):
            # We raise a special error to be caught in GUI
            raise FileExistsError(f"Файл с именем '{final_name + enc_ext}' уже существует в целевой папке!") 
    else:
        # If name is not set - generate random
        while True:
            random_name = random_filename(min_len=p_min_len, max_len=p_max_len)
            output_path = os.path.join(target_dir, random_name + enc_ext)
            if not os.path.exists(output_path):
                break
    
    # Normalize and write
    output_path = os.path.normpath(output_path)

    with open(output_path, "wb") as f:
        f.write(salt)
        f.write(nonce)
        f.write(ciphertext)
        
    return output_path


def decrypt_file(input_path: str, password: str, config=None, output_dir=None):
    if config is None:
        config = {}

    # 1. Data preparation
    # Important: AAD and KDF params must match those used during encryption
    aad = get_aad_bytes(config)
    kp = get_kdf_params(config)
    
    password_bytes = password.encode("utf-8")

    # --- Read encrypted file ---
    with open(input_path, "rb") as f:
        salt = f.read(16)
        nonce = f.read(12)
        ciphertext = f.read()

    # --- KDF (Key Recovery) ---
    kdf = Argon2id(
        salt=salt,
        length=kp['length'],
        iterations=kp['iterations'],
        memory_cost=kp['memory_cost'],
        lanes=kp['lanes']
    )
    key = kdf.derive(password_bytes)

    # --- AES-GCM Decryption ---
    aesgcm = AESGCM(key)
    # If password, salt, nonce or AAD are wrong - an exception is raised here
    plaintext = aesgcm.decrypt(nonce, ciphertext, aad)

    # --- Parse plaintext (restore name) ---
    offset = 0

    name_len = int.from_bytes(plaintext[offset:offset + 2], "big")
    offset += 2

    name = plaintext[offset:offset + name_len].decode("utf-8")
    offset += name_len

    ext_len = plaintext[offset]
    offset += 1

    ext = plaintext[offset:offset + ext_len].decode("utf-8")
    offset += ext_len

    file_data = plaintext[offset:]

    # --- Saving result ---
    
    # Determine target folder
    if output_dir and str(output_dir).strip():
        target_dir = output_dir
        if not os.path.exists(target_dir):
            raise FileNotFoundError(f"Указанная папка для сохранения не существует: {target_dir}")
    else:
        target_dir = os.path.dirname(input_path)
        
    output_path = os.path.join(target_dir, name + ext)
    output_path = os.path.normpath(output_path)

    with open(output_path, "wb") as f:
        f.write(file_data)
        
    return output_path

# ---------------------------------------------------------

def encrypt_file_stream(input_path: str, vault_dir: str, password: str, enc_ext: str = ".enc", config=None):
    if config is None: config = {}
    
    # Extract settings
    kp = get_kdf_params(config)
    aad = get_aad_bytes(config)
    
    # Chunk size from settings (default 64KB)
    chunk_size = config.get('streaming_params', {}).get('chunk_size', 64 * 1024)

    password_bytes = password.encode("utf-8")

    # --- Prepare filename ---
    filename = os.path.basename(input_path)
    base, point, extension = filename.rpartition(".")
    if not point:
        name, ext = filename, ""
    else:
        name, ext = base, point + extension

    name_bytes = name.encode("utf-8")
    ext_bytes = ext.encode("utf-8")

    if len(name_bytes) > 65535: raise ValueError("Имя файла слишком длинное")
    if len(ext_bytes) > 255: raise ValueError("Расширение слишком длинное")

    # --- KDF ---
    salt = os.urandom(16)
    kdf = Argon2id(
        salt=salt,
        length=kp['length'],
        iterations=kp['iterations'],
        memory_cost=kp['memory_cost'],
        lanes=kp['lanes']
    )
    key = kdf.derive(password_bytes)
    aesgcm = AESGCM(key)

    # --- Random name ---
    os.makedirs(vault_dir, exist_ok=True)
    
    # Generate unique name
    fname_params = config.get('filename_params', {})
    p_min_len = fname_params.get('min_len', 16)
    p_max_len = fname_params.get('max_len', 32)
    
    while True:
        random_name = random_filename(min_len=p_min_len, max_len=p_max_len)
        output_path = os.path.join(vault_dir, random_name + enc_ext)
        if not os.path.exists(output_path):
            break

    with open(input_path, "rb") as fin, open(output_path, "wb") as fout:
        fout.write(salt)

        first_chunk = True
        while True:
            if first_chunk:
                header = (
                    len(name_bytes).to_bytes(2, "big") +
                    name_bytes +
                    len(ext_bytes).to_bytes(1, "big") +
                    ext_bytes
                )
                max_data = chunk_size - len(header)
                data = fin.read(max_data)
                data = header + data
                first_chunk = False
            else:
                data = fin.read(chunk_size)
    
            if not data:
                break
            
            real_len = len(data)
            # Pad with random data to match chunk size
            if real_len < chunk_size:
                data += os.urandom(chunk_size - real_len)

            nonce = os.urandom(12)
            ciphertext = aesgcm.encrypt(nonce, data, aad)

            fout.write(nonce)
            fout.write(real_len.to_bytes(4, "big"))
            fout.write(ciphertext)
            
    return os.path.basename(output_path)


def decrypt_file_stream(input_path: str, password: str, output_path: str, config=None):
    if config is None: config = {}
    
    kp = get_kdf_params(config)
    aad = get_aad_bytes(config)
    chunk_size = config.get('streaming_params', {}).get('chunk_size', 64 * 1024)
    
    password_bytes = password.encode("utf-8")

    with open(input_path, "rb") as fin:
        salt = fin.read(16)

        kdf = Argon2id(
            salt=salt,
            length=kp['length'],
            iterations=kp['iterations'],
            memory_cost=kp['memory_cost'],
            lanes=kp['lanes']
        )
        key = kdf.derive(password_bytes)
        aesgcm = AESGCM(key)

        first_chunk = True
        fout = None
        
        try:
            while True:
                nonce = fin.read(12)
                if not nonce: 
                    break 

                real_len_bytes = fin.read(4)
                if not real_len_bytes: 
                    break 
                
                real_len = int.from_bytes(real_len_bytes, "big")
                ciphertext = fin.read(chunk_size + 16)
                
                if len(ciphertext) != chunk_size + 16:
                    raise ValueError("Повреждён контейнер (неполный чанк)")

                plaintext = aesgcm.decrypt(nonce, ciphertext, aad)
                data = plaintext[:real_len]

                if first_chunk:
                    offset = 0
                    name_len = int.from_bytes(data[offset:offset + 2], "big")
                    offset += 2 + name_len
                    ext_len = data[offset]
                    offset += 1 + ext_len
                    
                    # !!! CREATE FOLDER ONLY HERE !!!
                    # If we reached here, the password is correct.
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    
                    fout = open(output_path, "wb")
                    fout.write(data[offset:])
                    first_chunk = False
                else:
                    fout.write(data)
        finally:
            if fout: 
                fout.close()


def collect_files(root_dir: str, exclude_dirs=None):
    if exclude_dirs is None: 
        exclude_dirs = set()
    files = []
    root_dir = os.path.abspath(root_dir)

    for current_dir, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
        for filename in filenames:
            full_path = os.path.join(current_dir, filename)
            rel_path = os.path.relpath(full_path, root_dir)
            files.append(rel_path)
    return files


def check_free_space(root_dir: str, vault_dir: str, chunk_size: int):
    total_vault_size = 0
    chunk_overhead = 12 + 4 + 16
    file_overhead = 16

    for dirpath, _, filenames in os.walk(root_dir):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if not os.path.islink(fp):
                size = os.path.getsize(fp)
                num_chunks = (size // chunk_size) + (1 if size % chunk_size != 0 or size == 0 else 0)
                encrypted_size = file_overhead + (num_chunks * (chunk_size + chunk_overhead))
                total_vault_size += encrypted_size

    target_path = vault_dir if os.path.exists(vault_dir) else os.path.dirname(os.path.abspath(vault_dir))
    try:
        free_space = shutil.disk_usage(target_path).free
    except FileNotFoundError:
        # If disk/path does not exist, return 0 (error)
        free_space = 0 

    if free_space < total_vault_size:
        return False, total_vault_size, free_space
    return True, total_vault_size, free_space


def build_manifest(root_dir: str, vault_dir: str, password: str, exclude_dirs=None, config=None, status_callback=None, custom_manifest_dir=None):
    """
    status_callback: function(str), to send progress messages to GUI.
    custom_manifest_dir: If specified, manifest.json is saved there.
                         If None, saved in vault_dir/manifest/
    """
    if config is None: 
        config = {}
    chunk_size = config.get('streaming_params', {}).get('chunk_size', 64 * 1024)
    enc_ext = config.get('general_params', {}).get('extension', '.enc')
    
    # 1. Space check
    can_proceed, total_s, free_s = check_free_space(root_dir, vault_dir, chunk_size)
    if not can_proceed:
        needed_mb = total_s // (1024**2)
        avail_mb = free_s // (1024**2)
        raise OSError(f"Недостаточно места! Нужно: {needed_mb} МБ, доступно: {avail_mb} МБ")
    
    files_to_encrypt = collect_files(root_dir, exclude_dirs)
    if not files_to_encrypt:
        raise ValueError("Нет файлов для шифрования (папка пуста или все файлы исключены).")

    if not os.path.exists(vault_dir):
        os.makedirs(vault_dir)

    # --- MANIFEST PATH LOGIC ---
    if custom_manifest_dir and str(custom_manifest_dir).strip():
        # If user selected a folder
        man_dir = str(custom_manifest_dir).strip()
    else:
        # Default: "manifest" folder inside vault
        man_dir = os.path.join(vault_dir, "manifest")
    
    os.makedirs(man_dir, exist_ok=True)
    manifest_path = os.path.join(man_dir, "manifest.json")

    # Overwrite check
    if os.path.exists(manifest_path):
        raise FileExistsError(f"Файл манифеста уже существует по пути:\n{manifest_path}\nУдалите его или выберите другую папку.")

    manifest = []
    
    # Mode 'x' ensures we don't overwrite the file if it appears at the last second
    with open(manifest_path, "x", encoding="utf-8") as f_manifest:
        f_manifest.write("[\n")
        first_entry = True

        for i, rel_path in enumerate(files_to_encrypt):
            full_path = os.path.join(root_dir, rel_path)
            try:
                if status_callback: 
                    status_callback(f"[{i+1}/{len(files_to_encrypt)}] Шифрование: {rel_path}")
                
                stored_name = encrypt_file_stream(full_path, vault_dir, password, enc_ext, config)
                entry = {"original": rel_path, "stored": stored_name}
                manifest.append(entry)

                if not first_entry: f_manifest.write(",\n")
                json.dump(entry, f_manifest, ensure_ascii=False)
                f_manifest.flush()
                os.fsync(f_manifest.fileno()) # For reliability, but slows down
                first_entry = False
                
            except Exception as e:
                if status_callback: 
                    status_callback(f"Ошибка на {rel_path}: {e}", is_error=True)
                # Decide: abort or continue
                # raise e 
        
        f_manifest.write("\n]")

    return manifest_path


def restore_from_manifest(manifest_path: str, vault_dir: str, output_dir: str, password: str, config=None, status_callback=None):
    """
    manifest_path: Full path to manifest.json (now we pass the file, not the folder!)
    vault_dir: Folder where .enc files are located
    """
    
    if not os.path.exists(manifest_path):
        raise FileNotFoundError("Файл манифеста не найден!")

    with open(manifest_path, "r", encoding="utf-8") as f:
        try:
            content = f.read().strip()
            if not content.endswith("]"): content += "\n]"
            manifest = json.loads(content)
        except Exception as e:
            raise ValueError(f"Критическая ошибка при чтении JSON: {e}")

    # Convert destination path to absolute for correct comparison
    abs_output_dir = os.path.abspath(output_dir)
    
    total = len(manifest)
    for i, entry in enumerate(manifest):
        rel_path = entry["original"]
        stored_name = entry["stored"]
        
        input_file = os.path.join(vault_dir, stored_name)
        
        # --- PATH TRAVERSAL PROTECTION ---
        # 1. Join path
        final_output_path = os.path.abspath(os.path.join(abs_output_dir, rel_path))
        
        # 2. Check: does final path start with destination folder?
        # commonpath correctly compares paths in different OS
        try:
            common = os.path.commonpath([abs_output_dir, final_output_path])
            if common != abs_output_dir:
                msg = f"ОШИБКА БЕЗОПАСНОСТИ: Путь '{rel_path}' пытается выйти за пределы папки восстановления!"
                if status_callback: status_callback(msg, is_error=True)
                continue # Skip this dangerous file
        except ValueError:
            # If paths are on different drives (Windows), commonpath raises error -> definitely attack or bug
            if status_callback: status_callback(f"Подозрительный путь (разные диски): {rel_path}", is_error=True)
            continue
        # -------------------------------
        
        # Check if encrypted file exists
        if not os.path.exists(input_file):
            if status_callback: status_callback(f"Файл не найден в хранилище: {stored_name}", is_error=True)
            continue
        
        try:
            # First do the work...
            decrypt_file_stream(input_file, password, final_output_path, config)
            
            # ...and only if no error occurred, log it
            if status_callback:
                status_callback(f"[{i+1}/{total}] Успешно восстановлен: {rel_path}")
        
        except InvalidTag:
            # If password didn't work for one file, it won't work for others.
            err_msg = "НЕВЕРНЫЙ ПАРОЛЬ! Восстановление прервано."
            # if status_callback: status_callback(err_msg, is_error=True) --- comment
            # Abort execution of the whole function
            raise InvalidTag(err_msg) 
        
        except Exception as e:
            # If error, log it immediately
            if status_callback: 
                status_callback(f"Ошибка при восстановлении {rel_path}: {e}", is_error=True)
                # Important: if password is wrong, error occurs on the first file
                # and empty folders will not be created.
                
            
#  === BLOCK FOR "STREAM" TAB (SINGLE FILES) ===

def encrypt_file_stream_single(input_path: str, password: str, enc_ext: str = ".enc", config=None, output_dir=None, custom_name=None):
    """
    Stream encryption for a single file.
    Writes filename inside the container (in the first chunk) so that during decryption
    without manifest we know the original name.
    """
    if config is None: config = {}
    
    # 1. Settings
    kp = get_kdf_params(config)
    aad = get_aad_bytes(config)
    chunk_size = config.get('streaming_params', {}).get('chunk_size', 64 * 1024)

    password_bytes = password.encode("utf-8")

    # 2. Header preparation (Name + Extension)
    filename = os.path.basename(input_path)
    base, point, extension = filename.rpartition(".")
    if not point: name, ext = filename, ""
    else: name, ext = base, point + extension

    name_bytes = name.encode("utf-8")
    ext_bytes = ext.encode("utf-8")

    if len(name_bytes) > 65535: raise ValueError("Имя файла слишком длинное")
    if len(ext_bytes) > 255: raise ValueError("Расширение слишком длинное")

    # 3. Cryptography
    salt = os.urandom(16)
    kdf = Argon2id(salt=salt, length=kp['length'], iterations=kp['iterations'], memory_cost=kp['memory_cost'], lanes=kp['lanes'])
    key = kdf.derive(password_bytes)
    aesgcm = AESGCM(key)

    # 4. Determine paths
    if output_dir and str(output_dir).strip():
        target_dir = output_dir
        if not os.path.exists(target_dir):
            raise FileNotFoundError(f"Папка не существует: {target_dir}")
    else:
        target_dir = os.path.dirname(input_path)

    # Name logic (Custom or Random)
    if custom_name and str(custom_name).strip():
        final_name = str(custom_name).strip()
        if final_name.endswith(enc_ext):
            final_name = final_name[:-len(enc_ext)]
        output_path = os.path.join(target_dir, final_name + enc_ext)
        if os.path.exists(output_path):
            raise FileExistsError(f"Файл уже существует: {final_name + enc_ext}")
    else:
        fname_params = config.get('filename_params', {})
        p_min_len = fname_params.get('min_len', 16)
        p_max_len = fname_params.get('max_len', 32)
        while True:
            random_name = random_filename(min_len=p_min_len, max_len=p_max_len)
            output_path = os.path.join(target_dir, random_name + enc_ext)
            if not os.path.exists(output_path):
                break
    
    output_path = os.path.normpath(output_path)
    
    # 5. Space check (using shutil)
    try:
        file_size = os.path.getsize(input_path)
        
        # Calculate number of chunks
        if file_size == 0:
            num_chunks = 1
        else:
            num_chunks = (file_size // chunk_size) + (1 if file_size % chunk_size != 0 else 0)
        
        # IMPORTANT: Output file size will consist of full chunks (including padding) + metadata.
        # Each written block = chunk_size (data+padding) + 12(nonce) + 4(len) + 16(tag)
        block_size_on_disk = chunk_size + 12 + 4 + 16
        
        estimated_total_size = 16 + (num_chunks * block_size_on_disk) + 1024 # + salt and margin for header
        
        free_space = shutil.disk_usage(target_dir).free
        
        if free_space < estimated_total_size:
            needed_mb = estimated_total_size / (1024**2)
            avail_mb = free_space / (1024**2)
            # Form clear message, like in Manifest
            raise OSError(f"Недостаточно места (с учетом Chunk Size)!\nТребуется: {needed_mb:.2f} MB\nДоступно: {avail_mb:.2f} MB")
            
    except OSError as e:
        raise e 
    except Exception:
        pass # If shutil failed (rare case), try writing anyway

    # 6. Stream writing
    with open(input_path, "rb") as fin, open(output_path, "wb") as fout:
        fout.write(salt)

        first_chunk = True
        while True:
            if first_chunk:
                # In first chunk write header
                # Structure: [LenName 2b][Name][LenExt 1b][Ext][Data...]
                header = len(name_bytes).to_bytes(2, "big") + name_bytes + len(ext_bytes).to_bytes(1, "big") + ext_bytes
                
                # How much space left in chunk for data
                max_data_in_chunk = chunk_size - len(header)
                
                # Read exactly enough to fill chunk to chunk_size (or less if file ended)
                file_part = fin.read(max_data_in_chunk)
                
                # Join header and data
                data = header + file_part
                first_chunk = False
            else:
                data = fin.read(chunk_size)
    
            if not data:
                break
            
            real_len = len(data)
            
            # Padding (fill) with random data if chunk is smaller than norm
            if real_len < chunk_size:
                data += os.urandom(chunk_size - real_len)

            nonce = os.urandom(12)
            ciphertext = aesgcm.encrypt(nonce, data, aad)

            fout.write(nonce)
            fout.write(real_len.to_bytes(4, "big"))
            fout.write(ciphertext)
            
    return os.path.basename(output_path)


def decrypt_file_stream_single(input_path: str, password: str, config=None, output_dir=None):
    """
    Stream decryption for a single file.
    Reads the first chunk, extracts filename and restores it.
    """
    if config is None: config = {}
    
    kp = get_kdf_params(config)
    aad = get_aad_bytes(config)
    chunk_size = config.get('streaming_params', {}).get('chunk_size', 64 * 1024)
    
    password_bytes = password.encode("utf-8")

    with open(input_path, "rb") as fin:
        salt = fin.read(16)

        kdf = Argon2id(salt=salt, length=kp['length'], iterations=kp['iterations'], memory_cost=kp['memory_cost'], lanes=kp['lanes'])
        key = kdf.derive(password_bytes)
        aesgcm = AESGCM(key)

        first_chunk = True
        fout = None
        output_path = None

        try:
            while True:
                nonce = fin.read(12)
                if not nonce: break 

                real_len_bytes = fin.read(4)
                if not real_len_bytes: break 
                real_len = int.from_bytes(real_len_bytes, "big")
                
                # Read (Chunk + Tag)
                ciphertext = fin.read(chunk_size + 16)
                if len(ciphertext) != chunk_size + 16:
                    raise ValueError("Повреждён контейнер или неверный размер чанка")

                # Decryption (InvalidTag raised here if password wrong)
                plaintext = aesgcm.decrypt(nonce, ciphertext, aad)
                
                # Cut padding
                data = plaintext[:real_len]

                if first_chunk:
                    # --- Parse header ---
                    offset = 0
                    
                    # 1. Name length (2 bytes)
                    name_len = int.from_bytes(data[offset:offset + 2], "big")
                    offset += 2
                    
                    # 2. Name
                    _n = data[offset:offset + name_len].decode("utf-8")
                    offset += name_len
                    
                    # 3. Extension length (1 byte)
                    ext_len = data[offset] # Take byte as int
                    offset += 1
                    
                    # 4. Extension
                    _e = data[offset:offset + ext_len].decode("utf-8")
                    offset += ext_len
                    
                    orig_filename = _n + _e
                    
                    # Determine where to save
                    if output_dir and str(output_dir).strip():
                        target_dir = output_dir
                    else:
                        target_dir = os.path.dirname(input_path)
                    
                    output_path = os.path.join(target_dir, orig_filename)
                    output_path = os.path.normpath(output_path)
                    
                    # Create folder if needed and open file for writing
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    fout = open(output_path, "wb")
                    
                    # Write rest of data (this is already file payload)
                    fout.write(data[offset:])
                    first_chunk = False
                else:
                    fout.write(data)
        finally:
            if fout: fout.close()
            
    return output_path


# === UTILITIES BLOCK (Password Generator, Hashing) ===

import hashlib 

def generate_strong_password(length: int = 20, use_digits=True, use_symbols=True) -> str:
    """
    Generates a cryptographically strong password.
    Uses only printable characters, easy to type.
    """
    # Я знаю, что мы ограничили минимальное значение 8 с помощью ползунка, но никогда не знаешь, вдруг ты решишь изменить это значение.
    if length < 4:
        raise ValueError("Длина пароля должна быть не менее 4 символов")

    # Base set: letters (uppercase and lowercase)
    chars = string.ascii_letters
    
    if use_digits:
        chars += string.digits
    
    if use_symbols:
        # Exclude complex symbols like tilde, quotes or backslash,
        # so user can type them manually easier.
        safe_symbols = "!@#$%^&*()-_=+[]{}<>:;"
        chars += safe_symbols

    while True:
        password = "".join(secrets.choice(chars) for _ in range(length))
        
        # Quality check: password must contain at least one char from selected categories
        has_digit = any(c.isdigit() for c in password) if use_digits else True
        has_symbol = any(c in safe_symbols for c in password) if use_symbols else True
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)

        if has_digit and has_symbol and has_upper and has_lower:
            return password

def calculate_file_hash(filepath: str, algorithm="sha256") -> str:
    """
    Calculates file hash (SHA-256) to check integrity.
    Reads file in chunks to avoid clogging memory.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Файл не найден: {filepath}")
        
    hasher = hashlib.sha256()
    
    # Read by 64KB
    chunk_size = 65536 
    
    with open(filepath, "rb") as f:
        while True:
            data = f.read(chunk_size)
            if not data:
                break
            hasher.update(data)
            
    return hasher.hexdigest()