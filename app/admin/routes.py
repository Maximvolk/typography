from flask import render_template, request, abort, flash
from . import admin
from . import admin_service
from app.common import get_all_books, search_books, get_employee_by_id, update_employee_and_return_updated
from flask_login import current_user
from functools import wraps


def check_employee_position(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401, 'Sign in to your account')

        if current_user.position != 'admin':
            abort(403, 'You do not have access to administrators subsystem')

        return func(*args, **kwargs)

    return inner


@admin.route('/me', methods=['GET', 'POST'])
@check_employee_position
def admin_me():
    admin = get_employee_by_id(current_user.id)

    if admin is None:
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
            return render_template('admin/adminMe.html', employee=admin)

        if new_password != '' or new_password_confirmation != '':
            if new_password != new_password_confirmation:
                flash('Пароли должны совпадать', 'error')
                return render_template('admin/adminMe.html', employee=admin)
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

        result = update_employee_and_return_updated(admin, data, update_password)

        if result[1] == 1:
            flash('Неправильный пароль', 'error')
        elif result[1] == 2:
            flash('Пользователь с указанным номером телефона уже существует', 'error')
        else:
            flash('Данные сохранены', 'success')
            admin = result[0]

    return render_template('admin/adminMe.html', employee=admin)


@admin.route('/books', methods=['GET'])
@check_employee_position
def admin_books():
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

    return render_template('admin/adminFindBook.html', result=books, params=search_params)


@admin.route('/emitAuthToken', methods=['GET', 'POST'])
@check_employee_position
def emit_auth_token():
    if request.method == 'POST':
        position = request.form.get('position')
        phone = request.form.get('phone')

        if position == '' or phone == '':
            flash('Необходимо заполнить все поля', 'error')
            return render_template('admin/emitAuthToken.html')

        if position not in ['admin', 'editor', 'manager', 'orders_manager']:
            flash('Указанной должости не существует', 'error')
            return render_template('admin/emitAuthToken.html')

        auth_token = admin_service.emit_auth_token(position, phone)

        if auth_token == 1:
            flash('Пользователь с таким телефоном уже существует', 'error')
        else:
            return render_template('admin/emitAuthToken.html', auth_token=auth_token)

    return render_template('admin/emitAuthToken.html')


@admin.route('/salesReport', methods=['GET'])
@check_employee_position
def sales_report():
    books = admin_service.get_sales_report()

    return render_template('admin/salesReport.html', books=books)
