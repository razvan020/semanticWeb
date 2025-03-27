import requests
from bs4 import BeautifulSoup
import random
from lxml import etree

# URL to scrape from
url = "https://reedsy.com/discovery/blog/best-books-to-read-in-a-lifetime"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

response = requests.get(url, headers=headers)
if response.status_code != 200:
    print("Failed to retrieve the page, status code:", response.status_code)
    exit()

soup = BeautifulSoup(response.text, 'html.parser')
titles = []
# Try extracting titles from h2 tags
for tag in soup.find_all('h2'):
    text = tag.get_text().strip()
    if text and len(text) > 5:
        titles.append(text)
    if len(titles) >= 20:
        break
# If not enough titles, try h3 tags
if len(titles) < 20:
    for tag in soup.find_all('h3'):
        text = tag.get_text().strip()
        if text and text not in titles:
            titles.append(text)
        if len(titles) >= 20:
            break

if not titles:
    print("No book titles found. Exiting.")
    exit()

# Sample themes and reading levels
theme_options = ["Science Fiction", "Mystery", "Fantasy", "Romance", "Historical", "Thriller"]
reading_levels = ["Beginner", "Intermediate", "Advanced"]

# Create the XML document with an XSD reference
nsmap = {"xsi": "http://www.w3.org/2001/XMLSchema-instance"}
library = etree.Element("library", nsmap=nsmap)
# Reference the XSD file (books.xsd must be provided separately)
library.set("{http://www.w3.org/2001/XMLSchema-instance}noNamespaceSchemaLocation", "books.xsd")

for title in titles[:20]:
    book_elem = etree.SubElement(library, "book")
    title_elem = etree.SubElement(book_elem, "title")
    title_elem.text = title
    # Create <themes> with two <theme> children
    themes_elem = etree.SubElement(book_elem, "themes")
    theme_elem1 = etree.SubElement(themes_elem, "theme")
    theme_elem1.text = random.choice(theme_options)
    theme_elem2 = etree.SubElement(themes_elem, "theme")
    theme_elem2.text = random.choice(theme_options)
    # Create <readingLevels>
    rl_elem = etree.SubElement(book_elem, "readingLevels")
    level1 = etree.SubElement(rl_elem, "level1")
    level1.text = reading_levels[0]
    level2 = etree.SubElement(rl_elem, "level2")
    level2.text = reading_levels[1]
    level3 = etree.SubElement(rl_elem, "level3")
    level3.text = reading_levels[2]

# Add one user
user_elem = etree.SubElement(library, "user")
name_elem = etree.SubElement(user_elem, "name")
name_elem.text = "John"
surname_elem = etree.SubElement(user_elem, "surname")
surname_elem.text = "Doe"
readingLevel_elem = etree.SubElement(user_elem, "readingLevel")
readingLevel_elem.text = "Intermediate"
preferredTheme_elem = etree.SubElement(user_elem, "preferredTheme")
preferredTheme_elem.text = "Mystery"

# Write XML to file
tree = etree.ElementTree(library)
tree.write("books.xml", pretty_print=True, xml_declaration=True, encoding="UTF-8")
print("books.xml generated successfully with {} books and 1 user.".format(len(titles[:20])))
