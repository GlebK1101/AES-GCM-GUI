import os

STEGO_SIGNATURE = b"STG_V2.0" 

def hide_data_in_image(cover_path: str, secret_path: str, output_path: str):
    if not os.path.exists(cover_path): raise FileNotFoundError(f"File missing: {cover_path}")
    if not os.path.exists(secret_path): raise FileNotFoundError(f"File missing: {secret_path}")

    # Prepare names
    cover_name = os.path.basename(cover_path).encode('utf-8')
    secret_name = os.path.basename(secret_path).encode('utf-8')
    
    with open(secret_path, "rb") as f:
        secret_data = f.read()
    
    secret_len = len(secret_data)

    with open(cover_path, "rb") as f_cov, open(output_path, "wb") as f_out:
        # 1. Image
        f_out.write(f_cov.read())
        # 2. Secret data
        f_out.write(secret_data)
        
        # 3. METADATA (written in reverse order for convenience or sequentially)
        # Write: Secret Filename -> Secret Name Length -> Image Name -> Image Name Length
        
        f_out.write(secret_name)
        f_out.write(len(secret_name).to_bytes(4, 'big'))
        
        f_out.write(cover_name)
        f_out.write(len(cover_name).to_bytes(4, 'big'))
        
        # 4. Data size and signature
        f_out.write(secret_len.to_bytes(8, 'big'))
        f_out.write(STEGO_SIGNATURE)

def extract_data_from_image(stego_path: str, output_dir: str):
    if not os.path.exists(stego_path): raise FileNotFoundError(f"File missing: {stego_path}")

    file_size = os.path.getsize(stego_path)
    sig_len = len(STEGO_SIGNATURE)
    
    with open(stego_path, "rb") as f:
        # 1. Check signature
        f.seek(-sig_len, 2)
        if f.read() != STEGO_SIGNATURE:
            raise ValueError("Hidden data not found (no signature).")
            
        # 2. Read sizes (from the end)
        f.seek(-(sig_len + 8), 2)
        data_len = int.from_bytes(f.read(8), 'big')
        
        f.seek(-(sig_len + 8 + 4), 2)
        len_name_img = int.from_bytes(f.read(4), 'big')
        
        f.seek(-(sig_len + 8 + 4 + len_name_img), 2)
        name_img = f.read(len_name_img).decode('utf-8')
        
        f.seek(-(sig_len + 8 + 4 + len_name_img + 4), 2)
        len_name_sec = int.from_bytes(f.read(4), 'big')
        
        f.seek(-(sig_len + 8 + 4 + len_name_img + 4 + len_name_sec), 2)
        name_sec = f.read(len_name_sec).decode('utf-8')
        
        # Calculate start
        meta_size = sig_len + 8 + 4 + len_name_img + 4 + len_name_sec
        secret_start_pos = file_size - meta_size - data_len
        
        if secret_start_pos < 0:
            raise ValueError("File corrupted (incorrect sizes).")

        # --- OVERWRITE CHECK ---
        path_img = os.path.join(output_dir, name_img)
        path_sec = os.path.join(output_dir, name_sec)
        
        if os.path.exists(path_img):
            raise FileExistsError(f"File already exists: {name_img}")
        if os.path.exists(path_sec):
            raise FileExistsError(f"File already exists: {name_sec}")

        # --- EXTRACTION ---
        
        # A) Original image
        f.seek(0)
        clean_image_data = f.read(secret_start_pos)
        
        # B) Secret data
        f.seek(secret_start_pos)
        secret_data = f.read(data_len)

    # --- SAVE ---
    # Create folder if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    with open(path_img, "wb") as f:
        f.write(clean_image_data)
        
    with open(path_sec, "wb") as f:
        f.write(secret_data)
        
    return name_img, name_sec