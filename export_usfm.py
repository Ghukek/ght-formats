import sqlite3
import sys
from collections import defaultdict
import os

if len(sys.argv) < 2:
    print("Usage: python export_usfm.py concordance.db")
    sys.exit(1)

DB_PATH = sys.argv[1]

# --- Full canonical book list (ID, Name, order) ---
BOOKS_EN = [
    ("GEN", "Genesis", ""), ("EXO", "Exodus", ""), ("LEV", "Leviticus", ""),
    ("NUM", "Numbers", ""), ("DEU", "Deuteronomy", ""), ("JOS", "Joshua", ""),
    ("JDG", "Judges", ""), ("RUT", "Ruth", ""), ("1SA", "1 Samuel", ""),
    ("2SA", "2 Samuel", ""), ("1KI", "1 Kings", ""), ("2KI", "2 Kings", ""),
    ("1CH", "1 Chronicles", ""), ("2CH", "2 Chronicles", ""), ("EZR", "Ezra", ""),
    ("NEH", "Nehemiah", ""), ("EST", "Esther", ""), ("JOB", "Job", ""),
    ("PSA", "Psalms", ""), ("PRO", "Proverbs", ""), ("ECC", "Ecclesiastes", ""),
    ("SNG", "Song of Solomon", ""), ("ISA", "Isaiah", ""), ("JER", "Jeremiah", ""),
    ("LAM", "Lamentations", ""), ("EZK", "Ezekiel", ""), ("DAN", "Daniel", ""),
    ("HOS", "Hosea", ""), ("JOL", "Joel", ""), ("AMO", "Amos", ""),
    ("OBA", "Obadiah", ""), ("JON", "Jonah", ""), ("MIC", "Micah", ""),
    ("NAM", "Nahum", ""), ("HAB", "Habakkuk", ""), ("ZEP", "Zephaniah", ""),
    ("HAG", "Haggai", ""), ("ZEC", "Zechariah", ""), ("MAL", "Malachi", ""),
    ("MAT", "Matthew", "Good-message according-to Matthew"), ("MRK", "Mark", "Good-message according-to Mark"), ("LUK", "Luke", "Good-message according-to Luke"),
    ("JHN", "John", "Good-message according-to John"), ("ACT", "Acts", "Practices of{the sent-off[one]s}"), ("ROM", "Romans", "Toward Romans"),
    ("1CO", "1 Corinthians", "Toward Corinthians, Alpha"), ("2CO", "2 Corinthians", "Toward Corinthians, Beta"), ("GAL", "Galatians", "Toward Galatians"),
    ("EPH", "Ephesians", "Toward Ephesians"), ("PHP", "Philippians", "Toward Philippians"), ("COL", "Colossians", "Toward Colossians"),
    ("1TH", "1 Thessalonians", "Toward Thessalonians, Alpha"), ("2TH", "2 Thessalonians", "Toward Thessalonians, Beta"), ("1TI", "1 Timothy", "Toward Timothy, Alpha"),
    ("2TI", "2 Timothy", "Toward Timothy, Beta"), ("TIT", "Titus", "Toward Titus"), ("PHM", "Philemon", "Toward Philemon"),
    ("HEB", "Hebrews", "Toward Hebrews"), ("JAS", "James", "[James]"), ("1PE", "1 Peter", "[1 Peter]"),
    ("2PE", "2 Peter", "[2 Peter]"), ("1JN", "1 John", "[1 John]"), ("2JN", "2 John", "[2 John]"),
    ("3JN", "3 John", "[1 John]"), ("JUD", "Jude", "[Jude]"), ("REV", "Revelation", "[Revelation]")
]

# --- Full canonical book list (ID, Name, order) ---
BOOKS_GR = [
    ("GEN", "Genesis", ""), ("EXO", "Exodus", ""), ("LEV", "Leviticus", ""),
    ("NUM", "Numbers", ""), ("DEU", "Deuteronomy", ""), ("JOS", "Joshua", ""),
    ("JDG", "Judges", ""), ("RUT", "Ruth", ""), ("1SA", "1 Samuel", ""),
    ("2SA", "2 Samuel", ""), ("1KI", "1 Kings", ""), ("2KI", "2 Kings", ""),
    ("1CH", "1 Chronicles", ""), ("2CH", "2 Chronicles", ""), ("EZR", "Ezra", ""),
    ("NEH", "Nehemiah", ""), ("EST", "Esther", ""), ("JOB", "Job", ""),
    ("PSA", "Psalms", ""), ("PRO", "Proverbs", ""), ("ECC", "Ecclesiastes", ""),
    ("SNG", "Song of Solomon", ""), ("ISA", "Isaiah", ""), ("JER", "Jeremiah", ""),
    ("LAM", "Lamentations", ""), ("EZK", "Ezekiel", ""), ("DAN", "Daniel", ""),
    ("HOS", "Hosea", ""), ("JOL", "Joel", ""), ("AMO", "Amos", ""),
    ("OBA", "Obadiah", ""), ("JON", "Jonah", ""), ("MIC", "Micah", ""),
    ("NAM", "Nahum", ""), ("HAB", "Habakkuk", ""), ("ZEP", "Zephaniah", ""),
    ("HAG", "Haggai", ""), ("ZEC", "Zechariah", ""), ("MAL", "Malachi", ""),
    ("MAT", "Matthew", "ευαγγελιον κατα ματθαιον"), ("MRK", "Mark", "ευαγγελιον κατα μαρκον"), ("LUK", "Luke", "ευαγγελιον κατα λογκαν"),
    ("JHN", "John", "ευαγγελιον κατα ιωαννην"), ("ACT", "Acts", "πραξεις αποστολων"), ("ROM", "Romans", "προς ρωμαιους"),
    ("1CO", "1 Corinthians", "προς κορινθιους α"), ("2CO", "2 Corinthians", "προς κορινθιους β"), ("GAL", "Galatians", "προς γαλατας"),
    ("EPH", "Ephesians", "προς εφεσιους"), ("PHP", "Philippians", "προς φιλιππησιους"), ("COL", "Colossians", "προς κολοσσαεις"),
    ("1TH", "1 Thessalonians", "προς θεσσαλονικεις α"), ("2TH", "2 Thessalonians", "προς θεσσαλονικεις β"), ("1TI", "1 Timothy", "προς τιμοθεον α"),
    ("2TI", "2 Timothy", "προς τιμοθεον β"), ("TIT", "Titus", "προς τιτον"), ("PHM", "Philemon", "προς φιλημονα"),
    ("HEB", "Hebrews", "προς εβραιους"), ("JAS", "James", "[James]"), ("1PE", "1 Peter", "[1 Peter]"),
    ("2PE", "2 Peter", "[2 Peter]"), ("1JN", "1 John", "[1 John]"), ("2JN", "2 John", "[2 John]"),
    ("3JN", "3 John", "[3 John]"), ("JUD", "Jude", "[Jude]"), ("REV", "Revelation", "[Revelation]")
]

# -------------------------
# UID PARSER
# -------------------------
def parse_uid(uid):
    core = str(uid).split(".")[0].zfill(8)
    book = int(core[:2])
    chapter = int(core[2:5])
    verse = int(core[5:8])
    return book, chapter, verse


# -------------------------
# BOOK CODE MAP (USFM IDs)
# -------------------------
USFM_BOOKS = [
    "GEN","EXO","LEV","NUM","DEU","JOS","JDG","RUT",
    "1SA","2SA","1KI","2KI","1CH","2CH","EZR","NEH",
    "EST","JOB","PSA","PRO","ECC","SNG","ISA","JER",
    "LAM","EZK","DAN","HOS","JOL","AMO","OBA","JON",
    "MIC","NAM","HAB","ZEP","HAG","ZEC","MAL",
    "MAT","MRK","LUK","JHN","ACT","ROM","1CO","2CO",
    "GAL","EPH","PHP","COL","1TH","2TH","1TI","2TI",
    "TIT","PHM","HEB","JAS","1PE","2PE","1JN","2JN",
    "3JN","JUD","REV"
]

def export(conn, filename, text_column, order_column, booklist, abbrev):

    cur = conn.cursor()

    cur.execute(f"""
        SELECT {text_column}, uid, guid
        FROM entries
        WHERE {text_column} IS NOT NULL
        ORDER BY {order_column}
    """)

    books = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    for word, uid, guid in cur:

        # skip empty text
        if not word:
            continue

        word = word.strip()

        # skip blanks / placeholders
        if not word or word == "_":
            continue

        # skip malformed uid rows
        try:
            b, c, v = parse_uid(uid)
        except Exception:
            continue

        # prevent accidental duplicates
        verse_words = books[b][c][v]
        if verse_words and verse_words[-1] == word:
            continue

        verse_words.append(word)

    os.makedirs(filename, exist_ok=True)

    for book_num in sorted(books):

        index_offset = 1

        if book_num > 39:
            book_num += 1
            index_offset += 1

        book_id, book_short, book_name = booklist[book_num - index_offset]
        outname = f"{book_num:02d}{book_id}{abbrev}.usfm"
        path = os.path.join(filename, outname)

        with open(path, "w", encoding="utf-8") as f:

            book_id, book_short, book_name = booklist[book_num - index_offset]

            # Book header block
            f.write(f"\\id {book_id}\n")
            f.write(f"\\usfm 3.0\n")
            f.write(f"\\h {book_name}\n")
            f.write(f"\\toc1 {book_name}\n")
            f.write(f"\\toc2 {book_short}\n")
            f.write(f"\\mt1 {book_name}\n")

            chapters = books[book_num]

            for chapter in sorted(chapters):
                f.write(f"\\c {chapter}\n")

                verses = chapters[chapter]

                for verse in sorted(verses):
                    verse_text = " ".join(verses[verse])
                    f.write(f"\\v {verse} {verse_text}\n")

            f.write("\n")


# -------------------------
# RUN EXPORTS
# -------------------------
conn = sqlite3.connect(DB_PATH)

export(conn, "ght_usfm", "raw", "uid", BOOKS_EN, "GHT")
export(conn, "ghtg_usfm", "greek", "guid", BOOKS_GR, "GHTG")

conn.close()

print("Done.")
