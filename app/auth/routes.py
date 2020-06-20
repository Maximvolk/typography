from flask import render_template, request, redirect, flash
from flask_login import logout_user, current_user
from . import auth
from . import auth_service


@auth.route('/', methods=['GET'])
def index():
    if current_user.is_authenticated:
        if current_user.position == 'editor':
            return redirect('/editor/books')
        elif current_user.position == 'manager':
            return redirect('/manager/books')
        elif current_user.position == 'admin':
            return redirect('/admin/books')
        elif current_user.position == 'orders_manager':
            return redirect('/ordersManager/books')

    return redirect('/signIn')


@auth.route('/signIn', methods=['GET', 'POST'])
def sign_in():
    if current_user.is_authenticated:
        return redirect('/' + current_user.position + '/books')

    if request.method == 'POST':
        if request.form.get('isSignUp') == 'true':
            return redirect('/signUp')

        phone = request.form.get('phone')
        password = request.form.get('password')

        if phone == '' or password == '':
            flash('Необходимо заполнить все поля', 'error')
            return render_template('auth/signIn.html')

        user = auth_service.sign_in(phone, password)

        # Errors in specified data
        if isinstance(user, int):
            if user == 1:
                flash('Пользователя с такими данными не существует', 'error')
            elif user == 2:
                flash('Неверный пароль', 'error')

            return render_template('auth/signIn.html')

        # Get home page url depending on employee's position
        return redirect('/' + user.position + '/books') if user.position != 'orders_manager' \
            else redirect('/ordersManager/books')

    return render_template('auth/signIn.html')


@auth.route('/signOut', methods=['GET'])
def sign_out():
    logout_user()
    return redirect('/signIn')


@auth.route('/signUp', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        full_name = request.form.get('employee_full_name')
        itn = request.form.get('employee_itn')
        passport = request.form.get('employee_passport')
        address = request.form.get('employee_address')
        sex = request.form.get('employee_sex')
        birthdate = request.form.get('employee_birthdate')
        salary = request.form.get('employee_salary')
        position = request.form.get('employee_position')
        auth_token = request.form.get('auth_token')
        password = request.form.get('employee_password')
        password_confirmation = request.form.get('employee_password_confirmation')

        if full_name == '' or itn == '' or passport == '' or address == '' or \
                sex == '' or birthdate == '' or salary == '' or position == '' or \
                password == '' or password_confirmation == '' or auth_token == '':
            flash('Необходимо заполнить все поля', 'error')
            return render_template('auth/signUp.html')

        if password != password_confirmation:
            flash('Пароли не совпадают', 'error')
            return render_template('auth/signUp.html')

        data = {
            'employee_full_name': full_name,
            'employee_itn': itn,
            'employee_passport': passport,
            'employee_address': address,
            'employee_sex': 'Мужской' if sex == 'male' else 'Женский',
            'employee_birthdate': birthdate,
            'employee_salary': salary,
            'employee_position': position,
            'auth_token': auth_token,
            'employee_password': password
        }

        status = auth_service.sign_up(data)

        if status == 0:
            flash('Пользователь успешно создан', 'success')
            return redirect('/signIn')
        elif status == 1:
            flash('Пользователь с таким телефоном уже существует', 'error')
        elif status == 2:
            flash('Авторизационный ключ не валиден', 'error')

        return render_template('auth/signUp.html')

    return render_template('/auth/signUp.html')
