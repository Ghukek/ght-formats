import subprocess
import pathlib

INPUT_DIR = pathlib.Path("raw_usfm")
OUTPUT_DIR = pathlib.Path("usx")

OUTPUT_DIR.mkdir(exist_ok=True)

for usfm in INPUT_DIR.glob("*.usfm"):
    out = OUTPUT_DIR / (usfm.stem + ".usx")

    cmd = [
        "usfmtc",
        str(usfm),
        str(out)
    ]

    print("Converting:", usfm.name)
    subprocess.run(cmd, check=True)

print("Done.")

