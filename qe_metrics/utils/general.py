from typing import Any

from simple_logger.logger import get_logger


LOGGER = get_logger(name=__name__)


def verify_creds(creds: dict[str, Any], required_keys: list[str]) -> bool:
    """
    Check if credentials exist

    Args:
        creds (dict[str, Any]): Dictionary of credentials
        required_keys (list[str]): List of required keys

    Returns:
        bool: True if credentials exist, False otherwise
    """
    missing_keys = [key for key in required_keys if creds.get(key) is None]

    if missing_keys:
        missing_keys_str = ", ".join(missing_keys)
        raise ValueError(f"Missing keys in the configuration file: {missing_keys_str}")

    return all(creds.get(key) is not None for key in required_keys)
