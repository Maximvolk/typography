from flask import render_template, request, flash, redirect, abort
from flask_login import current_user
from . import editor
from app.common import get_all_books, search_books, get_employee_by_id, update_employee_and_return_updated
import app.editor.editor_service as editor_service
from functools import wraps


def check_employee_position(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401, 'Sign in to your account')

        if current_user.position != 'editor':
            abort(403, 'You do not have access to editors subsystem')

        return func(*args, **kwargs)

    return inner


@editor.route('/me', methods=['GET', 'POST'])
@check_employee_position
def editor_me():
    editor = get_employee_by_id(current_user.id)

    if editor is None:
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
            return render_template('editor/editorMe.html', employee=editor)

        if new_password != '' or new_password_confirmation != '':
            if new_password != new_password_confirmation:
                flash('Пароли должны совпадать', 'error')
                return render_template('editor/editorMe.html', employee=editor)
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

        result = update_employee_and_return_updated(editor, data, update_password)

        if result[1] == 1:
            flash('Неправильный пароль', 'error')
        elif result[1] == 2:
            flash('Пользователь с указанным номером телефона уже существует', 'error')
        else:
            flash('Данные сохранены', 'success')
            editor = result[0]

    return render_template('editor/editorMe.html', employee=editor)


@editor.route('/me/books', methods=['GET'])
@check_employee_position
def get_my_books():
    if request.args.get('is_main') is None:
        is_main = False
    else:
        is_main = True

    books = editor_service.get_my_books(current_user.id, is_main)

    return render_template('editor/myBooks.html', books=books, is_main=is_main)


@editor.route('/books', methods=['GET'])
@check_employee_position
def get_books():
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

    return render_template('editor/editorFindBook.html', result=books, params=search_params)


@editor.route('/createBook', methods=['GET', 'POST'])
@check_employee_position
def create_book():
    if request.method == 'POST':
        title = request.form.get('title')
        circulation = request.form.get('circulation')
        release_date = request.form.get('release_date')
        cost_price = request.form.get('cost_price')
        authors_names = request.form.getlist('author_name')
        authors_fees = request.form.getlist('author_fee')

        if '' in authors_names or '' in authors_fees or \
                title is None or circulation is None or \
                release_date is None or cost_price is None:
            flash('Необходимо заполнить все поля', 'error')
            return render_template('editor/createBook.html')

        if len(set(authors_names)) < len(authors_names):
            flash('Авторы не могут повторяться', 'error')
            return render_template('editor/createBook.html')

        book = {
            'title': title,
            'circulation': circulation,
            'release_date': release_date,
            'cost_price': cost_price,
            'authors': [
                {'author_name': n, 'author_fee': f}
                for n, f in zip(authors_names, authors_fees)
            ]
        }

        book_id, status = editor_service.add_book(book)

        if status == 0:
            flash('Книга успешно добавлена', 'success')
        elif status == 1:
            flash('Книга с таким названием уже существует', 'error')
        elif status == 2:
            flash('Указанного автора не существует', 'error')

        editor_service.attach_editor_to_book(current_user.id, book_id, is_main=True)

    return render_template('editor/createBook.html')


@editor.route('/book/<int:book_id>', methods=['GET', 'POST'])
@check_employee_position
def update_book(book_id):
    book = editor_service.get_book_by_id(book_id)

    if book is None:
        abort(404, 'Specified book does not exist')

    editors = editor_service.get_book_editors(book_id)
    authors = editor_service.get_book_authors(book[0])
    first_author = authors[0]
    authors.pop(0)

    editor_status = editor_service.get_editor_status(current_user.id, editors)

    if request.method == 'POST':
        if request.form.get('isDelete') == 'true':
            editor_service.delete_book(book_id)
            flash('Книга успешно удалена', 'success')

            return redirect('/editor/books')

        elif request.form.get('changeEditorStatus'):
            editor_service.change_editor_status(
                current_user.id, book_id, int(request.form.get('changeEditorStatus')))
            editors = editor_service.get_book_editors(book_id)
            editor_status = editor_service.get_editor_status(current_user.id, editors)
            flash('Статус успешно изменен', 'success')

            return render_template(
                'editor/editBook.html', book=book, first_author=first_author,
                authors=authors, editors=editors, editor_status=editor_status
            )

        else:
            title = request.form.get('title')
            circulation = request.form.get('circulation')
            release_date = request.form.get('release_date')
            cost_price = request.form.get('cost_price')
            authors_names = request.form.getlist('author_name')
            authors_fees = request.form.getlist('author_fee')

            if '' in authors_names or '' in authors_fees or \
                    circulation == '' or \
                    release_date == '' or cost_price == '':
                flash('Необходимо заполнить все поля', 'error')
                return render_template(
                    'editor/editBook.html', book=book, first_author=first_author,
                    authors=authors, editors=editors, editor_status=editor_status
                )

            if len(set(authors_names)) < len(authors_names):
                flash('Авторы не могут повторяться', 'error')
                return render_template(
                    'editor/editBook.html', book=book, first_author=first_author,
                    authors=authors, editors=editors, editor_status=editor_status
                )

            book_new_data = {
                'book_id': book[0],
                'title': title,
                'circulation': circulation,
                'release_date': release_date,
                'cost_price': cost_price,
                'authors': [
                    {'author_name': n, 'author_fee': f}
                    for n, f in zip(authors_names, authors_fees)
                ]
            }

            result = editor_service.update_book_and_return_updated(book_new_data)

            if result[1] == 0:
                book = result[0]
                authors = editor_service.get_book_authors(book[0])
                first_author = authors[0]
                authors.pop(0)
                flash('Данные книги успешно сохранены', 'success')

            elif result[1] == 1:
                flash('Указанного автора не существует', 'error')

    return render_template(
        'editor/editBook.html', book=book, first_author=first_author,
        authors=authors, editors=editors, editor_status=editor_status
    )


@editor.route('/authors', methods=['GET'])
@check_employee_position
def get_authors():
    search_param = ""

    if request.args.get('fullName') is None:
        books = editor_service.get_all_authors()
    else:
        books = editor_service.search_authors(request.args.get('fullName'))
        search_param = request.args.get('fullName')

    return render_template('editor/editorFindAuthor.html', result=books, param=search_param)


@editor.route('/createAuthor', methods=['GET', 'POST'])
@check_employee_position
def create_author():
    if request.method == 'POST':
        if any([request.form.get(x) == '' for x in
                ('author_full_name', 'author_itn', 'author_passport', 'author_address', 'author_phone_number')]):
            flash('Необходимо заполнить все поля', 'error')

            return render_template('editor/createAuthor.html')

        author = {
            'author_full_name': request.form.get('author_full_name'),
            'author_itn': request.form.get('author_itn'),
            'author_passport': request.form.get('author_passport'),
            'author_address': request.form.get('author_address'),
            'author_phone_number': request.form.get('author_phone_number')
        }

        author_id = editor_service.add_author(author)

        if author_id == 0:
            flash('Автор уже существует', 'error')
        else:
            flash('Автор успешно добавлен', 'success')

    return render_template('editor/createAuthor.html')


@editor.route('/author/<int:author_id>', methods=['GET', 'POST'])
@check_employee_position
def update_author(author_id):
    author = editor_service.get_author_by_id(author_id)

    if author is None:
        abort(404, 'Specified author does not exist')

    if request.method == 'POST':
        if request.form.get('isDelete') == 'true':
            editor_service.delete_author(author_id)
            flash('Автор успешно удален', 'success')

            return redirect('/editor/authors')

        else:
            if any([request.form.get(x) == '' for x in
                    ('author_full_name', 'author_itn', 'author_passport', 'author_address', 'author_phone_number')]):
                flash('Необходимо заполнить все поля', 'error')

                return render_template('editor/editAuthor.html', author=author)

            author_new_data = {
                'author_full_name': request.form.get('author_full_name'),
                'author_itn': request.form.get('author_itn'),
                'author_passport': request.form.get('author_passport'),
                'author_address': request.form.get('author_address'),
                'author_phone_number': request.form.get('author_phone_number')
            }

            author = editor_service.update_author_and_return_updated(author_id, author_new_data)
            flash('Данные автора успешно сохранены', 'success')

    return render_template('editor/editAuthor.html', author=author)
