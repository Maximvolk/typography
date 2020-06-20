from app.db_context import DbContext
from app.auth.user import User
from app import login
from werkzeug.security import check_password_hash, generate_password_hash


SECRET_KEY = 'you-will-never-guess'


@login.user_loader
def load_user(id):
    context = DbContext()

    query = "SELECT * FROM employee WHERE employee_id = {emp_id}".format(emp_id=id)
    result = context.select(query, ())

    del context

    return User(result[0][0], result[0][9])


def get_user(phone):
    context = DbContext()

    query = "SELECT * FROM employee WHERE employee_phone_number = {emp_phone}".format(emp_phone=phone)
    result = context.select(query, ())

    if len(result) == 0:
        return

    del context
    return result[0]


BASE_SEARCH_QUERY = "SELECT DISTINCT ON (book.book_id) book.book_id, " \
             "book_title, author_full_name, circulation, release_date, cost_price, author_fee " \
             "FROM book INNER JOIN " \
             "(SELECT author_id, author_book.book_id, author_book.author_fee FROM author_book INNER JOIN " \
             "(SELECT book_id, MAX(author_fee) AS author_fee FROM author_book GROUP BY book_id) t2 " \
             "ON author_book.book_id = t2.book_id AND author_book.author_fee = t2.author_fee) t1 " \
             "ON t1.book_id = book.book_id INNER JOIN " \
             "author ON author.author_id = t1.author_id "


def get_all_books():
    context = DbContext()

    result = context.select(BASE_SEARCH_QUERY, ())
    del context

    return result


def search_books(title, author_name):
    context = DbContext()
    query = BASE_SEARCH_QUERY + "WHERE "
    params = []

    if title is not None:
        query += "book_title LIKE %s AND "
        params.append("%" + title + "%")

    if author_name is not None:
        query += "author_full_name LIKE %s AND "
        params.append("%" + author_name + "%")

    query += "true = true;"
    result = context.select(query, params)
    del context

    return result


def get_employee_by_id(employee_id):
    context = DbContext()

    query = "SELECT * FROM employee WHERE employee_id = {employee_id}".format(
        employee_id=employee_id
    )
    result = context.select(query, ())

    if len(result) == 0:
        return None

    del context
    return result[0]


def update_employee_and_return_updated(employee_old, employee_new, update_password):
    context = DbContext()

    # Check password
    if not check_password_hash(employee_old[10], employee_new['employee_password']):
        return employee_old, 1

    # Check employee with specified phone number does not exist
    if int(employee_new['employee_phone_number']) != employee_old[5]:
        query = "SELECT * FROM employee WHERE employee_phone_number = {phone}".format(
            phone=employee_new['employee_phone_number']
        )

        if len(context.select(query, ())) > 0:
            return employee_old, 2

    # Save new data
    query = "UPDATE employee SET " \
        "employee_full_name = %s, " \
        "employee_itn = {itn}, " \
        "employee_passport = {passport}, " \
        "employee_address = %s, " \
        "employee_phone_number = {phone}, " \
        "employee_sex = %s, " \
        "employee_birthdate = %s, " \
        "employee_salary = {salary} " \
        "WHERE employee_id = {emp_id}".format(
            itn=employee_new['employee_itn'],
            passport=employee_new['employee_passport'],
            phone=employee_new['employee_phone_number'],
            salary=employee_new['employee_salary'],
            emp_id=employee_old[0]
        )

    context.update(
        query,
        [
            employee_new['employee_full_name'],
            employee_new['employee_address'],
            employee_new['employee_sex'],
            employee_new['employee_birthdate']
        ]
    )

    # Update password if necessary
    if update_password:
        new_password_hash = generate_password_hash(employee_new['new_password'])

        query = "UPDATE employee SET password_hash = %s WHERE employee_id = {emp_id}".format(
            emp_id=employee_old[0]
        )
        context.update(query, [new_password_hash])

    # Retrieve updated employee
    query = "SELECT * FROM employee WHERE employee_id = {employee_id}".format(
        employee_id=employee_old[0]
    )
    result = context.select(query, ())
    del context

    return result[0], 0
