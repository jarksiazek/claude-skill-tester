# jk-random Skill Setup Guide

## Overview

The `jk-random` skill has been copied from global scope to project scope and integrated with GitHub Actions. This skill generates random numbers within customizable bounds.

## Project Structure

```
.claude/skills/jk-random/
├── SKILL.md                          # Skill definition
└── scripts/
    └── generate_number.py            # Implementation script
```

## Using the Skill in Claude Code

### Method 1: Direct Skill Invocation
```
/jk-random
```

### Method 2: With Custom Range
```
/jk-random 10 50
```

This generates a random number between 10 and 50.

### Method 3: Command Line
```bash
python .claude/skills/jk-random/scripts/generate_number.py
python .claude/skills/jk-random/scripts/generate_number.py 1 100
python .claude/skills/jk-random/scripts/generate_number.py -50 50
```

## GitHub Actions Integration

The workflow file `.github/workflows/use-jk-random-skill.yml` includes:

### Automatic Triggers
- **On push**: Generates a random number (default 1-100)
- **On pull requests**: Generates a random number
- **Manual trigger**: Allows custom min/max values via workflow dispatch

### Jobs

#### `random-number` Job
- Generates random numbers with different ranges
- Captures output for use in subsequent jobs
- Demonstrates using the skill with default and custom parameters

#### `test-with-random-seed` Job
- Depends on the `random-number` job
- Uses the generated random number as a seed for tests
- Example shows how to use random values for test seeding

## Usage Examples in GitHub Actions

### 1. Run Workflow Manually with Custom Range
```
1. Go to Actions tab
2. Select "Use jk-random Skill"
3. Click "Run workflow"
4. Enter min_value: 5
5. Enter max_value: 50
6. Click "Run workflow"
```

### 2. Use Random Number in Your Job
```yaml
- name: Generate random number
  id: random
  run: |
    python .claude/skills/jk-random/scripts/generate_number.py 1 100
    # Capture the output for use in other steps
    OUTPUT=$(python .claude/skills/jk-random/scripts/generate_number.py 1 100)
    NUMBER=$(echo "$OUTPUT" | grep -oP '\d+(?!.*\d)')
    echo "random_number=$NUMBER" >> $GITHUB_OUTPUT

- name: Use the random number
  run: echo "Random number was: ${{ steps.random.outputs.random_number }}"
```

### 3. Random Test Selection
```yaml
- name: Run random subset of tests
  run: |
    RANDOM_SEED=$(python .claude/skills/jk-random/scripts/generate_number.py 1 999999 | grep -oP '\d+(?!.*\d)')
    pytest --randomly-seed=$RANDOM_SEED
```

## Next Steps

1. **Initialize Git repository** (if not already done):
   ```bash
   cd /Users/jksiazek/workspace/cloud-skill-tester
   git init
   git add .
   git commit -m "Add jk-random skill and GitHub Actions workflow"
   ```

2. **Configure GitHub Actions permissions**:
   - Push this repo to GitHub
   - Go to Settings → Actions → General
   - Ensure "Allow all actions and reusable workflows" is enabled

3. **Customize the workflow** to suit your needs:
   - Add more jobs that depend on the random number
   - Integrate with your testing framework
   - Use random numbers for load balancing, seed selection, etc.

## Troubleshooting

### Python not found
Ensure Python 3.6+ is available in your environment.

### Script not executable
Make the script executable:
```bash
chmod +x .claude/skills/jk-random/scripts/generate_number.py
```

### Import errors
The script only uses Python's built-in `random` and `sys` modules, so no additional dependencies are needed.
