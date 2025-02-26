#!/usr/bin/env python
import os
import platform
import subprocess
import sys


def main():
    # 获取要运行的命令和参数
    command = sys.argv[1]
    args = sys.argv[2:]

    # 根据操作系统选择 python 命令
    python_cmd = "python3" if platform.system() != "Windows" else "python"

    # 构建完整命令
    full_command = [python_cmd, "-m", command] + args

    # 执行命令
    result = subprocess.run(full_command)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
