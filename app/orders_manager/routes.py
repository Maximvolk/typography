from flask import render_template, request, abort, flash, redirect
from . import orders_manager
from . import orders_manager_service
from app.common import get_all_books, search_books, get_employee_by_id, update_employee_and_return_updated
from flask_login import current_user
from functools import wraps


def check_employee_position(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401, 'Sign in to your account')

        if current_user.position != 'orders_manager':
            abort(403, 'You do not have access to orders managers subsystem')

        return func(*args, **kwargs)

    return inner


@orders_manager.route('/me', methods=['GET', 'POST'])
@check_employee_position
def orders_manager_me():
    orders_manager = get_employee_by_id(current_user.id)

    if orders_manager is None:
        abort(404, 'User not found')

    if request.method == 'POST':
        update_password = False

        full_name = request.form.get('employee_full_name')
        itn = request.form.get('employee_itn')
        passport = request.form.get('employee_passport')
        address = request.form.get('employee_address')
        phone_number = request.form.get('employee_phone_number')
        sex = request.form.get('employee_sex')
        birthdate = request.form.get('employee_birthdate')
        salary = request.form.get('employee_salary')
        password = request.form.get('employee_password')

        new_password = request.form.get('employee_new_password')
        new_password_confirmation = request.form.get('employee_new_password_confirmation')

        if full_name == '' or itn == '' or passport == '' or address == '' or \
                sex == '' or birthdate == '' or salary == '' or password == '' or \
                phone_number == '':
            flash('Необходимо заполнить все поля', 'error')
            return render_template('orders_manager/ordersManagerMe.html', employee=orders_manager)

        if new_password != '' or new_password_confirmation != '':
            if new_password != new_password_confirmation:
                flash('Пароли должны совпадать', 'error')
                return render_template('orders_manager/ordersManagerMe.html', employee=orders_manager)
            else:
                update_password = True

        data = {
            'employee_full_name': full_name,
            'employee_itn': itn,
            'employee_passport': passport,
            'employee_address': address,
            'employee_phone_number': phone_number,
            'employee_sex': 'Мужской' if sex == 'male' else 'Женский',
            'employee_birthdate': birthdate,
            'employee_salary': salary,
            'employee_password': password,
            'new_password': new_password,
        }

        result = update_employee_and_return_updated(orders_manager, data, update_password)

        if result[1] == 1:
            flash('Неправильный пароль', 'error')
        elif result[1] == 2:
            flash('Пользователь с указанным номером телефона уже существует', 'error')
        else:
            flash('Данные сохранены', 'success')
            orders_manager = result[0]

    return render_template('orders_manager/ordersManagerMe.html', employee=orders_manager)


@orders_manager.route('/books', methods=['GET'])
@check_employee_position
def orders_manager_books():
    search_params = []

    if request.args.get('title') is None and request.args.get('author_name') is None:
        books = get_all_books()
    else:
        books = search_books(
            request.args.get('title'),
            request.args.get('author_name')
        )

    search_params.append(request.args.get('title') if request.args.get('title') is not None else "")
    search_params.append(request.args.get('author_name') if request.args.get('author_name') is not None else "")

    return render_template('orders_manager/ordersManagerFindBook.html', result=books, params=search_params)


@orders_manager.route('/orders', methods=['GET'])
@check_employee_position
def get_orders():
    search_params = []

    if request.args.get('customer_name') is None and request.args.get('receipt_date') is None:
        orders = orders_manager_service.get_all_orders()
    else:
        orders = orders_manager_service.search_orders(
            request.args.get('customer_name'),
            request.args.get('receipt_date')
        )

    search_params.append(request.args.get('customer_name') if request.args.get('customer_name') is not None else "")
    search_params.append(request.args.get('receipt_date') if request.args.get('receipt_date') is not None else "")

    return render_template('orders_manager/ordersManagerFindOrder.html', result=orders, params=search_params)


@orders_manager.route('/createOrder', methods=['GET', 'POST'])
@check_employee_position
def create_order():
    if request.method == 'POST':
        customer_name = request.form.get('customer_name')
        customer_address = request.form.get('customer_address')
        receipt_date = request.form.get('receipt_date')
        completion_date = request.form.get('completion_date')
        books_titles = request.form.getlist('title')
        books_amounts = request.form.getlist('books_amount')
        books_prices = request.form.getlist('book_price')

        if '' in books_titles or '' in books_amounts or \
                '' in books_prices or customer_name is None or \
                customer_address is None or receipt_date is None or \
                completion_date is None:
            flash('Необходимо заполнить все поля', 'error')
            return render_template('orders_manager/createOrder.html')

        if len(set(books_titles)) < len(books_titles):
            flash('Книги не могут повторяться', 'error')
            return render_template('orders_manager/createOrder.html')

        order = {
            'customer_name': customer_name,
            'customer_address': customer_address,
            'receipt_date': receipt_date,
            'completion_date': completion_date,
            'books': [
                {'title': t, 'books_amount': a, 'book_price': p}
                for t, a, p in zip(books_titles, books_amounts, books_prices)
            ]
        }

        order_id, status = orders_manager_service.add_order(order)

        if status == 0:
            flash('Заказ успешно добавлен', 'success')
        elif status == 1:
            flash('Указанной книги не существует', 'error')

    return render_template('orders_manager/createOrder.html')


@orders_manager.route('/order/<int:order_id>', methods=['GET', 'POST'])
@check_employee_position
def update_order(order_id):
    order = orders_manager_service.get_order_by_id(order_id)

    if order is None:
        abort(404, 'Specified order does not exist')

    books = orders_manager_service.get_books_in_order(order[0])
    first_book = books[0]
    books.pop(0)

    if request.method == 'POST':
        if request.form.get('isDelete') == 'true':
            orders_manager_service.delete_order(order_id)
            flash('Заказ успешно удален', 'success')

            return redirect('/ordersManager/orders')

        else:
            receipt_date = request.form.get('receipt_date')
            completion_date = request.form.get('completion_date')
            books_titles = request.form.getlist('title')
            books_amounts = request.form.getlist('books_amount')
            books_prices = request.form.getlist('book_price')

            if '' in books_titles or '' in books_amounts or \
                    '' in books_prices or receipt_date == '' or \
                    completion_date == '':
                flash('Необходимо заполнить все поля', 'error')
                return render_template(
                    'orders_manager/editOrder.html', order=order, first_book=first_book, books=books)

            if len(set(books_titles)) < len(books_titles):
                flash('Авторы не могут повторяться', 'error')
                return render_template(
                    'orders_manager/editOrder.html', order=order, first_book=first_book, books=books)

            order_new_data = {
                'order_id': order[0],
                'receipt_date': receipt_date,
                'completion_date': completion_date,
                'books': [
                    {'title': t, 'books_amount': a, 'book_price': p}
                    for t, a, p in zip(books_titles, books_amounts, books_prices)
                ]
            }

            result = orders_manager_service.update_order_and_return_updated(order_new_data)

            if result[1] == 0:
                order = result[0]
                books = orders_manager_service.get_books_in_order(order[0])
                first_book = books[0]
                books.pop(0)
                flash('Данные заказа успешно сохранены', 'success')
            elif result[1] == 1:
                flash('Указанной книги не существует', 'error')

    return render_template(
        'orders_manager/editOrder.html', order=order, first_book=first_book, books=books)

