from flask import Flask, request, render_template, redirect, url_for, flash
from lxml import etree

app = Flask(__name__)
app.secret_key = "some_secret_key"

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
        # 1) Collect inputs
        title  = request.form.get('title', '').strip()
        themes = request.form.getlist('theme')    # exactly two items
        levels = request.form.getlist('levels')   # 1–3 items

        # 2) Server‑side validation
        if not title:
            flash("Title is required.", "error")
            return redirect(url_for('add_book'))

        if len(themes) != 2 or themes[0] == themes[1]:
            flash("Please select two **different** themes.", "error")
            return redirect(url_for('add_book'))

        if len(levels) < 1:
            flash("Please select at least one reading level.", "error")
            return redirect(url_for('add_book'))

        allowed = {"Beginner", "Intermediate", "Advanced"}
        if any(l not in allowed for l in levels):
            flash("Invalid reading level choice.", "error")
            return redirect(url_for('add_book'))

        # 3) Build the <book> element
        tree = load_xml()
        root = tree.getroot()

        new_book = etree.Element("book")
        etree.SubElement(new_book, "title").text = title

        themes_elem = etree.SubElement(new_book, "themes")
        for th in themes:
            etree.SubElement(themes_elem, "theme").text = th

        rl_elem = etree.SubElement(new_book, "readingLevels")
        for lvl in levels:
            etree.SubElement(rl_elem, "level").text = lvl

        # 4) Insert before first <user> (if any), else append
        users = root.findall("user")
        if users:
            idx = root.index(users[0])
            root.insert(idx, new_book)
        else:
            root.append(new_book)

        save_xml(tree)
        flash("Book added successfully!", "success")
        return redirect(url_for('index'))

    # GET → render form
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

@app.route('/recommend', methods=['GET', 'POST'])
def recommend():
    tree = load_xml()
    users = tree.xpath('/library/user')
    if not users:
        flash("No users available for recommendations.", "error")
        return redirect(url_for('index'))

    # Default to first user
    selected_idx = 0
    if request.method == 'POST':
        try:
            selected_idx = int(request.form['user_index'])
            if selected_idx < 0 or selected_idx >= len(users):
                raise IndexError
        except (KeyError, ValueError, IndexError):
            flash("Invalid user selection.", "error")
            return redirect(url_for('recommend'))

    user = users[selected_idx]
    user_level = user.xpath('readingLevel/text()')[0]
    user_theme = user.xpath('preferredTheme/text()')[0]

    # Match any of the three levels
    books_by_level = tree.xpath(
        f"/library/book[readingLevels/* = $lvl]",
        lvl=user_level
    )
    # Match both level & theme
    books_by_level_theme = tree.xpath(
        f"/library/book[readingLevels/* = $lvl and themes/theme = $th]",
        lvl=user_level, th=user_theme
    )

    return render_template(
        'recommend.html',
        users=users,
        selected_idx=selected_idx,
        books_by_level=books_by_level,
        books_by_level_theme=books_by_level_theme,
        user_level=user_level,
        user_theme=user_theme
    )
    
    
@app.route('/book/<title>')
def book_details(title):
    tree = load_xml()
    # find the book by title
    books = tree.xpath("/library/book[title = $t]", t=title)
    if not books:
        flash("Book not found.", "error")
        return redirect(url_for('index'))

    book = books[0]

    # extract the data we need
    book_title = book.findtext('title')
    themes     = book.xpath('themes/theme/text()')               # list of theme strings
    levels     = book.xpath('readingLevels/level/text()')        # list of level strings

    return render_template(
        'book_details.html',
        title=book_title,
        themes=themes,
        levels=levels
    )

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

@app.route('/transform', methods=['GET', 'POST'])
def transform():
    xml_tree = load_xml()
    users = xml_tree.xpath('/library/user')
    if not users:
        flash("No users defined yet.", "error")
        return redirect(url_for('index'))

    if request.method == 'POST':
        # user index from the dropdown
        try:
            idx = int(request.form['user_index'])
            user = users[idx]
        except (KeyError, ValueError, IndexError):
            flash("Invalid user selection.", "error")
            return redirect(url_for('transform'))

        user_level = user.xpath('readingLevel/text()')[0]

        # apply XSL with dynamic userLevel param
        xslt_tree = etree.parse(XSL_FILE)
        transform = etree.XSLT(xslt_tree)
        result = transform(xml_tree,
                           userLevel=etree.XSLT.strparam(user_level))
        # return the HTML produced by XSLT
        return str(result)

    # GET → show a simple user‑picker form
    return render_template('select_user_transform.html', users=users)


if __name__ == '__main__':
    app.run(debug=True)
