---
name: jk-random
description: Generate and display a random number with custom bounds. Use this skill whenever the user asks for a random number, needs to generate random values within a range, or invokes /jk-random. Accepts two optional arguments - lower bound (default 1) and upper bound (default 100).
compatibility: Python 3.6+
---

# jk-random

Generate a random number with customizable bounds and display it to the user.

## What this skill does

This skill generates a random number within a specified range and displays it in a friendly format. By default, it generates a number between 1 and 100, but you can customize both the lower and upper boundaries.

## How to use it

You can invoke this skill in two ways:

### Without arguments (default range 1-100)
Simply invoke the skill with no arguments to get a random number between 1 and 100.

### With arguments
Provide two arguments to customize the range:
- **First argument**: Lower boundary (minimum value, default: 1)
- **Second argument**: Upper boundary (maximum value, default: 100)

The skill will generate a random integer within the specified range (inclusive).

## Output format

```
🎲 Your random number is: [NUMBER]
```

Where `[NUMBER]` is a random integer within the specified range.

## Examples

- No arguments: Returns a number between 1 and 100
- Arguments: `1 50` returns a number between 1 and 50
- Arguments: `10 20` returns a number between 10 and 20
- Arguments: `-10 10` returns a number between -10 and 10

## Implementation

The skill uses a Python script that accepts optional command-line arguments for the lower and upper bounds. This keeps things fast, reliable, and flexible.
