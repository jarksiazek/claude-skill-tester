#!/usr/bin/env python3
"""
Update Temperature column (column G) in Google Sheet using OpenWeatherMap API.
Usage: python update_temperature.py <spreadsheet_id> <service_account_json_path> <openweathermap_api_key>
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
    import requests
except ImportError as e:
    print("❌ Error: Required libraries not installed.", file=sys.stderr)
    print("Install with: pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client requests", file=sys.stderr)
    print(f"Details: {str(e)}", file=sys.stderr)
    sys.exit(1)


def get_temperature_from_city(city_name, api_key):
    """
    Fetch temperature from OpenWeatherMap API for a given city.

    Args:
        city_name: Name of the city
        api_key: OpenWeatherMap API key

    Returns:
        Temperature as float, or None if fetch fails
    """
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&units=metric&appid={api_key}"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            return data.get('main', {}).get('temp')
        elif response.status_code == 404:
            return None  # City not found
        else:
            return None  # Other error
    except Exception:
        return None


def update_temperature_column(spreadsheet_id, service_account_path, api_key):
    """
    Update Temperature column (G) in Google Sheet using OpenWeatherMap API.

    Args:
        spreadsheet_id: The ID of the Google Sheet
        service_account_path: Path to the service account JSON file
        api_key: OpenWeatherMap API key

    Returns:
        List of rows with updated temperature values
    """
    # Validate inputs
    if not spreadsheet_id or not isinstance(spreadsheet_id, str):
        raise ValueError("Spreadsheet ID must be a non-empty string")

    if not service_account_path:
        raise ValueError("Service account JSON path is required")

    if not api_key:
        raise ValueError("OpenWeatherMap API key is required")

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

    # Create credentials with read+write scope
    try:
        credentials = Credentials.from_service_account_info(
            service_account_info,
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
    except Exception as e:
        raise ValueError(f"Failed to create credentials from service account: {str(e)}")

    # Build the Sheets API client
    try:
        service = build('sheets', 'v4', credentials=credentials)
    except Exception as e:
        raise RuntimeError(f"Failed to build Sheets API client: {str(e)}")

    # Get the first sheet name
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

    # Fetch all values from columns A:G
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

    # Extract values
    values = result.get('values', [])
    if not values:
        return []

    # Ensure each row has 7 columns
    formatted_rows = []
    for row in values:
        padded_row = row + [''] * (7 - len(row)) if row else [''] * 7
        formatted_rows.append(padded_row[:7])

    # Skip header row if present
    header_row = formatted_rows[0] if formatted_rows else []
    data_rows = formatted_rows[1:] if len(formatted_rows) > 1 else []

    # Fetch temperatures and prepare updates
    temperature_updates = []
    temp_mapping = []  # For display

    for idx, row in enumerate(data_rows):
        city = row[3] if len(row) > 3 else ""

        if city:
            temp = get_temperature_from_city(city, api_key)
            temperature_updates.append([temp if temp is not None else ""])
            temp_mapping.append((city, temp if temp is not None else "N/A"))
        else:
            temperature_updates.append([""])
            temp_mapping.append(("", "N/A"))

    # Prepare batch update request (update column G, starting from row 2)
    try:
        batch_update_data = [
            {
                'range': f"'{first_sheet_name}'!G2:G{len(data_rows) + 1}",
                'values': [[temp[0]] for temp in temperature_updates]
            }
        ]

        service.spreadsheets().values().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={'data': batch_update_data, 'valueInputOption': 'USER_ENTERED'}
        ).execute()
    except HttpError as e:
        raise RuntimeError(f"Failed to update temperature column (HTTP {e.resp.status}): {e.content}")
    except Exception as e:
        raise RuntimeError(f"Failed to update spreadsheet: {str(e)}")

    # Prepare updated rows for return
    updated_rows = []
    for idx, row in enumerate(data_rows):
        updated_row = row.copy()
        if len(updated_row) > 6:
            updated_row[6] = temperature_updates[idx][0]
        else:
            updated_row.append(temperature_updates[idx][0])
        updated_rows.append(updated_row)

    return header_row, updated_rows, temp_mapping


def main():
    if len(sys.argv) != 4:
        print("Usage: python update_temperature.py <spreadsheet_id> <service_account_json_path> <openweathermap_api_key>")
        print("\nExample:")
        print('  python update_temperature.py "1a2b3c4d5e6f7g8h9i0j" "/path/to/service-account.json" "your-api-key"')
        sys.exit(1)

    spreadsheet_id = sys.argv[1]
    service_account_path = sys.argv[2]
    api_key = sys.argv[3]

    try:
        header_row, updated_rows, temp_mapping = update_temperature_column(spreadsheet_id, service_account_path, api_key)

        # Define column headers
        headers = ["First Name", "Last Name", "Id", "City", "Latitude", "Longitude", "Temperature"]

        # Print readable output to console
        print("\n" + "="*120)
        print("🌡️  TEMPERATURE UPDATE RESULTS")
        print("="*120)
        print(f"Total rows updated: {len(updated_rows)}\n")

        # Print city -> temperature mapping
        print("City Temperature Mapping:")
        print("-" * 50)
        for city, temp in temp_mapping:
            temp_str = f"{temp}°C" if temp != "N/A" else temp
            print(f"  {city:<20} → {temp_str}")
        print()

        # Print updated data
        print(f"{'Row':<5} | {headers[0]:<15} | {headers[1]:<15} | {headers[2]:<10} | {headers[3]:<15} | {headers[4]:<12} | {headers[5]:<12} | {headers[6]:<15}")
        print("-" * 120)

        for i, row in enumerate(updated_rows, 1):
            col1 = str(row[0])[:15] if len(row) > 0 else ""
            col2 = str(row[1])[:15] if len(row) > 1 else ""
            col3 = str(row[2])[:10] if len(row) > 2 else ""
            col4 = str(row[3])[:15] if len(row) > 3 else ""
            col5 = str(row[4])[:12] if len(row) > 4 else ""
            col6 = str(row[5])[:12] if len(row) > 5 else ""
            col7 = str(row[6])[:15] if len(row) > 6 else ""
            print(f"{i:<5} | {col1:<15} | {col2:<15} | {col3:<10} | {col4:<15} | {col5:<12} | {col6:<12} | {col7:<15}")

        print("\n" + "="*120)
        print("📋 JSON FORMAT (Updated Data)")
        print("="*120)
        # Output as JSON
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
            for row in updated_rows
        ]
        print(json.dumps(data_json, indent=2))
        print("\n✅ Temperature column updated successfully")

    except FileNotFoundError as e:
        print(f"\n❌ FILE NOT FOUND ERROR", file=sys.stderr)
        print(f"━" * 80, file=sys.stderr)
        print(f"Message: {str(e)}", file=sys.stderr)
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
        if "api key" in error_msg:
            print(f"\nIssue: OpenWeatherMap API key is missing or invalid", file=sys.stderr)
            print(f"How to fix:", file=sys.stderr)
            print(f"1. Get a free API key from https://openweathermap.org/api", file=sys.stderr)
            print(f"2. Pass it as the third argument", file=sys.stderr)
        print(f"━" * 80 + "\n", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
    except PermissionError as e:
        print(f"\n❌ PERMISSION DENIED ERROR", file=sys.stderr)
        print(f"━" * 80, file=sys.stderr)
        print(f"Message: {str(e)}", file=sys.stderr)
        print(f"\nHow to fix:", file=sys.stderr)
        print(f"1. Open your service account JSON file", file=sys.stderr)
        print(f"2. Find the 'client_email' field", file=sys.stderr)
        print(f"3. Open your Google Sheet", file=sys.stderr)
        print(f"4. Click 'Share' and add the email with Editor access", file=sys.stderr)
        print(f"━" * 80 + "\n", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
    except (IOError, RuntimeError) as e:
        print(f"\n❌ RUNTIME ERROR", file=sys.stderr)
        print(f"━" * 80, file=sys.stderr)
        print(f"Message: {str(e)}", file=sys.stderr)
        print(f"━" * 80 + "\n", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR", file=sys.stderr)
        print(f"━" * 80, file=sys.stderr)
        print(f"Exception Type: {type(e).__name__}", file=sys.stderr)
        print(f"Message: {str(e)}", file=sys.stderr)
        print(f"━" * 80 + "\n", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
