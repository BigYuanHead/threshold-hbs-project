# threshold-hbs-project
6453 Team Project


## Project Overview
This project implements a proof-of-concept threshold hash-based signature system based on Lamport one-time signatures and additive secret sharing.

The goal is to simulate a distributed signing setting where multiple parties collaboratively produce a valid signature without any single party holding the full signing capability.

The implementation includes:
- Lamport signature core
- Additive secret sharing
- Distributed signing workflow
- Signature verification
- Benchmarking under different settings

---

## Team Members
- Member 1: Lamport signature core, verification
- Member 2: Secret sharing and key distribution
- Member 3: Distributed signing workflow
- Member 4: Benchmarking, testing, documentation

---

## Project Structure

```text
project/
├── README.md
├── requirements.txt
├── main.py
├── config.py
├── core/
│   ├── hash_utils.py
│   ├── lamport_ots.py
│   ├── merkle.py
│   └── baseline.py
├── entities/
│   ├── trusted_server.py
│   ├── untrusted_server.py
│   ├── party.py
│   └── verifier.py
├── protocol/
│   ├── setup.py
│   ├── signing.py
│   ├── combine.py
│   └── verify.py
├── benchmark/
│   ├── bench_keygen.py
│   ├── bench_sign.py
│   ├── bench_verify.py
│   └── bench_scaling.py
├── test/
│   ├── test_lamport.py
│   ├── test_share.py
│   ├── test_signing.py
│   ├── test_verification.py
│   ├── test_end_to_end.py
│   └── test_threshold_end_to_end.py
├── extension_3/
│   └── batch_threshold.py
└── results/
```
---

## Minimal Threshold HBS Workflow
Core baseline modules have been implemented:

- `core/hash_utils.py`  
  Completed basic helper functions:
  - SHA-256 hashing
  - XOR calculation
  - bit conversion

- `core/lamport_ots.py`  
  Completed Lamport one-time signature:
  - key generation
  - signing
  - verification
  - basic input checking

- `core/merkle.py`  
  Completed Merkle tree:
  - tree construction
  - authentication path generation
  - path verification
  - basic boundary checking

- `core/baseline.py`  
  Completed baseline stateful HBS:
  - multiple one-time key generation
  - Merkle root construction
  - signing with keyid
  - key reuse prevention
  - signature verification

The minimal threshold HBS workflow has also been implemented as an n-of-n scheme:

- `protocol/setup.py`  
  Completed threshold setup and key sharing:
  - Lamport private key generation through the existing core module
  - XOR additive sharing of Lamport secret values
  - Merkle root construction over Lamport public keys
  - public parameter and party share bundle generation

- `protocol/signing.py`  
  Completed signature share generation:
  - message hash bit conversion
  - per-bit selection of zero/one key shares
  - signature share output for each party

- `protocol/combine.py`  
  Completed signature share combination:
  - validation of signature share structure
  - XOR combination of all party shares
  - reconstruction of a standard Lamport signature

- `protocol/verify.py`  
  Completed independent threshold signature verification:
  - Lamport signature verification
  - public key Merkle authentication path verification
  - verification using only the message, signed data, and public root

- `entities/trusted_server.py`  
  Completed trusted dealer role:
  - threshold key material setup
  - public parameter generation
  - party share distribution

- `entities/party.py`  
  Completed party signing role:
  - local storage of key shares
  - signature share generation
  - key reuse prevention
  - refusal response support

- `entities/untrusted_server.py`  
  Completed untrusted aggregator role:
  - request signing shares from all parties
  - reject incomplete signing attempts
  - combine accepted shares into a final signature

- `entities/verifier.py`  
  Completed verifier role:
  - public root based verification
  - wrapper around the threshold verification protocol

- `main.py`  
  Completed end-to-end demo:
  - trusted setup
  - party creation
  - untrusted signature aggregation
  - final verification

- `test/test_threshold_end_to_end.py`  
  Completed threshold workflow tests:
  - XOR share reconstruction
  - threshold sign and verify
  - wrong message rejection
  - repeated keyid refusal


## Minimal Threshold HBS Workflow with Extensions
### Extension 1: Have k-of-k subtrees in order to produce a k-of-n scheme rather than n-of-n.

### Extension 3: Use Merkle trees on the Lamport tree leaves to buffer then batch sign messages efficiently and update the verification algorithm to support this.
- `batch_threshold.py`  
  Completed extension 3 batch sign:
  - build a Merkle tree over multiple messages
  - sign only batch root
  - store message authentication path
  - verifies message and threshold signitures
  - rrejects wrong message, indexes and refused keyid

### Extension 5: Add support for Winternitz.