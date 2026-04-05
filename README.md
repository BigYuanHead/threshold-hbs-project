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
│   ├── lamport.py
│   ├── hash_utils.py
│   ├── share.py
│   └── merkle.py
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
├── tests/
│   ├── test_lamport.py
│   ├── test_share.py
│   ├── test_signing.py
│   ├── test_verification.py
│   └── test_end_to_end.py
└── results/