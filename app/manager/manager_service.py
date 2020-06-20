from app.common import DbContext


BASE_SEARCH_QUERY = "SELECT contract_id, book_title, employee_full_name AS manager_name, sign_date FROM " \
	"contract INNER JOIN employee ON contract.manager_id = employee.employee_id " \
	"INNER JOIN book ON contract.book_id = book.book_id "


def get_my_contracts(manager_id):
    context = DbContext()

    query = BASE_SEARCH_QUERY + "WHERE employee_id = {manager_id}".format(
        manager_id=manager_id
    )
    result = context.select(query, ())

    del context
    return result


def get_contract_by_id(contract_id):
    context = DbContext()

    query = BASE_SEARCH_QUERY + "WHERE contract_id = {contract_id}".format(
        contract_id=contract_id
    )
    result = context.select(query, ())

    del context
    return result[0]


def get_all_contracts():
    context = DbContext()

    result = context.select(BASE_SEARCH_QUERY, ())
    del context

    return result


def search_contracts(book_title, sign_date):
    context = DbContext()
    query = BASE_SEARCH_QUERY + "WHERE "
    params = []

    if book_title is not None:
        query += "book_title LIKE %s AND "
        params.append("%" + book_title + "%")

    if sign_date is not None:
        query += "sign_date = %s AND "
        params.append("%" + sign_date + "%")

    query += "true = true;"
    result = context.select(query, params)
    del context

    return result


def add_contract(contract, manager_id):
    context = DbContext()

    # Check contract for this book doesn't already exist
    query = "SELECT * FROM contract WHERE book_id = (SELECT book_id FROM book WHERE book_title = %s)"
    existing_contract = context.select(query, [contract['book_title']])

    if len(existing_contract) > 0:
        return 1

    # Check specified book exists
    query = "SELECT * FROM book WHERE book_title = %s"
    book = context.select(query, [contract['book_title']])

    if len(book) == 0:
        return 2

    # Save contract
    query = "INSERT INTO contract VALUES (DEFAULT, {book_id}, {manager_id}, %s)".format(
        book_id=book[0][0], manager_id=manager_id
    )
    context.update(query, [contract['sign_date']])

    del context
    return 0


def update_contract_and_return_updated(contract_id, contract):
    context = DbContext()

    query = "UPDATE contract SET sign_date = %s WHERE contract_id = {contract_id}".format(
        contract_id=contract_id
    )
    context.update(query, [contract['sign_date']])

    updated_author = context.select(
        "SELECT * FROM contract WHERE contract_id = {contract_id}".format(contract_id=contract_id), ())

    del context
    return updated_author[0]


def delete_contract(contract_id):
    context = DbContext()

    query = "DELETE FROM contract WHERE contract_id = {contract_id}".format(
        contract_id=contract_id
    )
    context.update(query, ())

    del context
