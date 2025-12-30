"""
Helpers for loading configuration and credentials from environment variables.
"""

from typing import Dict, Optional

from dotenv import load_dotenv
import os


def load_environment(dotenv_path: Optional[str] = ".env") -> None:
    """
    Load environment variables from a .env file and the host environment.

    Args:
        dotenv_path: Path to the .env file. Defaults to ".env".

    Returns:
        None. Modifies process environment in-place.
    """
    if dotenv_path:
        load_dotenv(dotenv_path)


def get_api_credentials() -> Dict[str, str]:
    """
    Collect credentials for Apify, Google Sheets, and X API.

    Returns:
        A dictionary containing tokens and keys sourced from environment variables.
    """
    return {
        "apify_token": os.getenv("APIFY_TOKEN", ""),
        "google_service_account_path": os.getenv("GOOGLE_SERVICE_ACCOUNT_PATH", ""),
        "x_api_key": os.getenv("X_API_KEY", ""),
        "x_api_secret": os.getenv("X_API_SECRET", ""),
        "x_access_token": os.getenv("X_ACCESS_TOKEN", ""),
        "x_access_token_secret": os.getenv("X_ACCESS_TOKEN_SECRET", ""),
    }
