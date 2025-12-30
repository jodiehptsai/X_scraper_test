"""
Google Sheets client utilities using gspread and service account credentials.

This module encapsulates authentication and basic worksheet operations:
fetching worksheets, reading rows as dictionaries, and appending new rows.

Example:
    >>> client = GoogleSheetsClient(spreadsheet_name="Automation Config")
    >>> rows = client.read_records("profiles")
    >>> client.append_row("logs", ["post_id", "status", "timestamp"])
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List

import gspread
from google.oauth2.service_account import Credentials

DEFAULT_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


class GoogleSheetsClient:
    """
    Lightweight wrapper around gspread for interacting with a target spreadsheet.

    Purpose:
        Provide authenticated access to a Google Sheet for reading structured data
        and appending new rows used in the automation pipeline.

    API behavior:
        - Authenticates using a service account JSON file located at the path in
          environment variable GOOGLE_SERVICE_ACCOUNT_PATH.
        - Opens the spreadsheet by ID (GOOGLE_SPREADSHEET_ID) when set, otherwise
          by the provided spreadsheet name.
        - Exposes helper methods for fetching worksheets, reading records, and
          appending rows with type hints for clarity.

    Example usage:
        client = GoogleSheetsClient(spreadsheet_name="Automation Config")
        profiles = client.read_records("profiles")
        client.append_row("logs", ["post_id", "sent", "2024-01-01T00:00:00Z"])

    Note:
        The reference sheet for this project contains X profile URLs in column E
        (worksheet "profiles") of spreadsheet
        `1gr9wMTJTDEFlsqGF8nSMJ4fXyBjNP2RvTdVyWvmuG00`.
    """

    def __init__(self, spreadsheet_name: str, spreadsheet_id: str | None = None):
        service_account_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_PATH")
        if not service_account_path:
            raise RuntimeError("GOOGLE_SERVICE_ACCOUNT_PATH is required but missing.")

        credentials_path = Path(service_account_path)
        if not credentials_path.is_file():
            raise RuntimeError(f"Service account file not found at {credentials_path}")

        credentials = Credentials.from_service_account_file(
            str(credentials_path),
            scopes=DEFAULT_SCOPES,
        )
        client = gspread.authorize(credentials)

        env_spreadsheet_id = os.getenv("GOOGLE_X_ACCOUNT_ID")
        spreadsheet_id = spreadsheet_id or env_spreadsheet_id
        try:
            if spreadsheet_id:
                self.spreadsheet = client.open_by_key(spreadsheet_id)
            else:
                self.spreadsheet = client.open(spreadsheet_name)
        except gspread.SpreadsheetNotFound as exc:
            raise RuntimeError(
                f"Spreadsheet not found. Name='{spreadsheet_name}', "
                f"ID='{spreadsheet_id or 'unset'}'."
            ) from exc

    def get_sheet(self, sheet_name: str) -> Any:
        """
        Retrieve a worksheet by name.

        Args:
            sheet_name: Name of the worksheet to fetch.

        Returns:
            A gspread Worksheet instance.

        Raises:
            RuntimeError: If the worksheet cannot be located.
        """
        try:
            return self.spreadsheet.worksheet(sheet_name)
        except gspread.WorksheetNotFound as exc:
            raise RuntimeError(f"Worksheet '{sheet_name}' not found.") from exc

    def read_records(self, sheet_name: str) -> List[Dict[str, Any]]:
        """
        Read all rows from a worksheet as a list of dictionaries.

        Args:
            sheet_name: Name of the worksheet to read.

        Returns:
            A list where each element represents a row keyed by column header.

        Raises:
            RuntimeError: If the worksheet cannot be located.
        """
        worksheet = self.get_sheet(sheet_name)
        return worksheet.get_all_records()

    def append_row(self, sheet_name: str, row: List[Any]) -> None:
        """
        Append a row to the end of a worksheet.

        Args:
            sheet_name: Name of the worksheet to write to.
            row: Sequence of values to append as a new row.

        Returns:
            None. The operation writes data to the sheet.

        Raises:
            RuntimeError: If the worksheet cannot be located.
        """
        worksheet = self.get_sheet(sheet_name)
        worksheet.append_row(row, value_input_option="USER_ENTERED")


# Backward-compatible placeholders for higher-level workflow stubs.
def get_sheet_client(spreadsheet_name: str) -> GoogleSheetsClient:
    """
    Convenience wrapper to instantiate a GoogleSheetsClient.
    """
    return GoogleSheetsClient(spreadsheet_name=spreadsheet_name)


def read_profiles(sheet_client: GoogleSheetsClient, sheet_name: str) -> List[Dict[str, Any]]:
    """
    Placeholder for reading profile definitions; to be implemented with project-specific parsing.
    """
    raise NotImplementedError("Profile reading is not yet implemented.")


def log_interaction(sheet_client: GoogleSheetsClient, sheet_name: str, record: Dict[str, Any]) -> None:
    """
    Placeholder for logging interactions; to be implemented with project-specific parsing.
    """
    raise NotImplementedError("Logging interactions is not yet implemented.")


def write_review_queue(sheet_client: GoogleSheetsClient, sheet_name: str, rows: List[Dict[str, Any]]) -> None:
    """
    Placeholder for writing review queue entries; to be implemented with project-specific parsing.
    """
    raise NotImplementedError("Review queue writing is not yet implemented.")
