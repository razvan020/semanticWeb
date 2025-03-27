from flask import Flask, request, render_template, redirect, url_for, flash
from lxml import etree

app = Flask(__name__)
app.secret_key = "some_secret_key"  # Required for flashing messages

XML_FILE = "books.xml"
XSL_FILE = "books.xsl"

def load_xml():
    return etree.parse(XML_FILE)

def save_xml(tree):
    tree.write(XML_FILE, pretty_print=True, xml_declaration=True, encoding="UTF-8")

@app.route('/')
def index():
    tree = load_xml()
    books = tree.xpath('/library/book')
    return render_template('index.html', books=books)

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        theme1 = request.form.get('theme1', '').strip()
        theme2 = request.form.get('theme2', '').strip()
        level1 = request.form.get('level1', '').strip()
        level2 = request.form.get('level2', '').strip()
        level3 = request.form.get('level3', '').strip()

        # Basic validation
        if not title or not theme1 or not theme2 or not level1 or not level2 or not level3:
            flash("All fields are required for adding a book.", "error")
            return redirect(url_for('add_book'))

        tree = load_xml()
        root = tree.getroot()
        new_book = etree.SubElement(root, "book")
        etree.SubElement(new_book, "title").text = title
        themes_elem = etree.SubElement(new_book, "themes")
        etree.SubElement(themes_elem, "theme").text = theme1
        etree.SubElement(themes_elem, "theme").text = theme2
        rl_elem = etree.SubElement(new_book, "readingLevels")
        etree.SubElement(rl_elem, "level1").text = level1
        etree.SubElement(rl_elem, "level2").text = level2
        etree.SubElement(rl_elem, "level3").text = level3
        save_xml(tree)
        flash("Book added successfully!", "success")
        return redirect(url_for('index'))
    return render_template('add_book.html')

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        surname = request.form.get('surname', '').strip()
        readingLevel = request.form.get('readingLevel', '').strip()
        preferredTheme = request.form.get('preferredTheme', '').strip()

        if not name or not surname or not readingLevel or not preferredTheme:
            flash("All fields are required for adding a user.", "error")
            return redirect(url_for('add_user'))

        tree = load_xml()
        root = tree.getroot()
        new_user = etree.SubElement(root, "user")
        etree.SubElement(new_user, "name").text = name
        etree.SubElement(new_user, "surname").text = surname
        etree.SubElement(new_user, "readingLevel").text = readingLevel
        etree.SubElement(new_user, "preferredTheme").text = preferredTheme
        save_xml(tree)
        flash("User added successfully!", "success")
        return redirect(url_for('index'))
    return render_template('add_user.html')

@app.route('/recommend')
def recommend():
    tree = load_xml()
    # Select the first user from the XML
    users = tree.xpath('/library/user')
    if not users:
        flash("No user available for recommendations.", "error")
        return redirect(url_for('index'))
    user = users[0]
    user_level = user.xpath('readingLevel/text()')[0]
    user_theme = user.xpath('preferredTheme/text()')[0]
    # Recommend by reading level (using level2)
    books_by_level = tree.xpath(f"/library/book[readingLevels/level2='{user_level}']")
    # Recommend by both reading level and theme (note: theme is inside <themes>)
    books_by_level_theme = tree.xpath(f"/library/book[readingLevels/level2='{user_level}' and themes/theme='{user_theme}']")
    return render_template('recommend.html',
                           books_by_level=books_by_level,
                           books_by_level_theme=books_by_level_theme,
                           user_level=user_level,
                           user_theme=user_theme)

@app.route('/book/<title>')
def book_details(title):
    tree = load_xml()
    # Use XPath to find the book by title
    books = tree.xpath("/library/book[title=$t]", t=title)

    if not books:
        flash("Book not found.", "error")
        return redirect(url_for('index'))
    book = books[0]
    return render_template('book_details.html', book=book)

@app.route('/books_by_theme', methods=['GET', 'POST'])
def books_by_theme():
    tree = load_xml()
    # Retrieve all theme texts from books and create a sorted set
    theme_list = sorted(set(tree.xpath("/library/book/themes/theme/text()")))
    if request.method == 'POST':
        selected_theme = request.form.get('theme')
        if not selected_theme:
            flash("Please select a theme.", "error")
            return redirect(url_for('books_by_theme'))
        books = tree.xpath(f"/library/book[themes/theme='{selected_theme}']")
        return render_template('books_by_theme.html', books=books, theme_list=theme_list, selected_theme=selected_theme)
    return render_template('books_by_theme.html', theme_list=theme_list)

@app.route('/transform')
def transform():
    xml_tree = load_xml()
    xslt_tree = etree.parse(XSL_FILE)
    transform = etree.XSLT(xslt_tree)
    # Optionally, if you want to pass a parameter dynamically:
    result_tree = transform(xml_tree, userLevel=etree.XSLT.strparam("Intermediate"))
    return str(result_tree)


if __name__ == '__main__':
    app.run(debug=True)
