import tkinter as tk
import webbrowser
import sys
from gui.base_tab import BaseTab

REPO_URL = "https://github.com/GlebK1101/AES-GCM-GUI"

class AboutTab(BaseTab):
    def setup_ui(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        header_frame = tk.Frame(self.main_frame)
        header_frame.pack(fill='x', pady=(0, 10))

        tk.Label(header_frame, text="Argon2id & AES-GCM Encryptor", 
                 font=("Arial", 20, "bold"), fg="#333").pack()
        
        ver_info = f"Version 1.0.0 | Python {sys.version.split()[0]}"
        tk.Label(header_frame, text=ver_info, font=("Arial", 10), fg="#666").pack()

        link = tk.Label(header_frame, text="GitHub repository", 
                        font=("Arial", 10, "underline"), fg="blue", cursor="hand2")
        link.pack(pady=5)
        link.bind("<Button-1>", lambda e: webbrowser.open_new(REPO_URL))

        text_frame = tk.Frame(self.main_frame, bd=1, relief="sunken")
        text_frame.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y")

        self.txt = tk.Text(text_frame, font=("Consolas", 12), wrap="word",
                           yscrollcommand=scrollbar.set, padx=10, pady=10, bg="white")
        self.txt.pack(fill="both", expand=True)
        scrollbar.config(command=self.txt.yview)

        self.txt.tag_configure("h1", font=("Arial", 14, "bold"), spacing3=10, foreground="#2c3e50", justify='center')
        self.txt.tag_configure("important", foreground="#d35400", font=("Consolas", 10, "bold"))
        self.txt.tag_configure("bold", font=("Consolas", 10, "bold"))

        self.fill_manual()
        self.txt.config(state="disabled") 

    def fill_manual(self):
        manual = """
=== 1. A Note from the Author ===
This program was created as a tool for people who value complete control over their data and do not trust it to anyone else. In a sense, it is indeed designed for "paranoids" — but reasonable paranoids who understand why they need this level of protection.

At its core lie modern industrial-grade cryptographic algorithms. AES in GCM mode is used for data encryption, and Argon2id for password protection. These are not experimental solutions or homemade cryptography, but proven standards used in real security systems and resistant to known attacks.

The program does not store key copies and has no "master password" or emergency recovery method. This is a conscious choice. All responsibility for the safety of the password and encryption parameters lies with the user. If the password is forgotten or the configuration file with KDF settings is lost, data recovery will become mathematically impossible. In this case, no one can help, including the program developer.

=== 2. Tab: Single File ===
Single file encryption works by loading the entire file into the program's RAM. The program encrypts the data and immediately writes the result. The nuance is that if the file is too heavy (larger than available free RAM), the program might freeze or crash with an error. For large files (movies, archives, disk images), use the "Stream" tab.

Mandatory fields:
- File
- Password (spaces at the edges of the password are removed!)

Other fields are optional. If you do not specify them, the program will choose default values:
1. Save folder = source file folder.
2. Output filename = random character set (length defined in "Settings").
Collision protection is implemented: if a random name matches an existing one, the program will generate a different one.

The rules for decryption are the same. Important: when decrypting, we do not check if a file with that name exists. If a file with the original name already exists in the folder, it will be silently overwritten by the decrypted version. This is done intentionally for automation convenience, but please be careful.

=== 3. Tab: Stream ===
Here, the data processing method changes. Encryption and decryption occur in a "batch" manner (by chunks). The file size does not matter: you can encrypt a terabyte archive while having only 2 GB of RAM.
The size of a single chunk is set in the "Settings" tab.

Important: The container format (byte structure) in "Single File" and "Stream" modes differs. You cannot decrypt a "stream" file in the "Single File" tab and vice versa, even if the password is correct.

=== 4. Tab: Manifest ===
The encryption method is stream-based (like in item 3), but applied recursively to the entire folder structure.
This tab is designed to protect entire directories. The program takes all files, encrypts them, gives them random names, and dumps them into one common folder ("heap") without subfolders.

In parallel, a manifest.json file is created. It is NOT encrypted automatically (I recommend encrypting it separately). This file describes the map: which random name corresponds to which real file and where it was located.
This file is needed ONLY for automatic structure restoration. Its loss DOES NOT mean data loss. If you lose the manifest, you will simply get a pile of files with names like "a8z9.enc". They can be decrypted individually via the "Stream" tab — the content will be restored correctly.

=== 5. Tab: Steganography ===
Allows hiding data inside an image. Technically, data is simply appended to the end of the image file (after a special terminator byte). The size of the output image equals the sum of the source image and the hidden file.

Important limitation: In this tab, files are loaded into RAM entirely. If you try to hide a 10 GB file while having only 4 GB of memory, the program may freeze or close. There are no memory shortage checks here — calculate resources yourself.

Attention: If you send such an image via a messenger (Telegram, WhatsApp) without packing it into an archive, the server will compress the image and cut off the "extra" tail with your data. The data will be destroyed. Transfer only as a file/archive.
Upon extraction, you get both the clean image and the hidden file.

=== 6. Tab: Shredder ===
When deleting a file normally, Windows OS simply marks the disk space as "free," but the data bytes themselves remain there until they are overwritten by something else. Specialized software can easily recover them.
The shredder overwrites the file content with random garbage, then renames it to random gibberish (to hide the original filename, as it is also stored in the file system), and only then deletes it. You can delete both individual files and entire folders.

=== 7. Tab: Settings ===
Here the mathematics of protection is defined.
- Name length: Boundaries for generating random filenames.
- AAD (Additional Authenticated Data): Consider this a "second password" or a context tag. If you encrypted a file with AAD "Docs2024", you MUST specify this same string in settings during decryption. Without it, the file will not open, even if the password is correct.
- Chunk size: The size of the data portion read at a time in "Stream" and "Manifest" modes.
- Key length: Key length. 32 bytes = 256 bits (maximum for AES).
- Iterations: Number of memory passes when creating a key from a password. Forces the processor to work longer. Do not set above 4 — it will take too long.
- Memory: Amount of RAM (in KB) allocated for hash calculation. Makes the attack "expensive." If set to 65536 (64 MB), a hacker cannot run a million password guesses on a single video card — they will simply run out of memory.
- Lanes: Number of threads. With lanes=1, the attack becomes sequential, and the GPU loses its advantage.

In fields with numbers, you can write expressions: the program will understand "64*1024" as "65536". Do not forget to click "Apply settings".

=== 8. Tab: Utilities ===
Useful tools for security.
- Password Generator: Creates complex strings that are really hard to crack but possible to type manually.
- Integrity Check: Calculates the hash (digital fingerprint) of a file. If even one bit in the file changes, the hash will become completely different. Needed to check: "Did the file download without errors?".
- Master Export: Saves the current configuration, the last generated password, and hash into one JSON file. Caution: the password is in plaintext there!

=== 9. About Details ===
! Important Tip
Use a password of at least 24 characters when encrypting. It is more secure.

! Path Traversal (Escaping the folder)
The manifest.json file stores paths. An attacker can use this.
Imagine: you have a recovery folder C:\\Photos.
The manifest says: "Restore file cat.jpg".
The program does: C:\\Photos + cat.jpg = C:\\Photos\\cat.jpg. All good.
Attack: An attacker silently changes the manifest. Instead of cat.jpg, they write: ..\\..\\Windows\\System32\\virus.exe.
The symbols ".." mean "go to the folder above".
The program joins: C:\\Photos + .. + .. + Windows...
Result: You thought you were restoring photos, but the program "jumped out" of the folder and wrote a virus into the system. This program has built-in protection against such tricks.

! Shredder Pass Count
Do you need to wipe a file 3 or 7 times?
1. For Hard Disk Drives (HDD): Previously, it was believed that a "shadow" of data might remain on the edges of the magnetic track. Therefore, standards like 3 passes (DoD) and 35 passes (Gutmann) were invented. For modern HDDs, the recording density is so wild that hitting the same atom twice is impossible. Therefore, 1 pass with random data (not zeros!) is quite enough.
2. For SSDs and Flash drives: It's more complicated here. An SSD has a controller that monitors cell wear. When you say "Overwrite file in cell #100", the controller might say: "Cell #100 is tired, I will write new data to fresh cell #500, and just mark the old one as empty."
Result: physically old data remained in cell #100. Therefore, even 7 passes on an SSD do not give a 100% guarantee of destruction. The most reliable way is to use full disk erasure (Secure Erase) via BIOS.
Summary: 1 pass — enough against recovery software. 3 passes — for peace of mind. 7 passes — excessive.

! Technical Format Limitations
The program writes service data in binary form, so mathematical limits exist:
1. Filename: 2 bytes are allocated for storing the name length. This means the filename cannot exceed 65535 characters.
2. Extension: 1 byte allocated. Maximum 255 characters.
3. Chunk Size: In stream mode, 4 bytes are allocated for the data block length. This means that one chunk in settings strictly must not exceed 4 GB (4 294 967 295 bytes). If set higher, the math will overflow, and the file will be corrupted during writing.
4. For steganography, limits are shifted up by two times: 4 bytes for the name and 8 bytes for data.

! AES-GCM and "Digital Seal"
Why do we use GCM mode specifically, and not just AES?
Ordinary encryption (like in old archivers) works like a lock on a door. If you have the key (password), you open the door. But if an intruder saws off the hinges or drills a hole in the wall (changes bytes inside the encrypted file) at night, a standard algorithm won't notice. It will simply decrypt "mush" and a corrupted file for you.

AES-GCM is "Authenticated Encryption".
Imagine that we didn't just lock the data in a safe, but also hung a chemical seal on it.
During encryption, the algorithm calculates a complex checksum (Tag) of all your data. This happens at the level of cipher mathematics, not at the level of our program.

When you enter the password for decryption, AES-GCM first checks this seal:
1. If the file downloaded with an error (bad internet);
2. If a virus "corrupted" the file on the disk;
3. If a hacker intentionally changed even one bit inside the container;
...then the math simply won't match. The algorithm will issue an "InvalidTag" error and refuse to give you the data.

This guarantees absolute integrity: you get either the file byte-for-byte as the original, or an error. You will never receive a corrupted, "glitchy," or fake file.
"""
        
        self.txt.config(state="normal")
        self.txt.delete("1.0", tk.END)
        self.txt.insert("1.0", manual)
        
        count_lines = int(self.txt.index('end-1c').split('.')[0])
        for i in range(1, count_lines + 1):
            line_text = self.txt.get(f"{i}.0", f"{i}.end").strip()
            
            if not line_text:
                continue

            if line_text.startswith("==="):
                self.txt.tag_add("h1", f"{i}.0", f"{i}.end")
            elif line_text.startswith("!"):
                self.txt.tag_add("important", f"{i}.0", f"{i}.end")

        self.txt.config(state="disabled")