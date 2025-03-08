import importlib.resources
import os
import shutil
import subprocess
import sys
from importlib.metadata import distributions
from pathlib import Path

from packaging.requirements import Requirement
from packaging.version import Version


def sync_bizyui_files():
    import bizyui

    bizyui_js_path: Path = importlib.resources.files(bizyui) / "js"
    print(f"\033[92m[BizyAir]\033[0m UI location: {str(bizyui_js_path)}")

    current_path = Path(__file__).parent.resolve()
    target_js_dir = current_path / "js"
    source_js_dir = bizyui_js_path

    if not target_js_dir.exists():
        print(f"\033[92m[BizyAir]\033[0m copy whole folder: {str(bizyui_js_path)}")
        shutil.copytree(str(source_js_dir), str(target_js_dir))
        return

    for src_file in source_js_dir.glob("**/*"):
        if src_file.is_file():
            rel_path = src_file.relative_to(source_js_dir)
            dest_file = target_js_dir / rel_path

            if not dest_file.exists():
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                print(f"\033[92m[BizyAir]\033[0m copy : {str(src_file)}")
                shutil.copy2(str(src_file), str(dest_file))
                continue

            src_mtime = src_file.stat().st_mtime
            dest_mtime = dest_file.stat().st_mtime
            if src_mtime > dest_mtime:
                print(f"\033[92m[BizyAir]\033[0m copy : {str(src_file)}")
                shutil.copy2(str(src_file), str(dest_file))


def install_dependencies():
    current_path = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(current_path, "requirements.txt")) as f:
        required_packages = [
            line.strip()
            for line in f.readlines()
            if line.strip() and not line.strip().startswith("#")
        ]

    installed_packages = {
        dist.metadata["Name"]: Version(dist.version) for dist in distributions()
    }

    for package in required_packages:
        try:
            requirement = Requirement(package)
            installed_version = installed_packages.get(requirement.name)
            if not installed_version or not requirement.specifier.contains(
                installed_version
            ):
                try:
                    print(f"\033[92m[BizyAir]\033[0m Try to install depency {package}")
                    subprocess.check_call(
                        [sys.executable, "-m", "pip", "install", package]
                    )
                except subprocess.CalledProcessError as e:
                    print(f"\033[91m[BizyAir]\033[0m Failed to install {package}: {e}")
                    continue
        except Exception as e:
            print(
                f"\033[91m[BizyAir]\033[0m Failed to parse requirement {package}: {e}"
            )
            continue


install_dependencies()

sync_bizyui_files()
