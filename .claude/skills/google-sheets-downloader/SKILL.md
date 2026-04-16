---
name: google-sheets-downloader
description: Download data from a Google Sheet and extract 7 columns (First Name, Last Name, Id, City, Latitude, Longitude, Temperature). Optionally update the Temperature column using OpenWeatherMap API. Use this skill whenever the user needs to fetch data from Google Sheets, wants to read spreadsheet values into JSON, or needs to integrate Google Sheets data into their workflow. Accepts three arguments - the spreadsheet ID, the path to a Google service account JSON file for authentication, and optionally the OpenWeatherMap API key for temperature updates.
compatibility: Python 3.7+
---

# Google Sheets Downloader Skill

This skill downloads data from a Google Sheet and extracts 7 columns (A through G) from the first sheet, returning it as JSON with structured data. Optionally, it can update the Temperature column (G) with live weather data from OpenWeatherMap API.

## What it does

**Download Mode (default):**
- Authenticates with Google Sheets API using a service account
- Fetches the first sheet from a specified Google Sheet
- Extracts all values from columns A through G (First Name, Last Name, Id, City, Latitude, Longitude, Temperature)
- Prints the data in a readable table format to the console with row numbers
- Returns the data as JSON for programmatic use with named fields

**Temperature Update Mode (with OpenWeatherMap API key):**
- Same as above, plus:
- Fetches the current temperature for each city using OpenWeatherMap API
- Updates column G (Temperature) in the spreadsheet with live weather data
- Prints a city-to-temperature mapping for verification
- Errors are handled gracefully (missing cities return "N/A")

## How to use it

The skill requires two arguments and accepts an optional third:

1. **Spreadsheet ID** - The ID of your Google Sheet (found in the URL: `https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit`)
2. **Service Account JSON Path** - Full path to your Google service account JSON file (e.g., `/path/to/service-account.json`)
3. **OpenWeatherMap API Key** (optional) - Your OpenWeatherMap API key to enable temperature updates

### Example usage

**Download mode (no temperature updates):**
```
Download 7 columns from my Google Sheet with ID "1a2b3c4d5e6f" 
using the service account at "/Users/me/credentials/google-key.json"
```

**Temperature update mode:**
```
Download 7 columns and update temperatures from my Google Sheet with ID "1a2b3c4d5e6f" 
using the service account at "/Users/me/credentials/google-key.json" 
and my OpenWeatherMap API key "your-api-key-here"
```

## How it works

**Download mode:**
1. Load the service account credentials from the JSON file
2. Authenticate with Google Sheets API
3. Fetch values from the first sheet
4. Extract columns A through G (First Name, Last Name, Id, City, Latitude, Longitude, Temperature)
5. Return as JSON array with named fields
6. If errors occur, print the error cause clearly

**Temperature update mode (when API key is provided):**
1. Same as above steps 1-3
2. For each data row, read the City name (column D)
3. Call OpenWeatherMap Current Weather API for that city
4. Extract the temperature value in Celsius
5. Update column G (Temperature) in the spreadsheet using batch update
6. Return updated JSON with fresh temperature data
7. Print city-to-temperature mapping for verification

## Output format

### Success - Console Output:
```
========================================================================================================================
📊 DATA FROM GOOGLE SHEET (7 COLUMNS)
========================================================================================================================
Total rows: 4

Row   | First Name      | Last Name       | Id         | City            | Latitude     | Longitude    | Temperature    
------------------------------------------------------------------------------------------------------------------------------
1     | John            | Doe             | 001        | New York        | 40.7128      | -74.0060     | 72.5           
2     | Jane            | Smith           | 002        | Los Angeles     | 34.0522      | -118.2437    | 85.2           
3     | Bob             | Johnson         | 003        | Chicago         | 41.8781      | -87.6298     | 68.1           
4     | Alice           | Williams        | 004        | Houston         | 29.7604      | -95.3698     | 88.7           

========================================================================================================================
📋 JSON FORMAT
========================================================================================================================
[
  {
    "First Name": "John",
    "Last Name": "Doe",
    "Id": "001",
    "City": "New York",
    "Latitude": "40.7128",
    "Longitude": "-74.0060",
    "Temperature": "72.5"
  },
  {
    "First Name": "Jane",
    "Last Name": "Smith",
    "Id": "002",
    "City": "Los Angeles",
    "Latitude": "34.0522",
    "Longitude": "-118.2437",
    "Temperature": "85.2"
  }
]
```

### Error Output Example:
```
❌ PERMISSION DENIED ERROR
════════════════════════════════════════════════════════════════════════════════
Message: Access denied. Is the sheet shared with the service account email from your JSON?

The service account doesn't have access to the spreadsheet.

How to fix:
1. Open /path/to/service-account.json
2. Find the 'client_email' field (looks like: xxx@xxx.iam.gserviceaccount.com)
3. Copy the email address
4. Open your Google Sheet
5. Click 'Share' and paste the email
6. Grant at least 'Viewer' access
7. Try again
════════════════════════════════════════════════════════════════════════════════

Traceback (most recent call last):
  File "download_sheets.py", line ..., in <module>
    ...
```

The error messages include:
- **Clear error type** (e.g., "PERMISSION DENIED ERROR", "FILE NOT FOUND ERROR")
- **Exact error message** from Python
- **Specific diagnostic steps** to fix the issue
- **Full traceback** for technical debugging

## Setup: Getting a service account

To use this skill, you need a Google service account:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Sheets API
4. Go to "Credentials" → "Create Credentials" → "Service Account"
5. Create a key in JSON format
6. Share your Google Sheet with the service account email (found in the JSON file)
7. Grant the service account **Editor** access (needed for temperature updates)
8. Use the JSON file path with this skill

The service account email will look like: `my-sa-123@my-project.iam.gserviceaccount.com`

## Setup: Getting an OpenWeatherMap API key (optional)

To enable temperature updates, you need a free OpenWeatherMap API key:

1. Go to [OpenWeatherMap API](https://openweathermap.org/api)
2. Sign up for a free account
3. Go to your API keys section
4. Copy your default API key
5. Use it as the third argument when running the skill
6. For GitHub Actions, add it as a repository secret named `OPENWEATHERMAP_API_KEY`

The free tier allows up to 1,000 calls/day, which is plenty for daily updates.

## Automatic Dependency Management

This skill automatically handles all Python dependencies using a temporary virtual environment:

- Creates a temporary venv when the skill runs
- Installs required Google libraries (`google-auth-oauthlib`, `google-auth-httplib2`, `google-api-python-client`)
- Executes the script in the isolated environment
- Cleans up the temporary venv after execution

This means you don't need to manually install any dependencies—the skill handles everything automatically.

## Troubleshooting Common Errors

### Permission Denied Error
**Message:** "Access denied. Is the sheet shared with the service account email from your JSON?"

**Solution:**
1. Open your service account JSON file
2. Look for the `client_email` field (e.g., `my-sa@project.iam.gserviceaccount.com`)
3. Go to your Google Sheet
4. Click **Share** and paste the email
5. Grant "Viewer" access (or higher)
6. Retry the skill

### File Not Found Error
**Message:** "Service account file not found at: [path]"

**Solution:**
1. Verify the path to your JSON file is correct
2. Use absolute paths (not relative paths)
3. Check the file actually exists: `ls -la /path/to/file.json`

### Spreadsheet Not Found Error
**Message:** "Spreadsheet not found. Check the spreadsheet ID"

**Solution:**
1. Go to your Google Sheet in a browser
2. Copy the ID from the URL: `https://docs.google.com/spreadsheets/d/{ID}/edit`
3. Ensure you're using the exact ID (no extra characters)

### Invalid JSON Error
**Message:** "Service account file is not valid JSON"

**Solution:**
1. Validate your JSON file at [jsonlint.com](https://jsonlint.com)
2. Or download a fresh key from [Google Cloud Console](https://console.cloud.google.com/)

### API Not Enabled Error
**Message:** "Failed to build Sheets API client" or similar API errors

**Solution:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project
3. Enable the "Google Sheets API"
4. Wait a few minutes for it to activate
5. Retry the skill
