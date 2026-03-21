import os
import platform
import stat
import subprocess
import sys
import urllib.request
from pathlib import Path

from .conf import WindConfig

GITHUB_REPO = "tailwindlabs/tailwindcss"
RELEASE_URL = f"https://github.com/{GITHUB_REPO}/releases"


def _platform_binary() -> str:
    system = sys.platform
    machine = platform.machine().lower()

    if system == "darwin":
        os_name = "macos"
    elif system == "linux":
        os_name = "linux"
    elif system == "win32":
        os_name = "windows"
    else:
        raise RuntimeError(f"Unsupported platform: {system}")

    if machine in ("arm64", "aarch64"):
        arch = "arm64"
    elif machine in ("x86_64", "amd64"):
        arch = "x64"
    else:
        raise RuntimeError(f"Unsupported architecture: {machine}")

    name = f"tailwindcss-{os_name}-{arch}"
    if os_name == "windows":
        name += ".exe"
    return name


def _resolve_latest_version() -> str:
    import json

    url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())
    return data["tag_name"]


def _download(url: str, dest: Path, stdout_write=None) -> None:
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as resp:
        total = int(resp.headers.get("Content-Length", 0))
        downloaded = 0
        chunk_size = 1024 * 256
        with open(dest, "wb") as f:
            while True:
                chunk = resp.read(chunk_size)
                if not chunk:
                    break
                f.write(chunk)
                downloaded += len(chunk)
                if stdout_write and total:
                    pct = int(downloaded / total * 100)
                    stdout_write(f"\r  downloading... {pct}%")
    if stdout_write:
        stdout_write("\n")


def ensure_cli(config: WindConfig, stdout_write=None) -> Path:
    if config.cli_path:
        p = Path(config.cli_path)
        if p.exists():
            return p
        raise FileNotFoundError(f"CLI not found at {p}")

    binary_name = _platform_binary()
    version = config.cli_version

    if version == "latest":
        cached = list(config.bin_dir.glob(f"tailwindcss-*-{binary_name.split('-', 1)[1]}"))
        if cached:
            return sorted(cached)[-1]
        version = _resolve_latest_version()

    dest = config.bin_dir / f"tailwindcss-{version}-{binary_name.split('-', 1)[1]}"
    if dest.exists():
        return dest

    url = f"{RELEASE_URL}/download/{version}/{binary_name}"
    if stdout_write:
        stdout_write(f"Downloading Tailwind CSS CLI ({version})...\n")

    _download(url, dest, stdout_write)

    if sys.platform != "win32":
        dest.chmod(dest.stat().st_mode | stat.S_IEXEC)

    return dest


def run_build(cli_path: Path, input_css: Path, output_css: Path) -> subprocess.CompletedProcess:
    output_css.parent.mkdir(parents=True, exist_ok=True)
    return subprocess.run(
        [str(cli_path), "--input", str(input_css), "--output", str(output_css), "--minify"],
        check=True,
    )


def run_watch(cli_path: Path, input_css: Path, output_css: Path) -> subprocess.Popen:
    output_css.parent.mkdir(parents=True, exist_ok=True)
    return subprocess.Popen(
        [str(cli_path), "--input", str(input_css), "--output", str(output_css), "--watch"],
    )
