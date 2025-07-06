#!/usr/bin/env python3

import sys
import subprocess
import tempfile

def validate_code(input_code: str) -> str:
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w+") as temp_file:
        temp_file.write(input_code)
        temp_path = temp_file.name

    subprocess.run(["black", temp_path], check=False)
    subprocess.run(["isort", temp_path], check=False)

    result = subprocess.run(["flake8", temp_path], capture_output=True, text=True)
    if result.stdout:
        print("Lint warnings:\n" + result.stdout, file=sys.stderr)

    with open(temp_path, "r") as f:
        return f.read()

if __name__ == "__main__":
    input_code = sys.stdin.read()
    cleaned_code = validate_code(input_code)
    print(cleaned_code)
