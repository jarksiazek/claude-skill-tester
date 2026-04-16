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


def download_seven_columns(spreadsheet_id, service_account_path):
    """
    Download the first 7 columns (A through G) from the first sheet of a Google Sheet.

    Args:
        spreadsheet_id: The ID of the Google Sheet
        service_account_path: Path to the service account JSON file

    Returns:
        List of rows with 7 columns each, or None if error occurs
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

    # Fetch values from the first 7 columns (A:G) of the first sheet
    try:
        range_name = f"'{first_sheet_name}'!A:G"
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name
        ).execute()
    except HttpError as e:
        raise RuntimeError(f"Failed to retrieve column data (HTTP {e.resp.status}): {e.content}")
    except Exception as e:
        raise RuntimeError(f"Failed to retrieve column values: {str(e)}")

    # Extract values - the result has 'values' key which is a list of rows
    # Each row is a list that may contain up to 7 elements
    values = result.get('values', [])
    if not values:
        return []

    # Ensure each row has 7 columns (pad with empty strings if needed)
    try:
        formatted_rows = []
        for row in values:
            # Pad row to 7 columns with empty strings
            padded_row = row + [''] * (7 - len(row)) if row else [''] * 7
            formatted_rows.append(padded_row[:7])  # Ensure max 7 columns
        return formatted_rows
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
        rows_data = download_seven_columns(spreadsheet_id, service_account_path)

        # Skip the first row (header row) if there's more than one row
        if len(rows_data) > 1:
            rows_data = rows_data[1:]

        # Define column headers
        headers = ["First Name", "Last Name", "Id", "City", "Latitude", "Longitude", "Temperature"]

        # Print readable output to console
        print("\n" + "="*120)
        print("📊 DATA FROM GOOGLE SHEET (7 COLUMNS)")
        print("="*120)
        print(f"Total rows: {len(rows_data)}\n")

        # Print header row
        print(f"{'Row':<5} | {headers[0]:<15} | {headers[1]:<15} | {headers[2]:<10} | {headers[3]:<15} | {headers[4]:<12} | {headers[5]:<12} | {headers[6]:<15}")
        print("-" * 120)

        # Print data rows
        for i, row in enumerate(rows_data, 1):
            col1 = str(row[0])[:15] if len(row) > 0 else ""
            col2 = str(row[1])[:15] if len(row) > 1 else ""
            col3 = str(row[2])[:10] if len(row) > 2 else ""
            col4 = str(row[3])[:15] if len(row) > 3 else ""
            col5 = str(row[4])[:12] if len(row) > 4 else ""
            col6 = str(row[5])[:12] if len(row) > 5 else ""
            col7 = str(row[6])[:15] if len(row) > 6 else ""
            print(f"{i:<5} | {col1:<15} | {col2:<15} | {col3:<10} | {col4:<15} | {col5:<12} | {col6:<12} | {col7:<15}")

        print("\n" + "="*120)
        print("📋 JSON FORMAT")
        print("="*120)
        # Output as JSON for programmatic use
        data_json = [
            {
                "First Name": row[0] if len(row) > 0 else "",
                "Last Name": row[1] if len(row) > 1 else "",
                "Id": row[2] if len(row) > 2 else "",
                "City": row[3] if len(row) > 3 else "",
                "Latitude": row[4] if len(row) > 4 else "",
                "Longitude": row[5] if len(row) > 5 else "",
                "Temperature": row[6] if len(row) > 6 else ""
            }
            for row in rows_data
        ]
        print(json.dumps(data_json, indent=2))

    except FileNotFoundError as e:
        print(f"\n❌ FILE NOT FOUND ERROR", file=sys.stderr)
        print(f"━" * 80, file=sys.stderr)
        print(f"Message: {str(e)}", file=sys.stderr)
        print(f"\nLookup Path: {service_account_path}", file=sys.stderr)
        print(f"\nHow to fix:", file=sys.stderr)
        print(f"1. Verify the service account JSON file exists", file=sys.stderr)
        print(f"2. Check the file path is correct", file=sys.stderr)
        print(f"3. Ensure the path is absolute (not relative)", file=sys.stderr)
        print(f"━" * 80 + "\n", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"\n❌ CONFIGURATION ERROR", file=sys.stderr)
        print(f"━" * 80, file=sys.stderr)
        print(f"Message: {str(e)}", file=sys.stderr)
        error_msg = str(e).lower()
        if "missing required fields" in error_msg:
            print(f"\nIssue: Service account JSON is missing required fields", file=sys.stderr)
            print(f"How to fix:", file=sys.stderr)
            print(f"1. Go to Google Cloud Console", file=sys.stderr)
            print(f"2. Create a new service account key (JSON format)", file=sys.stderr)
            print(f"3. Replace your current key file", file=sys.stderr)
        elif "not valid json" in error_msg:
            print(f"\nIssue: The JSON file is malformed", file=sys.stderr)
            print(f"How to fix:", file=sys.stderr)
            print(f"1. Open {service_account_path}", file=sys.stderr)
            print(f"2. Validate it's proper JSON (use jsonlint.com)", file=sys.stderr)
            print(f"3. Download a fresh key from Google Cloud Console", file=sys.stderr)
        elif "spreadsheet id" in error_msg:
            print(f"\nIssue: Invalid or empty spreadsheet ID", file=sys.stderr)
            print(f"Current ID: {spreadsheet_id}", file=sys.stderr)
            print(f"How to fix: Get the ID from your sheet URL: https://docs.google.com/spreadsheets/d/{{ID}}/edit", file=sys.stderr)
        print(f"━" * 80 + "\n", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
    except PermissionError as e:
        print(f"\n❌ PERMISSION DENIED ERROR", file=sys.stderr)
        print(f"━" * 80, file=sys.stderr)
        print(f"Message: {str(e)}", file=sys.stderr)
        print(f"\nThe service account doesn't have access to the spreadsheet.", file=sys.stderr)
        print(f"\nHow to fix:", file=sys.stderr)
        print(f"1. Open {service_account_path}", file=sys.stderr)
        print(f"2. Find the 'client_email' field (looks like: xxx@xxx.iam.gserviceaccount.com)", file=sys.stderr)
        print(f"3. Copy the email address", file=sys.stderr)
        print(f"4. Open your Google Sheet", file=sys.stderr)
        print(f"5. Click 'Share' and paste the email", file=sys.stderr)
        print(f"6. Grant at least 'Viewer' access", file=sys.stderr)
        print(f"7. Try again", file=sys.stderr)
        print(f"━" * 80 + "\n", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
    except (IOError, RuntimeError) as e:
        print(f"\n❌ RUNTIME ERROR", file=sys.stderr)
        print(f"━" * 80, file=sys.stderr)
        print(f"Message: {str(e)}", file=sys.stderr)
        error_msg = str(e).lower()
        print(f"\nDebugging tips:", file=sys.stderr)
        if "spreadsheet not found" in error_msg or "404" in error_msg:
            print(f"- The spreadsheet ID might be wrong: {spreadsheet_id}", file=sys.stderr)
            print(f"- The spreadsheet might have been deleted", file=sys.stderr)
        elif "access" in error_msg or "denied" in error_msg or "403" in error_msg:
            print(f"- The service account may not be shared on the spreadsheet", file=sys.stderr)
        else:
            print(f"- Check your internet connection", file=sys.stderr)
            print(f"- Verify the spreadsheet ID is correct: {spreadsheet_id}", file=sys.stderr)
            print(f"- Check that the spreadsheet is not locked or archived", file=sys.stderr)
            print(f"- Ensure the Google Sheets API is enabled in Cloud Console", file=sys.stderr)
        print(f"\nFull traceback:", file=sys.stderr)
        print(f"━" * 80 + "\n", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR", file=sys.stderr)
        print(f"━" * 80, file=sys.stderr)
        print(f"Exception Type: {type(e).__name__}", file=sys.stderr)
        print(f"Message: {str(e)}", file=sys.stderr)
        print(f"\nInputs used:", file=sys.stderr)
        print(f"  - Spreadsheet ID: {spreadsheet_id}", file=sys.stderr)
        print(f"  - Service Account Path: {service_account_path}", file=sys.stderr)
        print(f"\nFull traceback for debugging:", file=sys.stderr)
        print(f"━" * 80 + "\n", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)


if __name__ == '__main__':
    main()
