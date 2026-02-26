import sqlite3
from collections import defaultdict
import os
from datetime import datetime

def greek_to_rtf(text):
    """
    Converts Greek Unicode text to RTF with CP1253 escapes for eSword.
    Assumes font f1 (TITUS Cyberbit Basic) in RTF.
    """
    rtf = ["\\f1"]  # start with font f1
    for c in text:
        code = ord(c)
        # Greek Unicode block: 0x0370–0x03FF
        if 0x0370 <= code <= 0x03FF:
            # Map Unicode Greek letter to CP1253 byte
            cp1253_byte = c.encode("cp1253")  # returns bytes
            rtf.append("".join(f"\\'{b:02x}" for b in cp1253_byte))
        else:
            # Keep ASCII as-is, escape \ and special RTF chars
            if c in ['\\', '{', '}']:
                rtf.append(f"\\{c}")
            else:
                rtf.append(c)
    return "".join(rtf)

def build_bblx(output_file, source_cursor, id_column, text_column,
               description, abbreviation, language_code, font, comments):
    """
    Creates a Version 4 .bblx Bible module from the specified source columns.
    
    language_code: "el" for Greek, "en" for English, etc.
    """
    # Remove existing file
    if os.path.exists(output_file):
        os.remove(output_file)

    conn = sqlite3.connect(output_file)
    cursor = conn.cursor()

    # Version 4 metadata
    cursor.execute("PRAGMA encoding = 'UTF-8';")
    cursor.execute("PRAGMA user_version = 4;")

    # Create Details table exactly as eSword expects
    cursor.execute("""
    CREATE TABLE Details (
        Description     NVARCHAR(250),
        Abbreviation    NVARCHAR(50),
        Comments        TEXT,
        Version         INT,
        Font            TEXT,
        RightToLeft     BOOL,
        OT              BOOL,
        NT              BOOL,
        Apocrypha       BOOL,
        Strong          BOOL
    )
    """)

    date_str = datetime.now().strftime("%d %b %Y")

    cursor.execute("""
    INSERT INTO Details (
        Description, Abbreviation, Comments,
        Version, Font, RightToLeft,
        OT, NT, Apocrypha, Strong
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        description,
        abbreviation,
        f"{comments}\\par Exported by script on {date_str}",
        1,                  # Version = 4
        font,               # Unicode font
        0,                  # Left-to-right text
        1, 1, 0,            # OT, NT, Apocrypha
        0                   # Strong numbers
    ))

    # Create Bible table
    cursor.execute("""
    CREATE TABLE Bible (
        Book INTEGER,
        Chapter INTEGER,
        Verse INTEGER,
        Scripture TEXT,
        PRIMARY KEY (Book, Chapter, Verse)
    )
    """)
    cursor.execute("CREATE INDEX BookChapterVerseIndex ON Bible (Book, Chapter, Verse)")

    # Group and format verses
    verses = defaultdict(list)
    seen_underscore_words = defaultdict(set)

    query = f"""
        SELECT {id_column}, {text_column}
        FROM entries
        WHERE {id_column} IS NOT NULL AND {text_column} IS NOT NULL
        ORDER BY {id_column}
    """
    source_cursor.execute(query)
    rows = source_cursor.fetchall()

    for identifier, word in rows:
        try:
            id_int = int(float(identifier))
            book = id_int // 1_000_000
            chapter = (id_int % 1_000_000) // 1_000
            verse = id_int % 1_000
            key = (book, chapter, verse)

            # Skip duplicate underscore-compounds
            if "_" in word and word in seen_underscore_words[key]:
                continue
            seen_underscore_words[key].add(word)

            verses[key].append((id_int, word))
        except Exception as e:
            print(f"Skipping {id_column}={identifier} due to error: {e}")

    # Insert verses into Bible table
    for key in sorted(verses.keys()):
        book, chapter, verse = key
        words = sorted(verses[key], key=lambda x: x[0])
        scripture = " ".join(word for _, word in words)

        # Convert to RTF if Greek
        #if language_code.lower() in ("el", "greek"):
        scripture = greek_to_rtf(scripture)

        cursor.execute("""
        INSERT INTO Bible (Book, Chapter, Verse, Scripture)
        VALUES (?, ?, ?, ?)
        """, (book, chapter, verse, scripture))

    conn.commit()
    conn.close()
    print(f"✅ Created: {output_file}")


# --- Run exports ---
source_conn = sqlite3.connect("../concordance.db")
source_cursor = source_conn.cursor()

info = "\\strike\\'a9\\strike0 Dedicated to the Public Domain.\\par Garth's Hyper-literal Translation sets a new bar as \"the only English translation actually achieving, or nearly achieving, 'formal equivalence' (faithful to the lexical/grammatical details of the source language)... It is for serious bible study for those who do not know Greek (yet), or who do know it but are not yet able to easily sight read it in the way they are able to sight read English at a glance... If you want to know what the original says, as close to the original as possible, translating every original word and every original grammatical construct, at the expense of nice English, yet still reasonably understandable in English, then this is the translation for you.\" Note, this translation does not pretend to tell you what the scriptures mean; only what they say. It your responsibility to interpret what is said in its proper context. Refer to the introduction at https://www.wiebefamily.org/GHT.htm for more details about the translation philosophy, formatting choices, textual basis, and translator qualification.\\par The module is maintained by Nathan; contact information is found at https://www.ghukek.com/ght.html. Please direct any module-specific issues (such as discrepancies between the module and the source) to him. Please keep in mind that this module will be updated less frequently than the source. Before contacting Garth with translation concerns, check the source to verify the current reading."

# Greek module
build_bblx(
    output_file="ght-g.bblx",
    source_cursor=source_cursor,
    id_column="guid",
    text_column="greek",
    description="Garth's Hyper-literal Translation, Greek Text",
    abbreviation="GHTg",
    language_code="el",
    font="Greek",
    comments=f"{info}\\par This module is the Greek textual basis for the GHT, compiled by means of back-translation \\'e0 la Scrivener as part of the validation process. It does not perfectly correspond to any published Greek New Testament but every variance from them is supported by significant manuscript evidence."
)

# English module
build_bblx(
    output_file="ght.bblx",
    source_cursor=source_cursor,
    id_column="uid",
    text_column="raw",
    description="Garth's Hyper-literal Translation",
    abbreviation="GHT",
    language_code="en",
    font="English",
    comments=f"{info}\\par This English text of the GHT is retrieved from the original source and has been checked for textual, lexical, and grammatical consistency using a battery of automated tools with manual oversight."
)

source_conn.close()

