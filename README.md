# Argon2id & AES-GCM Encryptor

A robust, offline, and transparent encryption tool designed for users who demand absolute control over their data. Built with Python, `tkinter`, and the `cryptography` library.

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Stable-orange.svg)

## Philosophy

This program was created for reasonable "paranoids". It does not trust anyone—not the cloud, not the OS, and not even the developer.
*   **No Backdoors:** There are no master passwords or recovery keys.
*   **No Cloud:** Everything runs locally on your machine.
*   **No Pity:** If you lose your password or your KDF configuration, your data is mathematically irretrievable.

## Technical Security

We use industry-standard, proven cryptographic primitives. No "home-brewed" crypto.

1.  **AES-256-GCM (Galois/Counter Mode):**
    *   **Confidentiality:** 256-bit encryption.
    *   **Integrity (Authenticated Encryption):** GCM mode calculates a cryptographic tag (checksum) for the data. If a file is corrupted, altered by a virus, or tampered with by a hacker, the decryption will fail with an `InvalidTag` error. You will never receive corrupted or manipulated data.
    *   **AAD (Additional Authenticated Data):** Allows binding the encrypted data to a specific context string.

2.  **Argon2id (Key Derivation):**
    *   Winner of the Password Hashing Competition.
    *   Protects against GPU/ASIC brute-force attacks by requiring significant RAM and CPU time to derive the encryption key from your password.

## Project Structure

```text
.
├── main.py                  # Entry point of the application
├── core/                    # Core logic (Cryptography & File Operations)
│   ├── crypto_manager.py    # AES-GCM and Argon2id implementation
│   ├── shredder_manager.py  # Secure deletion logic
│   └── stego_manager.py     # Steganography logic
├── gui/                     # Graphical User Interface (Tkinter)
│   ├── app.py               # Main GUI application class
│   ├── base_tab.py          # Base class for all tabs (helper methods)
│   └── tabs/
│       ├── encryption.py    # Single file encryption (RAM based)
│       ├── stream_single.py # Stream encryption (Chunk based)
│       ├── manifest.py      # Directory encryption with structure preservation
│       ├── stego.py         # Hiding data in images
│       ├── shredder.py      # Secure file wiper
│       ├── settings.py      # KDF and General parameters
│       ├── utilities.py     # Password gen, Hashing, Export
│       └── about.py         # Manual and info
└── requirements.txt         # List of Python dependencies
```

##  Features

### 1. Single File Encryption
Loads the entire file into RAM. Best for small to medium-sized files where maximum speed is required.
*   *Note:* Limited by your available RAM.

### 2. Stream Encryption (Chunk-based)
Reads and writes files in small chunks (e.g., 64KB).
*   **Low Memory Usage:** Can encrypt files of any size (even TBs) on a machine with 2GB RAM.
*   **Size Masking:** Encrypted files are padded to match the chunk size alignment, slightly obscuring exact file sizes.

### 3. Manifest (Folder Encryption)
Encrypts an entire directory structure recursively.
*   Files are renamed to random strings (e.g., `a8z9_k2.enc`) and moved to a single "Vault" folder.
*   A `manifest.json` file is created to map random names back to the original directory structure.
*   *Tip:* Encrypt the `manifest.json` separately for maximum security.

### 4. Steganography
Hides encrypted archives or files inside standard images (JPG, PNG).
*   The output looks like a normal image.
*   Extracts both the clean image and the secret data.

### 5. File Shredder
Irreversibly deletes files or folders.
*   Overwrites data with random noise before deletion.
*   Renames files before deletion to hide filenames from file system recovery tools.
*   Configurable number of passes (1 to 7).

### 6. Utilities
*   **Password Generator:** Generates strong, high-entropy passwords.
*   **Integrity Check:** Calculates SHA-256 hashes to verify file integrity.
*   **Session Export:** Save your current config, password, and hash to a JSON file (use with caution!).

### 7. IMPORTANT

**Please be sure to read the "About" tab in the program.**

##  Installation & Usage

### Prerequisites
*   Python 3.8+
*   `cryptography` library

### Setup
1.  Clone the repository:
    ```bash
    git clone https://github.com/GlebK1101/AES-GCM.git
    cd AES-GCM
    ```
2.  Install dependencies:
    ```bash
    pip install cryptography
    ```
3.  Run the application:
    ```bash
    python main.py
    ```

## Configuration (Settings Tab)

The **Settings** tab is crucial. It controls the KDF (Key Derivation Function) parameters.
*   **Memory Cost:** How much RAM is needed to unlock the file. Higher = safer against brute-force, but slower to open.
*   **Iterations:** How many times the math is repeated.
*   **Chunk Size:** Controls memory usage in Stream mode.

**⚠️ IMPORTANT:** To decrypt a file, you must use the **exact same** KDF settings (Iterations, Memory, Key Length) that were used during encryption. If you change them, you won't be able to decrypt your old files even with the correct password.

## ⚠️ Disclaimer

This software is provided "as is", without warranty of any kind.
*   If you lose your password, **your data is lost.**
*   If you delete or lose the `manifest.json` in Manifest mode, you lose the folder structure (files can still be decrypted individually via Stream tab).
*   The developer is not responsible for data loss caused by user error or hardware failure.

The program does not overwrite your data, but makes encrypted copies, but it is still better to make backup copies of your data before encryption!
