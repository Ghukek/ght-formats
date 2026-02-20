import requests
from bs4 import BeautifulSoup
import os

URL = "https://www.wiebefamily.org/GHT.htm"
OUTDIR = "ght_usfm"
OUTFILE = "A7INT.usfm"


# -------------------------
# HTML → USFM converter
# -------------------------
def clean_text(s):
    return s.replace("\xa0", " ").strip()


def parse_inline(node):

    if isinstance(node, str):
        return clean_text(node)

    tag = node.name.lower()

    # italics
    if tag in ("i","em"):
        return " \\it " + "".join(parse_inline(c) for c in node.children) + " \\it*"

    # bold
    if tag in ("b","strong"):
        return " \\bd " + "".join(parse_inline(c) for c in node.children) + " \\bd*"

    # links
    if tag == "a":
        href = node.get("href","").strip()
        text = "".join(parse_inline(c) for c in node.children)
        if href:
            return f' \\jmp {text}|link-href="{href}"\\jmp*'
        return text

    # line break
    if tag == "br":
        return "\n"

    # recurse default
    return "".join(parse_inline(c) for c in node.children)


def html_to_usfm(element):

    lines = []
    first_heading = True

    for node in element.descendants:

        if isinstance(node, str):
            continue

        tag = node.name.lower()

        # HEADINGS
        if tag in ("h1","h2","h3","h4"):

            text = clean_text(parse_inline(node))
            if not text:
                continue

            if first_heading:
                lines.append("\\imt " + text)
                first_heading = False
            else:
                lines.append("\\is " + text)

        # PARAGRAPH BLOCKS
        elif tag in ("p","div","section","article"):

            text = clean_text(parse_inline(node))
            if text:
                lines.append("\\ip " + text)

        # LISTS
        elif tag == "li":

            text = clean_text(parse_inline(node))
            if text:
                lines.append("\\ili1 " + text)

        # QUOTES
        elif tag == "blockquote":

            text = clean_text(parse_inline(node))
            if text:
                lines.append("\\iq1 " + text)

    return lines


# -------------------------
# FETCH PAGE
# -------------------------
print("Downloading page...")
resp = requests.get(URL)
resp.encoding = "utf-8"        # set BEFORE .text
html = resp.text
soup = BeautifulSoup(html, "html.parser")

intro_div = soup.find("div", id="Introduction")
if not intro_div:
    raise RuntimeError("Introduction div not found")


# -------------------------
# CONVERT CONTENT
# -------------------------
print("Converting HTML → USFM...")
content = html_to_usfm(intro_div)

# -------------------------
# REMOVE DUPLICATE BAD BLOCK
# -------------------------

START_BAD = "\\ip \\jmp https://www.wiebefamily.org/Greek.htm"
END_BAD = "first the New Testament."

start_i = None
end_i = None

for i, line in enumerate(content):
    if start_i is None and START_BAD in line:
        start_i = i
    if start_i is not None and END_BAD in line:
        end_i = i
        break

if start_i is not None and end_i is not None:
    del content[start_i:end_i+1]

# -------------------------
# BUILD FILE TEXT
# -------------------------
usfm = []
usfm.append("\\id INT")
usfm.append("\\usfm 3.0")
usfm.append("\\ide UTF-8")
usfm.append("")
usfm.extend(content)
usfm.append("")
usfm.append("\\ie")
usfm.append("")


# -------------------------
# WRITE FILE
# -------------------------
os.makedirs(OUTDIR, exist_ok=True)
path = os.path.join(OUTDIR, OUTFILE)

with open(path, "w", encoding="utf-8") as f:
    f.write("\n".join(usfm))

print("Saved:", path)

