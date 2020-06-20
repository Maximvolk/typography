from flask import render_template, request, abort, flash, redirect
from . import manager
from . import manager_service
from app.common import (
    get_all_books,
    search_books,
    get_employee_by_id,
    update_employee_and_return_updated
)
from flask_login import current_user
from functools import wraps


def check_employee_position(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401, 'Sign in to your account')

        if current_user.position != 'manager':
            abort(403, 'You do not have access to managers subsystem')

        return func(*args, **kwargs)

    return inner


@manager.route('/me', methods=['GET', 'POST'])
@check_employee_position
def manager_me():
    manager = get_employee_by_id(current_user.id)

    if manager is None:
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
            return render_template('manager/managerMe.html', employee=manager)

        if new_password != '' or new_password_confirmation != '':
            if new_password != new_password_confirmation:
                flash('Пароли должны совпадать', 'error')
                return render_template('manager/managerMe.html', employee=manager)
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

        result = update_employee_and_return_updated(manager, data, update_password)

        if result[1] == 1:
            flash('Неправильный пароль', 'error')
        elif result[1] == 2:
            flash('Пользователь с указанным номером телефона уже существует', 'error')
        else:
            flash('Данные сохранены', 'success')
            manager = result[0]

    return render_template('manager/managerMe.html', employee=manager)


@manager.route('/me/contracts', methods=['GET'])
@check_employee_position
def get_my_contracts():
    contracts = manager_service.get_my_contracts(current_user.id)

    return render_template('manager/myContracts.html', contracts=contracts)


@manager.route('/books', methods=['GET'])
@check_employee_position
def manager_books():
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

    return render_template('manager/managerFindBook.html', result=books, params=search_params)


@manager.route('/contracts', methods=['GET'])
@check_employee_position
def manager_contracts():
    search_params = []

    book_title = request.args.get('book_title')
    sign_date = request.args.get('sign_date')

    if book_title is None and sign_date is None:
        contracts = manager_service.get_all_contracts()
    else:
        contracts = manager_service.search_contracts(
            book_title,
            sign_date
        )

    search_params.append(book_title if book_title is not None else "")
    search_params.append(sign_date if sign_date is not None else "")

    return render_template('manager/managerFindContract.html', result=contracts, params=search_params)


@manager.route('/createContract', methods=['GET', 'POST'])
@check_employee_position
def add_contract():
    if request.method == 'POST':
        book_title = request.form.get('book_title')
        sign_date = request.form.get('sign_date')

        if book_title == '' or sign_date == '':
            flash('Необходимо заполнить все поля', 'error')
            return render_template('manager/createContract.html')

        contract = {
            'book_title': book_title,
            'sign_date': sign_date,
        }

        status = manager_service.add_contract(contract, current_user.id)

        if status == 0:
            flash('Контракт успешно добавлен', 'success')
        elif status == 1:
            flash('Контракт на указанную книгу уже существует', 'error')
        elif status == 2:
            flash('Указанной книги не существует', 'error')

    return render_template('manager/createContract.html')


@manager.route('/contracts/<int:contract_id>', methods=['GET', 'POST'])
@check_employee_position
def update_contract(contract_id):
    contract = manager_service.get_contract_by_id(contract_id)
    print(contract)
    if contract is None:
        abort(404, 'Specified contract does not exist')

    if request.method == 'POST':
        if request.form.get('isDelete') == 'true':
            manager_service.delete_contract(contract_id)
            flash('Контракт успешно удален', 'success')

            return redirect('/manager/contracts')

        else:
            if request.form.get('book_title') == '' or request.form.get('sign_date') == '':
                flash('Необходимо заполнить все поля', 'error')

                render_template('manager/editContract.html', contract=contract)

            contract_new_data = {
                'sign_date': request.form.get('sign_date')
            }

            contract = manager_service.update_contract_and_return_updated(contract_id, contract_new_data)
            flash('Данные контракта успешно сохранены', 'success')

    return render_template('manager/editContract.html', contract=contract)
