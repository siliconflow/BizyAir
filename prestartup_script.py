import os
import subprocess
import sys
from importlib.metadata import distributions

from packaging.requirements import Requirement
from packaging.version import Version


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
