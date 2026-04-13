# Helper functions shared by the threshold protocol modules.

from core.hash_utils import xor_calculator


def xor_many(values: list[bytes]) -> bytes:
    if not isinstance(values, list):
        raise TypeError("values must be a list")
    if len(values) == 0:
        raise ValueError("values cannot be empty")
    if not all(isinstance(value, bytes) for value in values):
        raise TypeError("all values must be bytes")

    result = values[0]
    for value in values[1:]:
        result = xor_calculator(result, value)

    return result


def validate_lamport_key(key, key_name: str) -> int:
    if not isinstance(key, dict):
        raise TypeError(f"{key_name} must be a dict")
    if "zero" not in key or "one" not in key:
        raise ValueError(f"{key_name} must contain zero and one")
    if not isinstance(key["zero"], list) or not isinstance(key["one"], list):
        raise TypeError(f"{key_name} zero and one must be lists")
    if len(key["zero"]) == 0 or len(key["zero"]) != len(key["one"]):
        raise ValueError(f"{key_name} zero and one must have the same positive length")

    for label in ("zero", "one"):
        if not all(isinstance(value, bytes) for value in key[label]):
            raise TypeError(f"{key_name} {label} values must be bytes")

    return len(key["zero"])


def serialize_public_key(public_key: dict) -> bytes:
    validate_lamport_key(public_key, "public_key")
    return b"".join(public_key["zero"] + public_key["one"])


def validate_positive_int(value, value_name: str) -> None:
    if not isinstance(value, int):
        raise TypeError(f"{value_name} must be an integer")
    if value <= 0:
        raise ValueError(f"{value_name} must be positive")


def validate_power_of_two(value, value_name: str) -> None:
    validate_positive_int(value, value_name)
    if value & (value - 1) != 0:
        raise ValueError(f"{value_name} must be a power of 2")
