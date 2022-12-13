from datetime import date

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateTimeLocalField, SubmitField, PasswordField, DecimalField, TimeField, \
    DateField, SelectMultipleField
from wtforms.validators import Length, NumberRange, InputRequired, Optional, ValidationError, Regexp

rus_length = Length(min=1, max=45, message='Значение поля должно быть длиной от %(min)d до %(max)d символов')
rus_number_range = NumberRange(min=1, max=99999999999, message='Значение поля должно быть длиной от %(min)d до %(max)d символов')
rus_input_required = InputRequired(message='Заполните поле')
rus_price_range = NumberRange(min=1, max=10000, message='Значение поля должно быть длиной от %(min)d до %(max)d символов')
rus_mileage_range = NumberRange(min=1, max=1000000, message='Значение поля должно быть длиной от %(min)d до %(max)d символов')


def date_check(form, field):
    if field.data < date.today():
        raise ValidationError('Введите не прошедшую дату')


def birthday_check(form, field):
    if field.data > date.fromisoformat('2000-01-01') or field.data < date.fromisoformat('1900-01-01'):
        raise ValidationError('Введите дату рождения от 1900 до 2000 года')


class LoginForm(FlaskForm):
    login = StringField('Логин', [rus_input_required, rus_length])
    password = PasswordField('Пароль', [rus_input_required, rus_length])
    submit = SubmitField('Войти')


class UserForm(FlaskForm):
    username = StringField('Имя пользователя', [rus_input_required, rus_length])
    password = PasswordField('Пароль', [rus_input_required, rus_length])
    fio = StringField('ФИО', [rus_input_required, rus_length])
    birthday = DateField('Дата рождения', [rus_input_required, birthday_check])
    address = StringField('Адрес проживания', [rus_input_required, rus_length])
    phone = DecimalField('Номер телефона', [rus_input_required, rus_number_range])
    role_id = SelectField('Роль', [rus_input_required])
    submit = SubmitField('Добавить')


class ChangeUserForm(FlaskForm):
    fio = StringField('ФИО', [Optional(), rus_length])
    birthday = DateField('Дата рождения', [Optional()])
    address = StringField('Адрес проживания', [Optional(), rus_length])
    phone = DecimalField('Номер телефона', [Optional(), rus_number_range])
    submit = SubmitField('Добавить')


class BusForm(FlaskForm):
    brand = StringField('Производитель', [rus_input_required, rus_length])
    model = StringField('Модель', [rus_input_required, rus_length])
    plate = StringField('Госномер', [rus_input_required, Regexp(regex='^[АВЕКМНОРСТУХ]\d{3}(?<!000)[АВЕКМНОРСТУХ]{2}\d{2,3}$', message='Введите госномер вида А111АА11')])
    year = DecimalField('Год выпуска', [rus_input_required])
    mileage = DecimalField('Пробег', [rus_input_required, rus_mileage_range])
    submit = SubmitField('Добавить')


class ChangeBusForm(FlaskForm):
    brand = StringField('Производитель', [Optional(), rus_length])
    model = StringField('Модель', [Optional(), rus_length])
    plate = StringField('Госномер', [Optional(),Regexp(regex='^[АВЕКМНОРСТУХ]\d{3}(?<!000)[АВЕКМНОРСТУХ]{2}\d{2,3}$',message='Введите госномер вида А111АА11')])
    year = DecimalField('Год выпуска', [Optional()])
    mileage = DecimalField('Пробег', [Optional(), rus_mileage_range])
    submit = SubmitField('Добавить')


class StopForm(FlaskForm):
    name = StringField('Название', [rus_input_required, rus_length])
    address = StringField('Адрес', [rus_input_required, rus_length])
    submit = SubmitField('Добавить')


class ChangeStopForm(FlaskForm):
    name = StringField('Название', [Optional(), rus_length])
    address = StringField('Адрес', [Optional(), rus_length])
    submit = SubmitField('Добавить')


class RouteForm(FlaskForm):
    number = DecimalField('Номер', [rus_input_required, rus_number_range])
    length = DecimalField('Длина маршрута', [rus_input_required, rus_price_range])
    submit = SubmitField('Добавить')


class ChangeRouteForm(FlaskForm):
    number = DecimalField('Номер', [Optional(), rus_number_range])
    length = DecimalField('Длина маршрута', [Optional(), rus_price_range])
    submit2 = SubmitField('Добавить')


class RouteHasStopForm(FlaskForm):
    stop_id = SelectField('Остановка', [rus_input_required])
    submit = SubmitField('Добавить')


class ListForm(FlaskForm):
    date = DateField('Дата выдачи', [rus_input_required, date_check])
    route_id = SelectField('Маршрут', [rus_input_required])
    bus_id = SelectField('Автобус', [rus_input_required])
    driver_id = SelectField('Водитель', [rus_input_required])
    submit = SubmitField('Добавить')


class ListFilterForm(FlaskForm):
    driver_id = SelectField('Выберите водителя', [Optional()])
    route_id = SelectField('Выберите маршрут', [Optional()])
    date1 = DateField('Дата от', validators=[Optional()])
    date2 = DateField('Дата до', validators=[Optional()])
    submit2 = SubmitField('Показать')


class FlightForm(FlaskForm):
    start_time = TimeField('Начало рейса', [rus_input_required])
    end_time = TimeField('Конец рейса', [rus_input_required])
    submit = SubmitField('Добавить')


class ChangeFlightForm(FlaskForm):
    flight_id = SelectField('Выберите рейс', [Optional()])
    start_time = TimeField('Начало рейса', [Optional()])
    end_time = TimeField('Конец рейса', [Optional()])
    submit2 = SubmitField('Добавить')


class StatusForm(FlaskForm):
    status = SelectField('Выберите статус', validators=[rus_input_required])
    submit2 = SubmitField('Изменить')
