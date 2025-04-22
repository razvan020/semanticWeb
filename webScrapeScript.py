import os
import requests
import random
from bs4 import BeautifulSoup
from lxml import etree

# ─── CONFIG ─────────────────────────────────────────────────────
XML_FILE      = "books.xml"
XSD_FILENAME  = "books.xsd"
URL           = "https://reedsy.com/discovery/blog/best-books-to-read-in-a-lifetime"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/115.0.0.0 Safari/537.36"
    )
}

theme_options  = ["Science Fiction", "Mystery", "Fantasy", "Romance", "Historical", "Thriller"]
reading_levels = ["Beginner", "Intermediate", "Advanced"]

# ─── 1. Fetch & parse the page ─────────────────────────────────
resp = requests.get(URL, headers=HEADERS)
resp.raise_for_status()
soup = BeautifulSoup(resp.text, "html.parser")

# ─── 2. Pull exactly the on‑screen book titles from the H2s ─────
titles = []
for blot in soup.select("div.book-blot"):
    h2 = blot.find("h2")
    if not h2:
        continue
    text = h2.get_text(strip=True)
    # e.g. "1. 1984 by George Orwell"
    if text and text not in titles:
        titles.append(text)
    if len(titles) >= 20:
        break

if len(titles) < 20:
    raise RuntimeError(f"Only found {len(titles)} book titles; expected 20")

# ─── 3. Load existing XML or create it ──────────────────────────
if os.path.exists(XML_FILE):
    tree = etree.parse(XML_FILE)
    root = tree.getroot()
else:
    nsmap = {"xsi": "http://www.w3.org/2001/XMLSchema-instance"}
    root = etree.Element("library", nsmap=nsmap)
    root.set(
        "{http://www.w3.org/2001/XMLSchema-instance}noNamespaceSchemaLocation",
        XSD_FILENAME
    )
    tree = etree.ElementTree(root)

# ─── 4. Remove old <book> nodes (keep all <user> in place) ─────
for old in root.findall("book"):
    root.remove(old)

# ─── 5. Find where users start so we can insert books before them ─
users = root.findall("user")
insert_idx = root.index(users[0]) if users else len(root)

# ─── 6. Insert the 20 new <book> entries ───────────────────────
for title in titles:
    book = etree.Element("book")
    etree.SubElement(book, "title").text = title

    themes_el = etree.SubElement(book, "themes")
    for th in random.sample(theme_options, 2):
        etree.SubElement(themes_el, "theme").text = th

    rl_el = etree.SubElement(book, "readingLevels")
    for lvl in random.sample(reading_levels, k=random.randint(1, 3)):
        etree.SubElement(rl_el, "level").text = lvl

    root.insert(insert_idx, book)
    insert_idx += 1

# ─── 7. Write back to books.xml ────────────────────────────────
tree.write(
    XML_FILE,
    pretty_print=True,
    xml_declaration=True,
    encoding="UTF-8"
)

print(f"✅ {XML_FILE} updated: {len(titles)} exact screen‑titles inserted; users preserved.")
