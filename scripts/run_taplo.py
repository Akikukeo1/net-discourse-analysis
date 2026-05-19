from __future__ import annotations

import shutil
import subprocess
import sys


def main() -> int:
    files = [path for path in sys.argv[1:] if path.endswith(".toml")]
    if not files:
        return 0

    taplo_path = shutil.which("taplo")
    if taplo_path is None:
        print("taplo が見つかりません。pre-commit の依存関係を確認してください。", file=sys.stderr)
        return 1

    result = subprocess.run([
        taplo_path,
        "format",
        *files,
    ], check=False)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
