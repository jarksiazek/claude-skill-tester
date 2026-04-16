---
name: google-sheets-downloader
description: Download data from a Google Sheet and extract the first column. Use this skill whenever the user needs to fetch data from Google Sheets, wants to read spreadsheet values into JSON, or needs to integrate Google Sheets data into their workflow. Accepts two arguments - the spreadsheet ID and the path to a Google service account JSON file for authentication.
compatibility: Python 3.7+
---

# Google Sheets Downloader Skill

This skill downloads data from a Google Sheet and extracts the first column from the first sheet, returning it as JSON.

## What it does

- Authenticates with Google Sheets API using a service account
- Fetches the first sheet from a specified Google Sheet
- Extracts all values from the first column
- Prints the data in a readable format to the console with row numbers
- Returns the data as JSON for programmatic use
- Prints errors clearly if something goes wrong

## How to use it

The skill requires two arguments:

1. **Spreadsheet ID** - The ID of your Google Sheet (found in the URL: `https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit`)
2. **Service Account JSON Path** - Full path to your Google service account JSON file (e.g., `/path/to/service-account.json`)

### Example usage

```
Download the first column from my Google Sheet with ID "1a2b3c4d5e6f" 
using the service account at "/Users/me/credentials/google-key.json"
```

## How it works

The skill will:

1. Load the service account credentials from the JSON file
2. Authenticate with Google Sheets API
3. Fetch values from the first sheet
4. Extract the first column (column A)
5. Return as JSON array
6. If errors occur, print the error cause clearly

## Output format

### Success - Console Output:
```
============================================================
📊 FIRST COLUMN DATA FROM GOOGLE SHEET
============================================================
Total rows: 4

  [1] Header
  [2] Value 1
  [3] Value 2
  [4] Value 3

============================================================
📋 JSON FORMAT
============================================================
[
  "Header",
  "Value 1",
  "Value 2",
  "Value 3"
]
```

### Error:
```
Error: [specific error message explaining what went wrong]
```

## Setup: Getting a service account

To use this skill, you need a Google service account:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Sheets API
4. Go to "Credentials" → "Create Credentials" → "Service Account"
5. Create a key in JSON format
6. Share your Google Sheet with the service account email (found in the JSON file)
7. Use the JSON file path with this skill

The service account email will look like: `my-sa-123@my-project.iam.gserviceaccount.com`

## Automatic Dependency Management

This skill automatically handles all Python dependencies using a temporary virtual environment:

- Creates a temporary venv when the skill runs
- Installs required Google libraries (`google-auth-oauthlib`, `google-auth-httplib2`, `google-api-python-client`)
- Executes the script in the isolated environment
- Cleans up the temporary venv after execution

This means you don't need to manually install any dependencies—the skill handles everything automatically.
