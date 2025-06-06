import importlib.resources
import os
import re
import shutil
import subprocess
import sys
from html.parser import HTMLParser
from importlib.metadata import distributions
from pathlib import Path
from threading import Thread

from packaging.requirements import Requirement
from packaging.version import Version
from packaging.version import parse as parse_version

current_path = Path(__file__).parent.resolve()
os.environ["BIZYAIR_COMFYUI_PATH"] = str(current_path)


class PackageLinkParser(HTMLParser):
    def __init__(self, package_name):
        super().__init__()
        self.package_name = package_name
        self.versions = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            attrs_dict = dict(attrs)
            href = attrs_dict.get("href", "")
            if self.package_name in href:
                parts = href.split("/")
                for part in parts:
                    if part.startswith(self.package_name + "-") and ".whl" in part:
                        version_part = part[len(self.package_name + "-") :]
                        version = version_part.split(".whl")[0].split("-py3")[0]
                        self.versions.append(parse_version(version))


def parse_max_version(content, package_name):
    parser = PackageLinkParser(package_name)
    parser.feed(content)
    if parser.versions:
        return max(parser.versions)
    return None


def get_pip_mirror_url():
    try:
        pip_config_path = None
        if os.name == "nt":  # windows
            pip_config_path = os.path.join(os.getenv("APPDATA"), "pip", "pip.ini")
        else:  # macOS/Linux
            pip_config_path = os.path.expanduser("~/.pip/pip.conf")
            if not os.path.exists(pip_config_path):
                pip_config_path = os.path.expanduser("~/.config/pip/pip.conf")
            if not os.path.exists(pip_config_path):
                pip_config_path = "/etc/pip.conf"

        mirror_url = None
        if pip_config_path and os.path.exists(pip_config_path):
            with open(pip_config_path, "r") as f:
                for line in f:
                    match = re.search(
                        r"index-url\s*=\s*(https?://[^\s]+)", line, re.IGNORECASE
                    )
                    if match:
                        mirror_url = match.group(1)
                        break

        if mirror_url is None:
            mirror_url = "https://pypi.org/simple"
    except Exception as e:
        print(f"Error happens when get pip mirror url: {str(e)}")
        mirror_url = "https://pypi.org/simple"
        print(f"Use default pip url: {mirror_url}")

    return mirror_url


def get_latest_stable_version_from_pip(pip_url, package_name) -> Version:
    import requests

    pkg_url = f"{pip_url.rstrip('/')}/{package_name}"
    response = requests.get(pkg_url)
    response.raise_for_status()
    html_content = response.text
    max_version = parse_max_version(html_content, package_name)
    return max_version


mirror_pip_url = get_pip_mirror_url()


def sync_bizyui_files():
    import bizyui

    bizyui_js_path: Path = importlib.resources.files(bizyui) / "js"
    print(f"\033[92m[BizyAir]\033[0m UI location: {str(bizyui_js_path)}")

    global current_path
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
        dist.metadata["Name"]: Version(dist.version)
        for dist in distributions()
        if dist.version is not None
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
                    install_comamnd = [
                        sys.executable,
                        "-m",
                        "pip",
                        "install",
                        "-U",
                        package,
                    ]
                    subprocess.check_call(install_comamnd)
                except subprocess.CalledProcessError as e:
                    print(f"\033[91m[BizyAir]\033[0m Failed to install {package}: {e}")
                    continue
        except Exception as e:
            print(
                f"\033[91m[BizyAir]\033[0m Failed to parse requirement {package}: {e}"
            )
            continue


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


def update_bizyengine_bizyui():
    def _update_package_when_needed(package_name):
        try:
            update_command = [
                sys.executable,
                "-m",
                "pip",
                "install",
                "-U",
                package_name,
            ]
            if package_name not in installed_packages:
                print(f"\033[92m[BizyAir]\033[0m Try to install {package_name}")
                subprocess.check_call(update_command)
            else:
                latest_version = get_latest_stable_version_from_pip(
                    mirror_pip_url, package_name
                )
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
                    update_command = [
                        sys.executable,
                        "-m",
                        "pip",
                        "install",
                        "-U",
                        package_name,
                    ]
                    subprocess.check_call(update_command)
        except Exception as e:
            print(
                f"\033[92m[BizyAir]\033[0m Error happens when update {package_name} packages: {str(e)}"
                f"\n{' '*10}Try to update manually: \033[91m{' '.join(update_command)}\033[0m"
            )

    installed_packages = {
        dist.metadata["Name"]: Version(dist.version)
        for dist in distributions()
        if dist.version is not None
    }
    print(
        f"\033[92m[BizyAir]\033[0m Checkout updating, current pip url {mirror_pip_url}"
    )

    _update_package_when_needed("bizyengine")
    _update_package_when_needed("bizyui")


install_dependencies()
SKIP_UPDATE = os.environ.get("BIZYAIR_SKIP_UPDATE", False)
if not SKIP_UPDATE:
    update_bizyengine_bizyui()
    sync_bizyui_files()
else:
    print(
        f"\033[92m[BizyAir]\033[0m BIZYAIR_SKIP_UPDATE set, skip updating automatically."
    )
