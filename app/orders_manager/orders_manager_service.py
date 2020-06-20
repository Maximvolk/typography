from app.common import DbContext


BASE_SEARCH_QUERY = "SELECT order_id, customer_full_name, customer_address, receipt_date, completion_date FROM " \
            "customer_order INNER JOIN customer ON customer_order.customer_id = customer.customer_id "


def get_all_orders():
    context = DbContext()

    result = context.select(BASE_SEARCH_QUERY, ())
    del context

    return result


def search_orders(customer_name, receipt_date):
    context = DbContext()
    query = BASE_SEARCH_QUERY + "WHERE "
    params = []

    if customer_name is not None:
        query += "customer_full_name LIKE %s AND "
        params.append("%" + customer_name + "%")

    if receipt_date is not None:
        query += "receipt_date = %s AND "
        params.append(receipt_date)

    query += "true = true;"
    result = context.select(query, params)
    del context

    return result


def get_order_by_id(order_id):
    context = DbContext()

    query = BASE_SEARCH_QUERY + "WHERE order_id = {order_id}".format(order_id=order_id)
    result = context.select(query, ())

    del context
    return result[0]


def get_books_in_order(order_id):
    context = DbContext()

    query = "SELECT DISTINCT ON (book.book_id) " \
        "book.book_title, books_amount, book_price FROM " \
        "order_book INNER JOIN book ON order_book.book_id = book.book_id " \
        "WHERE order_id = {order_id}".format(order_id=order_id)
    result = context.select(query, ())

    del context
    return result


def add_order(order):
    context = DbContext()

    # Check all books exist
    for i in range(len(order['books'])):
        query = "SELECT book_id FROM book WHERE book_title = %s"
        result = context.select(query, [order['books'][i]['title']])

        if len(result) == 0:
            return order, 1
        else:
            order['books'][i]['book_id'] = result[0][0]

    # Get customer id, add if not exists
    query = "SELECT customer_id FROM customer WHERE customer_full_name = %s AND customer_address = %s"
    customer = context.select(query, [order['customer_name'], order['customer_address']])

    if len(customer) > 0:
        customer_id = customer[0][0]
    else:
        query = "INSERT INTO customer VALUES (DEFAULT, %s, %s)"
        context.update(query, [order['customer_name'], order['customer_address']])
        customer_id = context.select("SELECT MAX(customer_id) AS last_customer_id FROM customer", ())[0][0]

    # Save order
    query = "INSERT INTO customer_order VALUES (DEFAULT, {customer_id}, %s, %s)".format(customer_id=customer_id)
    context.update(query, [order['receipt_date'], order['completion_date']])
    order_id = context.select("SELECT MAX(order_id) AS last_order_id FROM customer_order", ())[0][0]

    # Save order -> books relation
    for order in order['books']:
        context.update(
            "INSERT INTO order_book VALUES (%s, %s, %s, %s)",
            [order_id, order['book_id'], order['books_amount'], order['book_price']]
        )

    del context
    return order_id, 0


def delete_order(order_id):
    context = DbContext()

    query = "DELETE FROM customer_order WHERE order_id = {order_id}".format(order_id=order_id)
    context.update(query, ())

    del context


def update_order_and_return_updated(order):
    context = DbContext()

    # Check all books exist
    for i in range(len(order['books'])):
        query = "SELECT book_id FROM book WHERE book_title = %s"
        result = context.select(query, [order['books'][i]['title']])

        if len(result) == 0:
            return order, 1
        else:
            order['books'][i]['book_id'] = result[0][0]

    # Delete old order -> books relation and add new
    query = "DELETE FROM order_book WHERE order_id = {order_id}".format(order_id=order['order_id'])
    context.update(query, ())

    for book in order['books']:
        context.update(
            "INSERT INTO order_book VALUES (%s, %s, %s, %s)",
            [order['order_id'], book['book_id'], book['books_amount'], book['book_price']]
        )

    # Update order data
    query = "UPDATE customer_order SET receipt_date = %s, completion_date = %s WHERE order_id = {order_id}".format(
        order_id=order['order_id'])
    context.update(query, [order['receipt_date'], order['completion_date']])

    query = "SELECT * FROM customer_order WHERE order_id = {order_id}".format(order_id=order['order_id'])
    updated = context.select(query, ())

    del context
    return updated[0], 0
