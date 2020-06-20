from app.db_context import DbContext


BASE_SEARCH_QUERY = "SELECT * FROM author "


def get_my_books(editor_id, is_main):
    context = DbContext()

    query = "SELECT DISTINCT ON (book.book_id) book.book_id, " \
             "book_title, author_full_name, circulation, release_date, cost_price, author_fee " \
             "FROM book INNER JOIN " \
             "(SELECT author_id, author_book.book_id, author_book.author_fee FROM author_book INNER JOIN " \
             "(SELECT book_id, MAX(author_fee) AS author_fee FROM author_book GROUP BY book_id) t2 " \
             "ON author_book.book_id = t2.book_id AND author_book.author_fee = t2.author_fee) t1 " \
             "ON t1.book_id = book.book_id INNER JOIN " \
             "author ON author.author_id = t1.author_id INNER JOIN " \
             "book_editor ON book_editor.book_id = book.book_id WHERE editor_id = {editor_id} ".format(
                 editor_id=editor_id
             )

    if is_main:
        query += "AND main_editor = true"

    result = context.select(query, ())

    del context
    return result


def get_book_by_id(book_id):
    context = DbContext()
    query = "SELECT * FROM book WHERE book_id = {book_id}".format(book_id=book_id)

    book = context.select(query, ())
    del context

    return book[0]


def get_book_by_title(title):
    context = DbContext()
    query = "SELECT * FROM book WHERE title = {title}".format(title=title)

    book = context.select(query, ())
    del context

    return book[0]


def get_book_authors(book_id):
    context = DbContext()

    query = "SELECT DISTINCT ON (author.author_id) author_full_name, author_fee FROM " \
	    "author INNER JOIN author_book ON author.author_id = author_book.author_id " \
	    "WHERE author.author_id IN (SELECT author_id FROM author_book WHERE book_id = {_book_id})".format(_book_id=book_id)
    authors = context.select(query, ())

    del context
    return authors


def get_book_editors(book_id):
    context = DbContext()

    query = "SELECT DISTINCT ON (employee.employee_id) employee.employee_id, " \
        "employee_full_name, employee_phone_number, main_editor FROM " \
        "employee INNER JOIN book_editor ON employee.employee_id = book_editor.editor_id " \
        "WHERE book_id = {book_id}".format(book_id=book_id)
    result = context.select(query, ())

    del context
    return result


def _check_book_data(book):
    context = DbContext()

    # Check all authors exist
    for i in range(len(book['authors'])):
        query = "SELECT author_id FROM author WHERE author_full_name = %s"
        result = context.select(query, [book['authors'][i]['author_name']])
        if len(result) == 0:
            return book, 2
        else:
            book['authors'][i]['author_id'] = result[0][0]

    # Check book with same title does not exist
    query = "SELECT book_id FROM book WHERE book_title = %s"
    if len(context.select(query, [book['title']])) > 0:
        return book, 1

    del context
    return book, 0


def add_book(book):
    context = DbContext()

    book, check_data_status = _check_book_data(book)

    if check_data_status != 0:
        return None, check_data_status

    # Save book
    query = "INSERT INTO book VALUES (DEFAULT, %s, %s, %s, %s)"
    context.update(query, [book['title'], book['circulation'], book['release_date'], book['cost_price']])
    book_id = context.select("SELECT book_id FROM book WHERE book_title = %s", [book['title']])[0][0]

    # Save book -> authors relation
    for author in book['authors']:
        context.update(
            "INSERT INTO author_book VALUES (%s, %s, %s)",
            [author['author_id'], book_id, author['author_fee']]
        )

    del context
    return book_id, 0


def update_book_and_return_updated(book):
    context = DbContext()

    # Check all authors exist
    for i in range(len(book['authors'])):
        query = "SELECT author_id FROM author WHERE author_full_name = %s"
        result = context.select(query, [book['authors'][i]['author_name']])
        if len(result) == 0:
            return book, 1
        else:
            book['authors'][i]['author_id'] = result[0][0]

    # Delete old book -> authors relation and add new
    query = "DELETE FROM author_book WHERE book_id = {book_id}".format(book_id=book['book_id'])
    context.update(query, ())

    for author in book['authors']:
        context.update(
            "INSERT INTO author_book VALUES (%s, %s, %s)",
            [author['author_id'], book['book_id'], author['author_fee']]
        )

    # Update book data
    query = "UPDATE book SET circulation = {circ}, release_date = %s, cost_price = {cp}".format(
        circ=book['circulation'], cp=book['cost_price'])
    context.update(query, [book['release_date']])

    query = "SELECT * FROM book WHERE book_id = {book_id}".format(book_id=book['book_id'])
    updated = context.select(query, ())

    del context
    return updated[0], 0


def delete_book(book_id):
    context = DbContext()

    query = "DELETE FROM book WHERE book_id = {book_id}".format(book_id=book_id)
    context.update(query, ())

    del context


def attach_editor_to_book(user_id, book_id, is_main=False):
    context = DbContext()

    query = "INSERT INTO book_editor VALUES ({user_id}, {book_id}, %s)".format(
        user_id=user_id, book_id=book_id)
    context.update(query, [is_main])

    del context


def get_all_authors():
    context = DbContext()

    result = context.select(BASE_SEARCH_QUERY, ())
    del context

    return result


def search_authors(fullName):
    context = DbContext()
    query = BASE_SEARCH_QUERY + "WHERE "
    params = []

    if fullName is not None:
        query += "author_full_name LIKE %s AND "
        params.append("%" + fullName + "%")

    query += "true = true;"
    result = context.select(query, params)
    del context

    return result


def add_author(author):
    context = DbContext()

    result = context.select("SELECT author_id FROM author WHERE author_full_name = %s",
                            [author['author_full_name']])

    if len(result) == 0:
        context.update("INSERT INTO author VALUES (DEFAULT, %s, %s, %s, %s, %s)",
                       [author['author_full_name'], author['author_itn'], author['author_passport'],
                        author['author_address'], author['author_phone_number']])
        author_id = int(context.select("SELECT author_id FROM author WHERE author_full_name = %s",
                                       [author['author_full_name']])[0][0])
    else:
        author_id = 0

    del context

    return author_id


def update_author_and_return_updated(author_id, author):
    context = DbContext()

    query = "UPDATE author " \
            "SET author_full_name = %s, " \
                "author_itn = %s, " \
                "author_passport = %s, " \
                "author_address = %s, " \
                "author_phone_number = %s " \
            "WHERE author_id = {author_id}".format(author_id=author_id)

    context.update(
        query,
        [
            author['author_full_name'],
            author['author_itn'],
            author['author_passport'],
            author['author_address'],
            author['author_phone_number']
        ]
    )

    updated_author = context.select(
        "SELECT * FROM author WHERE author_id = {author_id}".format(author_id=author_id), ())

    del context
    return updated_author[0]


def delete_author(author_id):
    context = DbContext()

    query = "DELETE FROM author WHERE author_id = {author_id}".format(author_id=author_id)
    context.update(query, ())

    del context


def get_author_by_id(author_id):
    context = DbContext()
    query = "SELECT * FROM author WHERE author_id = {author_id}".format(author_id=author_id)

    author = context.select(query, ())
    del context

    if len(author) == 0:
        return None

    return author[0]


# Figure out editors' rights.
# Does he able to become and editor, stop being editor or make someone main editor.
def get_editor_status(editor_id, editors):
    _editor = list(filter(lambda x: x[0] == editor_id, editors))

    # Is editor
    if len(_editor) != 0:
        # Is main editor
        if _editor[0][3]:
            # # Are there many editors
            # if len(editors) > 1:
            #     return 3
            # else:
            #     return 4
            return 3
        else:
            return 2
    else:
        return 1


def change_editor_status(editor_id, book_id, status):
    context = DbContext()

    if status == 1:
        query = f'INSERT INTO book_editor VALUES ({editor_id}, {book_id}, false)'
    elif status == 2:
        query = f'DELETE FROM book_editor WHERE editor_id = {editor_id} AND book_id = {book_id}'
    else:
        raise Exception("Invalid editor status")

    context.update(query, ())
    del context
