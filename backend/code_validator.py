import subprocess
import tempfile
import os
import logging

def validate_and_format_python(code: str) -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as tmp:
        tmp.write(code.encode())
        tmp_path = tmp.name

    try:
        subprocess.run(["black", tmp_path], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.run(["isort", tmp_path], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        with open(tmp_path, "r") as f:
            formatted_code = f.read()
        return formatted_code
    except subprocess.CalledProcessError as e:
        logging.error(f"Validation error: {e.stderr}")
        return code
    finally:
        os.remove(tmp_path)
