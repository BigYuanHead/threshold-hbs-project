# threshold-hbs-project
6453 Team Project


## Project Overview
This project implements a proof-of-concept threshold hash-based signature system based on Lamport one-time signatures and additive secret sharing.

The goal is to simulate a distributed signing setting where multiple parties collaboratively produce a valid signature without any single party holding the full signing capability.

The implementation includes:
- Cryptographic primitives and utility functions
- Lamport signature core
- Merkle tree construction
- Baseline stateful HBS workflow
- Threshold setup and additive secret sharing
- Distributed signing workflow
- Signature share combination
- Signature verification
- Distributed role separation for trusted server, parties, untrusted server, and verifier
- Extension 1 for k-of-n threshold construction
- Extension 3 for batch signing
- Extension 5 for Winternitz support
- Benchmarking under different settings
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
│── extension_1/
│   ├── kofn_party.py
│   ├── kofn_sercer.py
│   ├──kofn_setup.py
│   └──kofn_verifier.py
├── extension_3/
│   └── batch_threshold.py
├── extension_5/
│   ├── winternitz_ots.py
│   ├── wz_party.py
│   ├── wz_server.py
│   ├── wz_setup.py
│   ├── wz_verifier.py
│   └── winternitz_standardized.py
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
- `extension_1/kofn_setup.py`  
  Completed k-of-n threshold setup:
  - build one k-of-k Lamport subtree for each k-party subset
  - XOR-share each subtree key only among the parties in that subset
  - build a global Merkle tree over subtree roots
  - generate party share bundles containing all subtrees each party belongs to

- `extension_1/kofn_party.py`  
  Completed k-of-n party role:
  - stores subset-specific Lamport key shares
  - signs only when the selected subtree contains the party
  - prevents keyid reuse inside the same subtree
  - keeps refused message support

- `extension_1/kofn_server.py`  
  Completed k-of-n untrusted aggregator role:
  - accepts exactly k selected parties instead of all n parties
  - chooses the matching k-of-k subtree from the selected party ids
  - combines the k signature shares into the final Lamport signature
  - keeps common signed_data fields: keyid, public_key, signature, and path

- `extension_1/kofn_verifier.py`  
  Completed k-of-n verification:
  - verifies the Lamport signature on the message or batch root
  - verifies the public key path inside the selected subtree
  - verifies the selected subtree root against the global root
  - supports verify(message_or_root, signed_data, root)-style verification

### Extension 3: Use Merkle trees on the Lamport tree leaves to buffer then batch sign messages efficiently and update the verification algorithm to support this.
- `batch_threshold.py`  
  Completed extension 3 batch sign:
  - build a Merkle tree over multiple messages
  - sign only batch root
  - store message authentication path
  - verifies message and threshold signitures
  - rrejects wrong message, indexes and refused keyid

### Extension 5: Add support for Winternitz.
- `winternitz_ots.py`  
  Completed standalone Winternitz OTS:
  - Winternitz key generation
  - message signing
  - signature verification
  - wrong message and wrong signature rejection

- `winternitz_standardized.py`  
  Completed threshold-compatible Winternitz backend prototype:
  - XOR sharing of precomputed Winternitz chain states
  - signature share generation for each party
  - XOR combination of signature shares
  - verification of the combined Winternitz signature

- `wz_setup.py`  
  Completed Winternitz threshold setup:
  - Winternitz key material generation
  - party share bundle generation
  - Merkle root construction over Winternitz public keys
  - authentication path generation for each keyid
  - public parameter generation

- `wz_party.py`  
  Completed Winternitz party role:
  - local storage of Winternitz key shares
  - Winternitz signature share generation
  - keyid reuse prevention
  - refused message support

- `wz_server.py`  
  Completed Winternitz untrusted aggregator role:
  - request Winternitz signature shares from all parties
  - reject incomplete signing attempts
  - combine accepted signature shares
  - output Lamport-like signed_data format

- `wz_verifier.py`  
  Completed Winternitz verifier role:
  - Winternitz signature verification
  - public key Merkle authentication path verification
  - verification using message, signed_data, and public root
