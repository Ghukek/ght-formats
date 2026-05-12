A repository serving the GHT in certain standard formats.

Use the GitHub issues tab or contact me directly to request certain formats.

Requires [usfmtc](https://github.com/usfm-bible/usfmtc) to be included in a directory ./.usfmtc

In run.sh, replace "../concordance.db" with the location of your source sqlite file, obtainable from https://github.com/Ghukek/ght-checks/blob/main/concordance.db

Unfortunately, .bbli creation is not automated and will require use of eSword's conversion tool.

For OSIS conversion, use $ python3 -m venv ./.osis and then $ ./.osis/bin/pip install usfm2osis
