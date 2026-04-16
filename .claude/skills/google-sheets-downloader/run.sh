#!/bin/bash
# Wrapper script to run the Google Sheets downloader with automatic venv management

SPREADSHEET_ID="$1"
SERVICE_ACCOUNT_PATH="$2"
OPENWEATHERMAP_API_KEY="$3"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="/tmp/gsheets_venv_$$"

# Create venv and install dependencies
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"
pip install -q google-auth-oauthlib google-auth-httplib2 google-api-python-client requests 2>/dev/null

# Run the appropriate Python script based on whether API key is provided
if [ -z "$OPENWEATHERMAP_API_KEY" ]; then
  # No API key provided, run download script
  python3 "$SCRIPT_DIR/scripts/download_sheets.py" "$SPREADSHEET_ID" "$SERVICE_ACCOUNT_PATH"
else
  # API key provided, run temperature update script
  python3 "$SCRIPT_DIR/scripts/update_temperature.py" "$SPREADSHEET_ID" "$SERVICE_ACCOUNT_PATH" "$OPENWEATHERMAP_API_KEY"
fi
EXIT_CODE=$?

# Cleanup
deactivate
rm -rf "$VENV_DIR"

exit $EXIT_CODE
