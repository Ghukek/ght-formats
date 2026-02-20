import subprocess
from pathlib import Path

ROOT = Path("/home/nathan/Documents/GHT/toUSFM")

USFMTC = ROOT / ".usfmtc/venv/bin/usfmconv"

FOLDERS = ["ght_usfm", "ghtg_usfm"]


def run(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


for folder in FOLDERS:

    in_dir = ROOT / folder
    out_dir = Path(folder.replace("_usfm", "_usx"))
    out_dir.mkdir(exist_ok=True)

    files = sorted(in_dir.glob("*.usfm"))

    print(f"\n=== Processing {folder} ({len(files)} files) ===")

    for f in files:

        out_file = out_dir / (f.stem + ".usx")

        print(f"{f.name} → {out_file.name}")

        cmd = [
            str(USFMTC),
            str(f),
            "-o", str(out_file),
            "-F", "usx",
        ]

        code, out, err = run(cmd)

        if code != 0:
            print("FAILED")
            print(err.strip() or out.strip())
        else:
            if not out_file.exists():
                print("⚠ Converted but file missing:", out_file)
            else:
                print("OK")

print("\nDone.")

