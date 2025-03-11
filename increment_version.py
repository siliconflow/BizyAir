import argparse
import os

import semver

parser = argparse.ArgumentParser()
parser.add_argument("--labels", type=str)
args = vars(parser.parse_args())
print(f"args: {args}")

with open(os.path.join("backend", "bizyengine", "version.txt"), "r+") as file:
    current_semver_str = file.read()
    print(f"current ver: {current_semver_str}")
    ver = semver.Version.parse(current_semver_str)
    if "patch" in args["labels"]:
        ver = ver.bump_patch()
    if "minor" in args["labels"]:
        ver = ver.bump_minor()
    if "major" in args["labels"]:
        ver = ver.bump_major()
    print(f"new ver: {ver}")
    file.seek(0)
    file.write(str(ver))
    file.truncate()

    with open(os.path.join("frontend", "version.txt"), "w") as uifile:
        uifile.write(str(ver))
