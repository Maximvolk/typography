from app.common import get_user, SECRET_KEY, DbContext
import jwt


def emit_auth_token(position, phone):
    user = get_user(phone)

    if user is not None:
        return 1

    payload = {
        'position': position,
        'phone': phone
    }

    auth_token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')
    return auth_token


def get_sales_report():
    context = DbContext()

    query = "SELECT book_title, amount, revenue FROM " \
                "(SELECT DISTINCT order_book.book_id, amount, book_price*amount AS revenue " \
                    "FROM (SELECT book_id, SUM(books_amount) AS amount FROM order_book GROUP BY book_id) t1 " \
                    "INNER JOIN order_book ON t1.book_id = order_book.book_id) t2 " \
                "INNER JOIN book ON t2.book_id = book.book_id"
    result = context.select(query, ())

    del context
    return result
