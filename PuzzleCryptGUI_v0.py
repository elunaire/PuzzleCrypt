import tkinter as tk
from tkinter import filedialog, messagebox

import os
import json
import gettext
import hashlib
import random
import tempfile
import shutil

import py7zr


gettext.bindtextdomain('puzzle_crypt', './i18n/')
gettext.textdomain('puzzle_crypt')
_ = gettext.gettext


# =====================================================
# OUTILS / TOOLS
# =====================================================

def build_permutation(password, n):

    seed = int(
        hashlib.sha256(
            password.encode("utf-8")
        ).hexdigest(),
        16
    )

    rng = random.Random(seed)

    perm = list(range(n))
    rng.shuffle(perm)

    return perm


def split_file(filepath, chunk_size):

    blocks = []

    with open(filepath, "rb") as src:

        idx = 0

        while True:

            data = src.read(chunk_size)

            if not data:
                break

            name = f"block_{idx:05d}.bin"

            with open(name, "wb") as dst:
                dst.write(data)

            blocks.append(name)
            idx += 1

    return blocks


# =====================================================
# COMPRESSION & CHIFFREMENT (x2)
# COMPRESSION & ENCRYPTION (x2)
# =====================================================

def encrypt():

    filename = file_var.get()

    p1 = pass1_var.get()
    p2 = pass2_var.get()

    if not filename:
        messagebox.showerror(
            _("Error"),
            _("Select a file."),
        )
        return

    if not p1 or not p2:
        messagebox.showerror(
            _("Error"),
            _("The two passwords are mandatory.")
        )
        return

    work = tempfile.mkdtemp(prefix="PuzzleCrypt_")

    try:

        original_file = os.path.abspath(filename)

        basename = os.path.basename(original_file)

        os.chdir(work)

        # ---------------------------------
        # AES 1er usage/1st use
        # ---------------------------------

        with py7zr.SevenZipFile(
            "inner.7z",
            "w",
            password=p1
        ) as z:

            z.write(
                original_file,
                arcname=basename
            )

        archive_size = os.path.getsize(
            "inner.7z"
        )

        block_size = max(
            1024,
            archive_size // 128
        )

        # ---------------------------------
        # Découpage/Splitting
        # ---------------------------------

        blocks = split_file(
            "inner.7z",
            block_size
        )

        nb_blocks = len(blocks)

        # ---------------------------------
        # Permutation
        # ---------------------------------

        perm = build_permutation(
            p1,
            nb_blocks
        )

        for piece_index, block_index in enumerate(perm):

            os.rename(
                blocks[block_index],
                f"piece_{piece_index:05d}.dat"
            )

        # ---------------------------------
        # Manifest
        # ---------------------------------

        manifest = {
            "filename": basename,
            "nb_blocks": nb_blocks,
            "block_size": block_size
        }

        with open(
            "manifest.json",
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                manifest,
                f,
                indent=4
            )

        # ---------------------------------
        # AES 2e usage/2nd use
        # ---------------------------------

        with py7zr.SevenZipFile(
            "output.pzc",
            "w",
            password=p2
        ) as z:

            z.write("manifest.json")

            for f in os.listdir("."):

                if f.startswith("piece_"):
                    z.write(f)

        destination = os.path.join(
            os.path.dirname(original_file),
            f"enc_{basename}.pzc"
        )

        shutil.copy2(
            "output.pzc",
            destination
        )

        messagebox.showinfo(
            _("Success"),
            _("File created:\n\n{destination}").format(destination=destination),
        )

    except Exception as e:

        messagebox.showerror(
            _("Error"),
            str(e)
        )

    finally:

        shutil.rmtree(
            work,
            ignore_errors=True
        )


# =====================================================
# DECOMPRESSION & DECHIFFREMENT (x2)
# DECOMPRESSION & UNENCRYPTION (x2)
# =====================================================

def decrypt():

    filename = file_var.get()

    p1 = pass1_var.get()
    p2 = pass2_var.get()

    if not filename:
        messagebox.showerror(
            _("Error"),
            _("Select a .pzc file."),
        )
        return

    work = tempfile.mkdtemp(prefix="PuzzleCrypt_")

    try:

        archive_file = os.path.abspath(
            filename
        )

        # ---------------------------------
        # Extraction AES 2
        # AES 2 Extraction
        # ---------------------------------

        with py7zr.SevenZipFile(
            archive_file,
            "r",
            password=p2
        ) as z:

            z.extractall(path=work)

        # ---------------------------------
        # Lecture du manifeste
        # Reading of the manifest
        # ---------------------------------

        manifest_path = os.path.join(
            work,
            "manifest.json"
        )

        with open(
            manifest_path,
            "r",
            encoding="utf-8"
        ) as f:

            manifest = json.load(f)

        original_name = manifest["filename"]
        nb_blocks = manifest["nb_blocks"]

        # ---------------------------------
        # Permutation
        # ---------------------------------

        perm = build_permutation(
            p1,
            nb_blocks
        )

        reconstructed = [None] * nb_blocks

        for piece_index, block_index in enumerate(perm):

            piece_file = os.path.join(
                work,
                f"piece_{piece_index:05d}.dat"
            )

            with open(
                piece_file,
                "rb"
            ) as pf:

                reconstructed[block_index] = pf.read()

        # ---------------------------------
        # Reconstruction d' inner.7z
        # inner.7z reconstruction
        # ---------------------------------

        inner_path = os.path.join(
            work,
            "inner.7z"
        )

        with open(
            inner_path,
            "wb"
        ) as out:

            for block in reconstructed:

                out.write(block)

        # ---------------------------------
        # Vérification
        # Verification
        # ---------------------------------

        if not py7zr.is_7zfile(inner_path):

            raise Exception(
                _(
                    "Invalid internal archive.\n"
                    "Wrong password 1 or corrupted archive."
                )
            )

        # ---------------------------------
        # AES 1
        # ---------------------------------

        extract_dir = os.path.join(
            work,
            "extract"
        )

        os.makedirs(
            extract_dir,
            exist_ok=True
        )

        with py7zr.SevenZipFile(
            inner_path,
            "r",
            password=p1
        ) as z:

            z.extractall(path=extract_dir)

        # ---------------------------------
        # Copie du fichier restauré
        # Copy of the restored file
        # ---------------------------------

        restored_file = os.path.join(
            extract_dir,
            original_name
        )

        destination = os.path.join(
            os.path.dirname(
                archive_file
            ),
            f"dec_{original_name}"
        )

        shutil.copy2(
            restored_file,
            destination
        )

        messagebox.showinfo(
            _("Succès"),
            _("File restored:\n\n{destination}").format(destination=destination)
        )

    except Exception as e:

        messagebox.showerror(
            _("Error"),
            str(e)
        )

    finally:

        shutil.rmtree(
            work,
            ignore_errors=True
        )


# =====================================================
# GUI
# =====================================================

root = tk.Tk()

root.title("PuzzleCrypt")
root.geometry("600x230")

file_var = tk.StringVar()
pass1_var = tk.StringVar()
pass2_var = tk.StringVar()

tk.Label(
    root,
    text=_("File"),
).pack(pady=5)

tk.Entry(
    root,
    textvariable=file_var,
    width=80
).pack()

tk.Button(
    root,
    text=_("Choosing a file"),
    command=lambda: file_var.set(
        filedialog.askopenfilename()
    )
).pack(pady=5)

tk.Label(
    root,
    text=_("Password 1 (internal AES)"),
).pack()

tk.Entry(
    root,
    textvariable=pass1_var,
    show="*"
).pack()

tk.Label(
    root,
    text=_("Password 2 (external AES)"),
).pack()

tk.Entry(
    root,
    textvariable=pass2_var,
    show="*"
).pack()

tk.Button(
    root,
    text=_("Encrypt"),
    command=encrypt,
    bg="#90EE90"
).pack(fill="x", padx=10, pady=5)

tk.Button(
    root,
    text=_("Unencrypt"),
    command=decrypt,
    bg="#ADD8E6"
).pack(fill="x", padx=10)

root.mainloop()
