#!/usr/bin/env python3

import json
import sys


def flatten(data, prefix=""):
    """Recursively flatten nested arrays/objects with dotted key paths."""
    results = []
    if isinstance(data, list):
        for i, item in enumerate(data):
            results.extend(flatten(item, f"{prefix}[{i}]"))
    elif isinstance(data, dict):
        for key, value in data.items():
            new_key = f"{prefix}.{key}" if prefix else key
            results.extend(flatten(value, new_key))
    else:
        results.append((prefix, data))
    return results


def print_structure(data, indent=0):
    """Pretty-print nested structure with indentation."""
    pad = "  " * indent
    if isinstance(data, list):
        print(f"{pad}Array ({len(data)} items)")
        for i, item in enumerate(data):
            print(f"{pad}  [{i}]:")
            print_structure(item, indent + 2)
    elif isinstance(data, dict):
        print(f"{pad}Object ({len(data)} keys)")
        for key, value in data.items():
            print(f"{pad}  {key}:")
            print_structure(value, indent + 2)
    else:
        print(f"{pad}{repr(data)}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 json_parser.py <file.json> [flatten|structure|pretty]")
        print("  flatten   - print all values with their key paths (default)")
        print("  structure - print nested structure overview")
        print("  pretty    - pretty-print the JSON")
        sys.exit(1)

    filepath = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else "flatten"

    with open(filepath) as f:
        data = json.load(f)

    if mode == "flatten":
        for path, value in flatten(data):
            print(f"{path} = {repr(value)}")
    elif mode == "structure":
        print_structure(data)
    elif mode == "pretty":
        print(json.dumps(data, indent=2))
    else:
        print(f"Unknown mode: {mode}")
        sys.exit(1)


if __name__ == "__main__":
    main()
