"""Create and update the maitri Hugging Face Space.

Run from the repo root with the .env file present and HF_TOKEN populated.
"""

from __future__ import annotations

import os
import shutil
import sys
import tempfile
from pathlib import Path

import ssl

from dotenv import load_dotenv
from huggingface_hub import HfApi, RepoUrl

# Workaround: the python 3.14 venv on this Mac has a broken default certifi bundle
# that makes httpx fail to build an ssl context. Hugging Face hub also reuses httpx.
# Pin a known working bundle from the system or skip verification when neither is set.
import certifi  # noqa: E402

try:
    ssl.create_default_context(cafile=certifi.where())
except (FileNotFoundError, ssl.SSLError):
    import os as _os
    _os.environ.setdefault("CURL_CA_BUNDLE", "")  # tell requests-style libs to skip
    _os.environ.setdefault("PYTHONHTTPSVERIFY", "0")


SPACE_REPO_ID = "mlvptl/maitri-demo"

INCLUDE_PATTERNS = [
    "app.py",
    "requirements.txt",
    "README.md",
    "src/**",
    "data/facilities/**",
    "data/climate/**",
]

EXCLUDE_PATTERNS = [
    "**/__pycache__/**",
    "**/*.pyc",
    "**/.pytest_cache/**",
    "**/.ruff_cache/**",
    "audit*.sqlite",
    "audit*.jsonl",
    ".env",
    ".env.*",
    ".venv/**",
]


def main() -> int:
    load_dotenv()
    token = os.environ.get("HF_TOKEN", "").strip()
    if not token:
        print("HF_TOKEN missing from env", file=sys.stderr)
        return 1

    # Make sure the underlying httpx client uses certifi explicitly.
    os.environ.setdefault("SSL_CERT_FILE", certifi.where())
    os.environ.setdefault("REQUESTS_CA_BUNDLE", certifi.where())
    api = HfApi(token=token)

    print(f"creating space {SPACE_REPO_ID}")
    url: RepoUrl = api.create_repo(
        repo_id=SPACE_REPO_ID,
        repo_type="space",
        space_sdk="gradio",
        exist_ok=True,
        token=token,
    )
    print(f"space url: {url}")

    print("adding HF_TOKEN secret to the space")
    api.add_space_secret(
        repo_id=SPACE_REPO_ID,
        key="HF_TOKEN",
        value=token,
        token=token,
    )

    repo_root = Path(__file__).resolve().parents[1]
    space_readme_src = repo_root / "space_README.md"
    if not space_readme_src.exists():
        print("space_README.md missing", file=sys.stderr)
        return 2

    with tempfile.TemporaryDirectory() as tmp:
        staging = Path(tmp) / "space"
        staging.mkdir()

        shutil.copy2(repo_root / "app.py", staging / "app.py")
        shutil.copy2(repo_root / "requirements.txt", staging / "requirements.txt")
        shutil.copy2(space_readme_src, staging / "README.md")
        shutil.copytree(repo_root / "src", staging / "src", ignore=shutil.ignore_patterns(
            "__pycache__", "*.pyc", ".pytest_cache", ".ruff_cache",
        ))
        shutil.copytree(
            repo_root / "data" / "facilities",
            staging / "data" / "facilities",
        )
        if (repo_root / "data" / "climate").exists():
            shutil.copytree(
                repo_root / "data" / "climate",
                staging / "data" / "climate",
            )

        print(f"uploading {sum(1 for _ in staging.rglob('*') if _.is_file())} files to the space")
        api.upload_folder(
            folder_path=str(staging),
            repo_id=SPACE_REPO_ID,
            repo_type="space",
            token=token,
            commit_message="deploy maitri seven agent gradio demo",
        )

    print(f"deployed: https://huggingface.co/spaces/{SPACE_REPO_ID}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
