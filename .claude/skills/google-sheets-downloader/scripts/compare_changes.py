#!/usr/bin/env python3
"""
Compare current data with previous data and print only rows with changes.
Usage: python compare_changes.py <current_data_json_file> <previous_data_json_file>
"""

import sys
import json
import traceback
from pathlib import Path


def load_json_file(file_path):
    """Load JSON data from file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {file_path}: {str(e)}")
    except Exception as e:
        raise IOError(f"Failed to read {file_path}: {str(e)}")


def compare_rows(current_row, previous_row):
    """
    Compare two row dictionaries.
    Returns True if any field has changed.
    """
    if previous_row is None:
        return True  # New row

    # Compare all fields
    for key in current_row:
        current_val = str(current_row.get(key, "")).strip()
        previous_val = str(previous_row.get(key, "")).strip()
        if current_val != previous_val:
            return True

    return False


def find_changes(current_data, previous_data):
    """
    Find rows that have changed between current and previous data.
    Returns list of tuples: (row_index, current_row, previous_row, changed_fields)
    """
    changes = []

    # Handle case where previous data is empty/None
    if not previous_data:
        return [(i + 1, row, None, list(row.keys())) for i, row in enumerate(current_data)]

    # Compare each current row with corresponding previous row
    for i, current_row in enumerate(current_data):
        previous_row = previous_data[i] if i < len(previous_data) else None

        if compare_rows(current_row, previous_row):
            # Find which specific fields changed
            changed_fields = []
            if previous_row is None:
                changed_fields = list(current_row.keys())
            else:
                for key in current_row:
                    current_val = str(current_row.get(key, "")).strip()
                    previous_val = str(previous_row.get(key, "")).strip()
                    if current_val != previous_val:
                        changed_fields.append(key)

            changes.append((i + 1, current_row, previous_row, changed_fields))

    return changes


def print_changes(changes):
    """Print changed rows in a readable format."""
    if not changes:
        print("\n" + "="*120)
        print("✅ NO CHANGES DETECTED")
        print("="*120)
        print("All rows have the same data as the previous update.")
        return

    print("\n" + "="*120)
    print("📊 ROWS WITH CHANGES")
    print("="*120)
    print(f"Total rows with changes: {len(changes)}\n")

    for row_num, current_row, previous_row, changed_fields in changes:
        print(f"Row {row_num}:")
        print("-" * 120)

        if previous_row is None:
            print("  Status: NEW ROW")
        else:
            print(f"  Status: UPDATED")
            print(f"  Changed fields: {', '.join(changed_fields)}")

        print("\n  Current Values:")
        for field in current_row:
            value = current_row.get(field, "")
            marker = "→" if field in changed_fields else " "
            print(f"    {marker} {field:<15}: {value}")

        if previous_row:
            print("\n  Previous Values:")
            for field in previous_row:
                value = previous_row.get(field, "")
                marker = "←" if field in changed_fields else " "
                print(f"    {marker} {field:<15}: {value}")

        print()


def output_json(changes):
    """Output changed rows as JSON."""
    print("\n" + "="*120)
    print("📋 JSON FORMAT (Changed Rows Only)")
    print("="*120)

    changed_rows = [row for _, row, _, _ in changes]

    if not changed_rows:
        print("[]")
    else:
        print(json.dumps(changed_rows, indent=2))


def main():
    if len(sys.argv) != 3:
        print("Usage: python compare_changes.py <current_data_json> <previous_data_json>")
        print("\nExample:")
        print('  python compare_changes.py "current-data.json" "previous-data.json"')
        print("\nNote: If previous data file doesn't exist, all rows will be marked as changed.")
        sys.exit(1)

    current_file = sys.argv[1]
    previous_file = sys.argv[2]

    try:
        # Load current data (required)
        current_data = load_json_file(current_file)
        if current_data is None:
            raise FileNotFoundError(f"Current data file not found: {current_file}")

        # Load previous data (optional)
        previous_data = load_json_file(previous_file)

        # Find changes
        changes = find_changes(current_data, previous_data)

        # Print results
        print_changes(changes)
        print_json = output_json(changes)

        # Exit with status code based on whether changes were found
        sys.exit(0 if changes else 0)  # Return 0 regardless (no error)

    except FileNotFoundError as e:
        print(f"\n❌ FILE NOT FOUND ERROR", file=sys.stderr)
        print(f"━" * 80, file=sys.stderr)
        print(f"Message: {str(e)}", file=sys.stderr)
        print(f"━" * 80 + "\n", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"\n❌ VALIDATION ERROR", file=sys.stderr)
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
