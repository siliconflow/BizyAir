import importlib.resources
import os
import shutil
import subprocess
import sys
from importlib.metadata import distributions
from pathlib import Path
from threading import Thread

from packaging.requirements import Requirement
from packaging.version import Version, parse


def sync_bizyui_files():
    import bizyui

    bizyui_js_path: Path = importlib.resources.files(bizyui) / "js"
    print(f"\033[92m[BizyAir]\033[0m UI location: {str(bizyui_js_path)}")

    current_path = Path(__file__).parent.resolve()
    os.environ["BIZYAIR_COMFYUI_PATH"] = str(current_path)
    target_js_dir = current_path / "js"
    source_js_dir = bizyui_js_path

    if not target_js_dir.exists():
        print(f"\033[92m[BizyAir]\033[0m copy whole folder: {str(bizyui_js_path)}")
        shutil.copytree(
            str(source_js_dir),
            str(target_js_dir),
            ignore=shutil.ignore_patterns("__pycache__"),
        )
        return

    for src_file in source_js_dir.glob("**/*"):
        if "__pycache__" in src_file.parts:
            continue
        if src_file.is_file():
            rel_path = src_file.relative_to(source_js_dir)
            dest_file = target_js_dir / rel_path

            if not dest_file.exists() and not str(dest_file).endswith(".py"):
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                print(f"\033[92m[BizyAir]\033[0m copy : {str(dest_file)}")
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


def get_latest_stable_version(package_name) -> Version:
    import requests

    url = f"https://www.pypi.org/pypi/{package_name}/json"
    # url = f"https://test.pypi.org/pypi/{package_name}/json" # debug env
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    versions = [parse(v) for v in data["releases"].keys()]
    stable_versions = [v for v in versions if not v.is_prerelease]
    if not stable_versions:
        return None
    return max(stable_versions)


def yes_or_no(package_name) -> str:
    import time

    def show_countdown(seconds):
        for i in range(seconds, 0, -1):
            print(
                f"\r\033[92m[BizyAir]\033[0m Update NOW? [y]/n {package_name} in {i} seconds",
                end="",
                flush=True,
            )
            time.sleep(1)

    from inputimeout import TimeoutOccurred, inputimeout

    try:
        timeout = 3
        countdown_thread = Thread(target=show_countdown, args=(timeout,))
        countdown_thread.start()
        answer = inputimeout(prompt="", timeout=timeout)
        countdown_thread.join()
    except TimeoutOccurred:
        answer = "y"
    if answer == "n":
        return False
    return True


def update_bizyair_bizyui():
    def _update_pacakge_when_needed(package_name):
        if package_name not in installed_packages:
            print(f"\033[92m[BizyAir]\033[0m Try to install {package_name}")
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", package_name]
            )
        else:
            latest_version = get_latest_stable_version(package_name)
            current_version = installed_packages.get(package_name)
            print(
                f"\033[92m[BizyAir]\033[0m {package_name} latest={str(latest_version)} vs current={str(current_version)}"
            )
            if latest_version > current_version:
                answer = yes_or_no(package_name)
                if not answer:
                    print(
                        f"\n\033[92m[BizyAir]\033[0m canceled by user, skip updating {package_name}"
                    )
                    return
                print(f"\033[92m[BizyAir]\033[0m UPDATE {package_name} NOW")
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", "--upgrade", package_name]
                )

    try:
        installed_packages = {
            dist.metadata["Name"]: Version(dist.version) for dist in distributions()
        }
        _update_pacakge_when_needed("bizyair")
        _update_pacakge_when_needed("bizyui")
    except Exception as e:
        print(f"Error happens when update bizyair packages: {str(e)}")


install_dependencies()
update_bizyair_bizyui()
sync_bizyui_files()
