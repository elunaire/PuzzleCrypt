# PuzzleCrypt

> **"A quantum computer may decrypt the pieces, but not necessarily solve the puzzle."**

PuzzleCrypt is an experimental data protection framework that combines **compression**, **fragmentation**, **deterministic permutation**, and **multi-layer encryption** using standard cryptographic tools. Its objective is not to replace post-quantum cryptography, but to investigate whether hiding the structure and ordering of information can provide an additional layer of resilience against future attackers.

---

# Overview

Traditional cryptography focuses on protecting the contents of data through encryption.

PuzzleCrypt introduces an additional concept:

## Structural Security

The idea is that recovering encrypted fragments is not necessarily equivalent to recovering the original message.

Instead of protecting only the plaintext, PuzzleCrypt also attempts to protect:

- Fragment ordering
- Reconstruction context
- Compression structure
- Dictionary location
- Relationships between data fragments

This creates a two-stage recovery problem:

```text
Recover Fragments
        +
Recover Ordering Information
        =
Recover Message
```

---

# Core Hypothesis

PuzzleCrypt is based on the following hypothesis:

> Recovering fragments ≠ Recovering the message.

Even if an attacker obtains valid decrypted fragments, reconstructing the original message may still require:

- Identifying the correct fragment order
- Locating critical reconstruction data
- Restoring the compression context
- Rebuilding a valid data stream

---

# Architecture

## Encryption

```text
Original File
      │
      ▼
Compression + AES-256 (Password 1)
      │
      ▼
inner.7z
      │
      ▼
Fragmentation
      │
      ▼
Deterministic Permutation
      │
      ▼
Permuted Fragments
      │
      ▼
Compression + AES-256 (Password 2)
      │
      ▼
PuzzleCrypt Archive (.pzc)
```

## Decryption

```text
PuzzleCrypt Archive (.pzc)
      │
      ▼
AES-256 Decryption (Password 2) + Unzip
      │
      ▼
Recover Fragments
      │
      ▼
Inverse Permutation
      │
      ▼
Reconstruct inner.7z
      │
      ▼
AES-256 Decryption (Password 1) + Unzip
      │
      ▼
Original File
```

---

# Current Implementation

PuzzleCrypt v0 is implemented in Python using:

- Python 3
- py7zr
- AES-256 encryption
- SHA-256 based deterministic permutations
- Tkinter graphical interface

The prototype uses standard and widely available tools.

No custom cryptographic primitive is introduced.

---

# Why Compression Matters

Compression is a key component of the PuzzleCrypt concept.

Many compression schemes rely on:

- Dictionaries
- Reconstruction context
- Sequential decoding

The compressed stream often contains information that must be interpreted in the correct order.

By fragmenting and permuting compressed data, PuzzleCrypt attempts to hide:

- Where the compressed stream begins
- Where important reconstruction information resides
- Which fragments are required first for successful decoding

As a result:

```text
Decrypting fragments
       does not necessarily imply
Recovering a valid compressed stream
```

---

# Security Goals

PuzzleCrypt aims to study whether information recovery can be made dependent on both:

## Cryptographic Information

```text
Ciphertext
Keys
Encrypted Blocks
```

## Structural Information

```text
Ordering
Position
Context
Dictionary Location
Fragment Relationships
```

The objective is not necessarily to make decryption harder.

The objective is to make:

```text
Successful Reconstruction
```

an indispensable and potentially difficult step.

---

# Example Workflow

## Encrypt a File

1. Select a file.
2. Enter Password 1.
3. Enter Password 2.
4. Click **Encrypt**.

Result:

```text
document.pdf
↓
enc_document.pdf.pzc
```

## Decrypt a File

1. Select a `.pzc` archive.
2. Enter Password 1.
3. Enter Password 2.
4. Click **Decrypt**.

Result:

```text
enc_document.pdf.pzc
↓
dec_document.pdf
```

---

# Current Limitations

PuzzleCrypt is currently a research prototype.

It does **not** claim:

- Information-theoretic security
- Formal post-quantum security
- Resistance against future quantum computers
- A replacement for NIST-standardized post-quantum cryptography

The purpose of the project is to explore the following research question:

> Can the protection of ordering information and reconstruction context provide an additional resilience layer even if some cryptographic protections become weaker in the future?

---

# Future Work

Potential future developments include:

- Noise (decoy) fragments
- Multiple puzzle layers
- Variable-size fragments
- Hidden stream pivots
- Graph-based reconstruction
- Compression-dictionary hiding
- Irregular puzzle geometries
- Experimental entropy analysis
- Formal reconstruction complexity studies

---

# Research Statement

PuzzleCrypt explores a simple idea:

> A future attacker may be able to decrypt the pieces, but not necessarily solve the puzzle.

By combining standard cryptographic tools with fragmentation, compression, permutation, and hidden reconstruction information, PuzzleCrypt investigates whether data recovery can be transformed from a pure decryption problem into a decryption-and-reconstruction problem.

---

# Installation

```bash
pip install py7zr
```

Run:

```bash
python PuzzleCrypt.py
```

---

# Project Status

| Item | Status |
|--------|--------|
| Compression Layer | ✅ |
| AES Internal Encryption | ✅ |
| AES External Encryption | ✅ |
| Fragmentation | ✅ |
| Deterministic Permutation | ✅ |
| GUI Interface | ✅ |
| Manifest Reconstruction | ✅ |
| Decoy Blocks | 🔬 Experimental |
| Multi-Level Puzzles | 🔬 Planned |
| Hidden Compression Dictionary | 🔬 Research |
| Quantum-Resilience Evaluation | 🔬 Research |

---

# Disclaimer

PuzzleCrypt is an experimental research project.

The software should not currently be considered a replacement for established cryptographic systems or post-quantum cryptographic standards. Its purpose is to explore the hypothesis that protecting ordering information and reconstruction context may provide an additional layer of resilience beyond conventional encryption.

---

# Author

**Etienne Lemaire**

**Project:** PuzzleCrypt

**Status:** Experimental Research Prototype

**License:** Research / Proof-of-Concept Use Only
