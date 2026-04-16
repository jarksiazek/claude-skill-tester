#!/usr/bin/env python3
"""
Download first column from Google Sheet using service account authentication.
Usage: python download_sheets.py <spreadsheet_id> <service_account_json_path>
"""

import sys
import os
import json
import traceback
from pathlib import Path

try:
    from google.oauth2.service_account import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError as e:
    print("❌ Error: Required Google libraries not installed.", file=sys.stderr)
    print("Install with: pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client", file=sys.stderr)
    print(f"Details: {str(e)}", file=sys.stderr)
    sys.exit(1)


def download_first_column(spreadsheet_id, service_account_path):
    """
    Download the first column from the first sheet of a Google Sheet.

    Args:
        spreadsheet_id: The ID of the Google Sheet
        service_account_path: Path to the service account JSON file

    Returns:
        List of values from the first column, or None if error occurs
    """
    # Validate inputs
    if not spreadsheet_id or not isinstance(spreadsheet_id, str):
        raise ValueError("Spreadsheet ID must be a non-empty string")

    if not service_account_path:
        raise ValueError("Service account JSON path is required")

    # Check if service account file exists
    sa_path = Path(service_account_path)
    if not sa_path.exists():
        raise FileNotFoundError(f"Service account file not found at: {service_account_path}")

    # Load service account credentials
    try:
        with open(service_account_path, 'r') as f:
            service_account_info = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Service account file is not valid JSON: {str(e)}")
    except Exception as e:
        raise IOError(f"Failed to read service account file: {str(e)}")

    # Validate service account structure
    required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email']
    missing_fields = [field for field in required_fields if field not in service_account_info]
    if missing_fields:
        raise ValueError(f"Service account JSON is missing required fields: {', '.join(missing_fields)}")

    # Create credentials
    try:
        credentials = Credentials.from_service_account_info(
            service_account_info,
            scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
        )
    except Exception as e:
        raise ValueError(f"Failed to create credentials from service account: {str(e)}")

    # Build the Sheets API client
    try:
        service = build('sheets', 'v4', credentials=credentials)
    except Exception as e:
        raise RuntimeError(f"Failed to build Sheets API client: {str(e)}")

    # Get the first sheet name and retrieve values from column A
    try:
        spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    except HttpError as e:
        if e.resp.status == 404:
            raise ValueError(f"Spreadsheet not found. Check the spreadsheet ID: {spreadsheet_id}")
        elif e.resp.status == 403:
            raise PermissionError(f"Access denied. Is the sheet shared with the service account email from your JSON?")
        else:
            raise RuntimeError(f"Failed to access spreadsheet: {e.content}")
    except Exception as e:
        raise RuntimeError(f"Failed to retrieve spreadsheet metadata: {str(e)}")

    try:
        if not spreadsheet.get('sheets'):
            raise ValueError("Spreadsheet has no sheets")
        first_sheet_name = spreadsheet['sheets'][0]['properties']['title']
    except (KeyError, IndexError) as e:
        raise ValueError(f"Unable to determine first sheet name: {str(e)}")

    # Fetch values from the first column (A:A) of the first sheet
    try:
        range_name = f"'{first_sheet_name}'!A:A"
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name
        ).execute()
    except HttpError as e:
        raise RuntimeError(f"Failed to retrieve column data (HTTP {e.resp.status}): {e.content}")
    except Exception as e:
        raise RuntimeError(f"Failed to retrieve column values: {str(e)}")

    # Extract values - the result has 'values' key which is a list of rows
    # Since we're getting column A, each row is a list with one element
    values = result.get('values', [])
    if not values:
        return []

    # Flatten the list (convert [[val1], [val2], ...] to [val1, val2, ...])
    try:
        flattened = [row[0] if row else '' for row in values]
        return flattened
    except Exception as e:
        raise RuntimeError(f"Failed to process column data: {str(e)}")


def main():
    if len(sys.argv) != 3:
        print("Usage: python download_sheets.py <spreadsheet_id> <service_account_json_path>")
        print("\nExample:")
        print('  python download_sheets.py "1a2b3c4d5e6f7g8h9i0j" "/path/to/service-account.json"')
        sys.exit(1)

    spreadsheet_id = sys.argv[1]
    service_account_path = sys.argv[2]

    try:
        column_data = download_first_column(spreadsheet_id, service_account_path)

        # Print readable output to console
        print("\n" + "="*60)
        print("📊 FIRST COLUMN DATA FROM GOOGLE SHEET")
        print("="*60)
        print(f"Total rows: {len(column_data)}\n")

        for i, value in enumerate(column_data, 1):
            print(f"  [{i}] {value}")

        print("\n" + "="*60)
        print("📋 JSON FORMAT")
        print("="*60)
        # Output as JSON for programmatic use
        print(json.dumps(column_data, indent=2))

    except FileNotFoundError as e:
        print(f"❌ File Error: {str(e)}", file=sys.stderr)
        print(f"\nMake sure the service account JSON file exists at: {service_account_path}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"❌ Configuration Error: {str(e)}", file=sys.stderr)
        if "missing required fields" in str(e).lower():
            print("\nYour service account JSON is missing required fields.", file=sys.stderr)
            print("Download a new service account key from Google Cloud Console.", file=sys.stderr)
        elif "not valid json" in str(e).lower():
            print(f"\nThe file at {service_account_path} is not valid JSON.", file=sys.stderr)
            print("Make sure it's a proper JSON file.", file=sys.stderr)
        sys.exit(1)
    except PermissionError as e:
        print(f"❌ Permission Error: {str(e)}", file=sys.stderr)
        print("\nHow to fix:", file=sys.stderr)
        print("1. Open your service account JSON file", file=sys.stderr)
        print("2. Find the 'client_email' field", file=sys.stderr)
        print("3. Share your Google Sheet with that email address", file=sys.stderr)
        print("4. Make sure it has at least 'Viewer' access", file=sys.stderr)
        sys.exit(1)
    except (IOError, RuntimeError) as e:
        print(f"❌ Runtime Error: {str(e)}", file=sys.stderr)
        print("\nDebugging tips:", file=sys.stderr)
        print("- Check your internet connection", file=sys.stderr)
        print("- Verify the spreadsheet ID is correct", file=sys.stderr)
        print("- Check that the spreadsheet is not locked or archived", file=sys.stderr)
        if "DEBUG" in os.environ:
            print("\nFull traceback:", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected Error: {str(e)}", file=sys.stderr)
        print("\nPlease report this issue with the following details:", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
