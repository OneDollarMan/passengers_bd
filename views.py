import hashlib
from datetime import date

from flask import url_for, render_template, request, redirect, send_from_directory, flash, session
from __init__ import app
import forms
from repo import *

repo = Repo(host=app.config['HOST'], user=app.config['USER'], password=app.config['PASSWORD'], db=app.config['DB'], port=app.config['PORT'])


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(error, 'warning')


@app.route("/")
def index():
    if not session.get('loggedin'):
        return redirect(url_for('login'))
    return render_template('index.html', title="Главная")


@app.route("/login", methods=['GET', 'POST'])
def login():
    if session.get('loggedin'):
        return redirect(url_for('index'))
    form = forms.LoginForm()
    if form.validate_on_submit():
        user = repo.login_user(form.login.data, hashlib.md5(form.password.data.encode('utf-8')).hexdigest())
        if user:
            flash('Вы авторизовались!', 'info')
            session['loggedin'] = True
            session['id'] = user[0]
            session['username'] = user[6]
            session['role'] = user[8]
            return redirect(url_for('index'))
        else:
            flash('Неверный логин или пароль!', 'warning')
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('index'))


@app.route("/users", methods=['GET', 'POST'])
def users():
    form = forms.UserForm()
    form.role_id.choices = repo.get_roles()
    if form.validate_on_submit():
        if session.get('role') == repo.ROLE_ADMINISTRATOR:
            data = form.data
            data['hiring_date'] = date.today()
            data['password'] = hashlib.md5(data['password'].encode('utf-8')).hexdigest()
            if not repo.add_user(data):
                flash('Пользователь уже существует', 'warning')
            else:
                app.logger.warning(f'User {form.username.data} with role id {form.role_id.data} was added by {session.get("username")}')
            return redirect(url_for('users'))
    return render_template('users.html', title='Пользователи', us=repo.get_all_users(), form=form)


@app.route("/users/rm/<int:id>")
def rm_user(id):
    if session.get('role') == repo.ROLE_ADMINISTRATOR:
        if id:
            repo.hide_user_with_lists(id)
    return redirect(url_for('users'))


@app.route('/users/<int:id>', methods=['GET', 'POST'])
def user(id):
    if session.get('role') == repo.ROLE_ADMINISTRATOR or id == session.get('id'):
        form = forms.ChangeUserForm()
        if form.validate_on_submit():
            repo.change_user(id, form.data)
            flash('Данные изменены', 'info')
            return redirect(url_for('user', id=id))
        return render_template('user.html', title='Работник', user=repo.get_user_by_id(id), form=form)
    flash('Доступа нет', 'warning')
    return redirect(url_for('users'))


@app.route("/buses", methods=['GET', 'POST'])
def buses():
    form = forms.BusForm()
    if form.validate_on_submit():
        if session.get('role') == repo.ROLE_ADMINISTRATOR:
            if 2000 <= form.year.data <= 2022:
                if not repo.add_bus_check(form.data):
                    flash('Введите уникальный госномер', 'warning')
            else:
                flash('Введите год выпуска от 2000 до 2022', 'warning')
            return redirect(url_for('buses'))
    return render_template('buses.html', title="Автобусы", buses=repo.get_buses(), form=form)


@app.route("/buses/rm/<int:id>")
def rm_buses(id):
    if session.get('role') == repo.ROLE_ADMINISTRATOR:
        if id:
            repo.hide_bus_with_lists(id)
    return redirect(url_for("buses"))


@app.route('/buses/<int:id>', methods=['GET', 'POST'])
def bus(id):
    if session.get('role') == repo.ROLE_ADMINISTRATOR:
        form = forms.ChangeBusForm()
        if form.validate_on_submit():
            if repo.change_bus(id, form.data):
                flash('Данные изменены', 'info')
            else:
                flash('Введите уникальный госномер', 'warning')
            return redirect(url_for('bus', id=id))
        return render_template('bus.html', title='Автобус', bus=repo.get_bus_by_id(id), form=form)
    flash('Доступа нет', 'warning')
    return redirect(url_for('buses'))


@app.route("/stops", methods=['GET', 'POST'])
def stops():
    form = forms.StopForm()
    if form.validate_on_submit():
        if session.get('role') == repo.ROLE_ADMINISTRATOR:
            repo.add_stop(form.data)
            return redirect(url_for('stops'))

    return render_template('stops.html', title="Остановки", stops=repo.get_stops(), form=form)


@app.route('/stops/<int:id>', methods=['GET', 'POST'])
def stop(id):
    if session.get('role') == repo.ROLE_ADMINISTRATOR:
        form = forms.ChangeStopForm()
        if form.validate_on_submit():
            repo.change_stop(id, form.data)
            flash('Данные изменены', 'info')
            return redirect(url_for('stop', id=id))
        return render_template('stop.html', title='Остановка', stop=repo.get_stop_by_id(id), form=form)
    flash('Доступа нет', 'warning')
    return redirect(url_for('stops'))


@app.route("/stops/rm/<int:id>", methods=['GET', 'POST'])
def rm_stop(id):
    if session.get('role') >= repo.ROLE_ADMINISTRATOR:
        if id:
            repo.remove_stop(id)
    return redirect(url_for("stops"))


@app.route("/routes", methods=['GET', 'POST'])
def routes():
    form = forms.RouteForm()
    if form.validate_on_submit():
        if session.get('role') == repo.ROLE_ADMINISTRATOR:
            repo.add_route(form.data)
            app.logger.warning(f'new route was added by {session.get("username")}')
            return redirect(url_for('routes'))

    return render_template('routes.html', title="Маршруты", routes=repo.get_routes(), form=form)


@app.route("/routes/rm/<int:id>")
def rm_route(id):
    if session.get('role') == repo.ROLE_ADMINISTRATOR:
        if id:
            repo.hide_route_with_lists(id)
    return redirect(url_for("routes"))


@app.route('/routes/<int:id>', methods=['GET', 'POST'])
def route(id):
    form = forms.RouteHasStopForm()
    form.stop_id.choices = repo.select_stops_not_in_route(id)
    change_form = forms.ChangeRouteForm()
    if form.validate_on_submit() and session.get('role') == repo.ROLE_ADMINISTRATOR:
        repo.add_stop_to_route(form.stop_id.data, id)
        return redirect(url_for('route', id=id))
    if session.get('role') >= repo.ROLE_DRIVER:
        return render_template('route.html', title='Маршрут', route=repo.get_route(id), stops=repo.get_stops_of_route(id), form=form, change_form=change_form)


@app.route('/routes/<int:id>/change', methods=['POST'])
def route_change(id):
    if session.get('role') == repo.ROLE_ADMINISTRATOR:
        form = forms.ChangeRouteForm()
        if form.validate_on_submit():
            repo.change_route(id, form.data)
            flash('Данные изменены', 'info')
            return redirect(url_for('route', id=id))
    flash('Доступа нет', 'warning')
    return redirect(url_for('routes'))


@app.route('/routes/<int:route_id>/rm/<int:stop_id>')
def rm_stop_from_route(route_id, stop_id):
    repo.rm_stop_from_route(route_id, stop_id)
    return redirect(url_for('route', id=route_id))


@app.route('/lists', methods=['GET', 'POST'])
def lists():
    form = forms.ListForm()
    form.route_id.choices = repo.select_routes()
    form.bus_id.choices = repo.select_buses()
    form.driver_id.choices = repo.select_users()

    filter_form = forms.ListFilterForm()
    filter_form.driver_id.choices = [("", "---")] + repo.select_users()
    filter_form.route_id.choices = [("", "---")] + repo.select_routes()

    if filter_form.validate_on_submit():
        return render_template('lists.html', title="Маршрутные листы", lists=repo.get_lists_sorted(filter_form.data), form=form, filter_form=filter_form)

    return render_template('lists.html', title='Маршрутные листы', lists=repo.get_lists(), form=form, filter_form=filter_form)


@app.route('/lists/add', methods=['POST'])
def add_list():
    form = forms.ListForm()
    form.route_id.choices = repo.select_routes()
    form.bus_id.choices = repo.select_buses()
    form.driver_id.choices = repo.select_users()

    if form.validate_on_submit() and session.get('role') >= repo.ROLE_ENGINEER:
        data = form.data
        data['conductor_id'] = form.data['driver_id']
        if repo.add_list_check(data):
            app.logger.warning(f'new list was added by {session.get("username")}')
        else:
            flash('На это число водитель или автобус заняты', 'warning')
    else:
        flash_errors(form)
    return redirect(url_for('lists'))


@app.route('/lists/<int:id>', methods=['GET', 'POST'])
def lists_id(id):
    list = repo.get_list(id)
    if session.get('id') == list[7] or session.get('role') >= repo.ROLE_ENGINEER:
        flight_form = forms.FlightForm()
        status_form = forms.StatusForm()
        status_form.status.choices = repo.select_statuses()

        change_form = forms.ChangeFlightForm()
        change_form.flight_id.choices = repo.select_flights_of_list(id)

        if status_form.validate_on_submit():
            repo.change_list_status(id, status_form.status.data)
            flash('Статус изменен', 'info')
            return redirect(url_for('lists_id', id=id))
        return render_template('list.html', title='Маршрутный лист', list=list, flights=repo.get_fligts_of_list(id), flight_form=flight_form, status_form=status_form, change_form=change_form)
    else:
        flash('Не ваш маршрутный лист', 'warning')
        return redirect(url_for('lists'))


@app.route('/lists/<int:id>/add', methods=['POST'])
def add_flight(id):
    flight_form = forms.FlightForm()
    if flight_form.validate_on_submit():
        if flight_form.start_time.data < flight_form.end_time.data:
            if not repo.add_flight_check(flight_form.start_time.data, flight_form.end_time.data, id):
                flash('Время начала должно быть больше конца самого позднего рейса', 'warning')
        else:
            flash('Время начала должно быть меньше времени конца', 'warning')
    return redirect(url_for('lists_id', id=id))


@app.route('/lists/<int:id>/change', methods=['POST'])
def flight_change(id):
    form = forms.ChangeFlightForm()
    form.flight_id.choices = repo.select_flights_of_list(id)
    if form.validate_on_submit():
        repo.change_flight(form.data)
        flash('Данные изменены', 'info')
        return redirect(url_for('lists_id', id=id))


@app.route('/lists/<int:id>/rm/<int:flight_id>')
def rm_flight(id, flight_id):
    repo.rm_flight(flight_id)
    return redirect(url_for('lists_id', id=id))


@app.route("/lists/rm/<int:id>")
def rm_list(id):
    if session.get('role') == repo.ROLE_ADMINISTRATOR:
        if id:
            repo.remove_list(id)
    return redirect(url_for("lists"))


@app.route('/flights_stat')
def stat():
    return repo.get_flights_stat()


@app.route('/stat')
def driver_stat():
    return render_template('stat.html', title='Статистика', driver_stat=repo.get_driver_stat(), bus_stat=repo.get_bus_stat(), route_stat=repo.get_route_stat())


@app.route('/robots.txt')
@app.route('/sitemap.xml')
@app.route('/favicon.ico')
@app.route('/style.css')
@app.route('/script.js')
@app.route('/bus.jpg')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404
