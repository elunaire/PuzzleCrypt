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
AES-256 (Password 2)
      │
      ▼
PuzzleCrypt Archive (.pzc)
```

## Decryption

```text
PuzzleCrypt Archive (.pzc)
      │
      ▼
AES-256 Decryption (Password 2)
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
AES-256 Decryption (Password 1)
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

Compression is
