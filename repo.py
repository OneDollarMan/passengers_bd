from datetime import time

from mysql.connector import connect, Error


class Repo:
    ROLE_DRIVER = 1
    ROLE_ENGINEER = 2
    ROLE_ADMINISTRATOR = 3

    def __init__(self, host, user, password, db):
        self.connection = None
        self.cursor = None
        self.connect_to_db(host, user, password, db)
        if self.connection is not None and self.cursor is not None:
            self.select_db(db)
            self.get_tables = lambda: self.raw_query("SHOW TABLES")

            self.get_user = lambda username: self.get_query(
                f"SELECT * FROM user WHERE username='{username}'")
            self.get_all_users = lambda: self.raw_query(
                "SELECT user.id, username, fio, birthday, phone, role.name FROM user JOIN role ON user.role_id=role.id WHERE hidden='0' ORDER BY user.id")
            self.login_user = lambda username, password: self.get_query(
                f"SELECT * FROM user WHERE username='{username}' AND password='{password}' AND hidden='0'")
            self.add_u = lambda params: self.write_query(
                "INSERT INTO user SET fio=%(fio)s, birthday=%(birthday)s, address=%(address)s, phone=%(phone)s, hiring_date=%(hiring_date)s, username=%(username)s, password=%(password)s, role_id=%(role_id)s",
                params)
            self.rm_user = lambda id: self.write_query(f"DELETE FROM user WHERE id='{id}'")
            self.select_users = lambda: self.raw_query("SELECT id, fio FROM user WHERE role_id='1' AND hidden='0'")
            self.hide_user = lambda id: self.write_query(f"UPDATE user SET hidden='1' WHERE id='{id}'")
            self.get_user_by_id = lambda id: self.get_query(f"SELECT user.id, username, fio, birthday, address, phone, role.name FROM user JOIN role ON user.role_id=role.id WHERE hidden='0' AND user.id='{id}'")

            self.get_roles = lambda: self.raw_query("SELECT * from role")

            self.get_buses = lambda: self.raw_query("SELECT * FROM bus WHERE hidden='0'")
            self.add_bus = lambda params: self.write_query(
                "INSERT INTO bus SET brand=%(brand)s, model=%(model)s, plate=%(plate)s, year=%(year)s, mileage=%(mileage)s",
                params)
            self.rm_bus = lambda id: self.write_query(f"DELETE FROM bus WHERE id='{id}'")
            self.select_buses = lambda: self.raw_query("SELECT id, CONCAT(brand, ' ', model, ' ', plate) FROM bus WHERE hidden='0'")
            self.get_bus_by_id = lambda id: self.get_query(f"SELECT * FROM bus WHERE id='{id}'")
            self.hide_bus = lambda id: self.write_query(f"UPDATE bus SET hidden='1' WHERE id='{id}'")

            self.get_stops = lambda: self.raw_query("SELECT * FROM stop")
            self.add_stop = lambda params: self.write_query("INSERT INTO stop SET name=%(name)s, address=%(address)s",
                                                            params)
            self.rm_stop = lambda id: self.write_query(f"DELETE FROM stop WHERE id='{id}'")
            self.select_stops = lambda: self.raw_query("SELECT id, name FROM stop")
            self.select_stops_not_in_route = lambda route_id: self.raw_query(
                f"SELECT id, name FROM stop WHERE id NOT IN (SELECT stop_id FROM route_has_stop WHERE route_id='{route_id}')")
            self.get_stop_by_id = lambda id: self.get_query(f"SELECT * FROM stop WHERE id='{id}'")

            self.get_routes = lambda: self.raw_query("SELECT * FROM route WHERE hidden='0'")
            self.get_route = lambda id: self.get_query(f"SELECT * FROM route WHERE id='{id}'")
            self.add_route = lambda params: self.write_query(
                "INSERT INTO route SET number=%(number)s, length=%(length)s", params)
            self.rm_route = lambda id: self.write_query(f"DELETE FROM route WHERE id='{id}'")
            self.select_routes = lambda: self.raw_query("SELECT id, number FROM route WHERE hidden='0'")
            self.hide_route = lambda id: self.write_query(f"UPDATE route SET hidden='1' WHERE id='{id}'")

            self.add_stop_to_route = lambda stop_id, route_id: self.write_query(
                f"INSERT INTO route_has_stop SET stop_id='{stop_id}', route_id='{route_id}'")
            self.get_stops_of_route = lambda route_id: self.raw_query(
                f"SELECT id, name, address FROM route_has_stop rs JOIN stop ON rs.stop_id=stop.id WHERE route_id='{route_id}'")
            self.rm_stop_from_route = lambda route_id, stop_id: self.write_query(
                f"DELETE FROM route_has_stop WHERE route_id='{route_id}' AND stop_id='{stop_id}'")
            self.remove_route_has_stops = lambda id: self.write_query(
                f"DELETE FROM route_has_stop WHERE route_id='{id}'")
            self.remove_stop_from_route_has_stops = lambda id: self.write_query(
                f"DELETE FROM route_has_stop WHERE stop_id='{id}'")

            self.get_lists = lambda: self.raw_query(
                "SELECT l.id, date, number, CONCAT(brand, ' ', model, ' ', plate) bus, fio, name FROM list l JOIN route r, bus b, user u, status s WHERE l.route_id=r.id AND l.bus_id=b.id AND l.driver_id=u.id AND l.status_id=s.id ORDER BY date")
            self.add_list = lambda params: self.write_query(
                f"INSERT INTO list SET date=%(date)s, route_id=%(route_id)s, bus_id=%(bus_id)s, driver_id=%(driver_id)s, conductor_id=%(conductor_id)s",
                params)
            self.rm_list = lambda id: self.write_query(f"DELETE FROM list WHERE id='{id}'")
            self.get_list = lambda id: self.get_query(
                f"SELECT l.id, date, number, CONCAT(brand, ' ', model, ' ', plate) bus, fio, name, s.id, u.id FROM list l JOIN route r, bus b, user u, status s WHERE l.route_id=r.id AND l.bus_id=b.id AND l.driver_id=u.id AND l.status_id=s.id AND l.id='{id}'")
            self.change_list_status = lambda id, status_id: self.write_query(
                f"UPDATE list SET status_id='{status_id}' WHERE id='{id}'")
            self.remove_route_lists = lambda id: self.write_query(f"DELETE FROM list WHERE route_id='{id}'")
            self.get_lists_of_bus = lambda id: self.raw_query(f"SELECT * FROM list WHERE bus_id='{id}'")
            self.get_lists_of_user = lambda id: self.raw_query(f"SELECT * FROM list WHERE driver_id='{id}'")

            self.get_fligts_of_list = lambda list_id: self.raw_query(f"SELECT * FROM flight WHERE list_id='{list_id}'")
            self.add_flight = lambda start_time, end_time, list_id: self.write_query(
                f"INSERT INTO flight SET start_time='{start_time}', end_time='{end_time}', list_id='{list_id}'")
            self.rm_flight = lambda id: self.write_query(f"DELETE FROM flight WHERE id='{id}'")
            self.remove_list_flights = lambda id: self.write_query(f"DELETE FROM flight WHERE list_id='{id}'")
            self.select_flights_of_list = lambda id: self.raw_query(f"SELECT id, CONCAT(start_time, ' - ', end_time) FROM flight WHERE list_id='{id}'")

            self.select_statuses = lambda: self.raw_query("SELECT id, name FROM status")

            self.get_flights_stat = lambda: self.raw_query(
                "SELECT date, COUNT(*) FROM flight f JOIN list l ON f.list_id=l.id WHERE MONTH(date)=MONTH(now()) GROUP BY YEAR(date), MONTH(date), DAY(date)")
            self.get_driver_stat = lambda: self.raw_query("SELECT u.id, fio, COUNT(*) FROM flight f JOIN list l , user u WHERE f.list_id=l.id AND l.driver_id=u.id AND MONTH(l.date)=MONTH(NOW()) GROUP BY driver_id")
            self.get_bus_stat = lambda: self.raw_query("SELECT b.id, CONCAT(brand, ' ', model, ' ', plate), COUNT(*) FROM flight f JOIN list l , bus b WHERE f.list_id=l.id AND l.bus_id=b.id AND MONTH(l.date)=MONTH(NOW()) GROUP BY bus_id")
            self.get_route_stat = lambda: self.raw_query("SELECT r.id, r.number, COUNT(*) FROM flight f JOIN list l , route r WHERE f.list_id=l.id AND l.route_id=r.id AND MONTH(l.date)=MONTH(NOW()) GROUP BY route_id")

    def connect_to_db(self, host, user, password, db):
        try:
            self.connection = connect(host=host, user=user, password=password)
            self.cursor = self.connection.cursor()
            self.cursor.execute("SHOW DATABASES")
            for res in self.cursor:
                if res[0] == db:
                    self.cursor.fetchall()
                    return
            for line in open('dump.sql'):
                self.cursor.execute(line)
            self.connection.commit()
            print('dump loaded successfully')
        except Error as e:
            print(e)

    def select_db(self, db):
        self.cursor.execute(f"USE {db}")

    def raw_query(self, query, params=None):
        if self.cursor and query:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()

    def write_query(self, query, params=None):
        if self.cursor and query:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.connection.commit()
            return self.cursor.fetchall()

    def get_query(self, query):
        if self.cursor and query:
            self.cursor.execute(query)
            return self.cursor.fetchone()

    def get_one_query(self, query):
        if self.cursor and query:
            self.cursor.execute(query)
            return self.cursor.fetchone()[0]

    def add_user(self, params):
        if not self.get_user(params['username']):
            self.add_u(params)
            return True
        else:
            return False

    def add_bus_check(self, params):
        if not self.get_query(f"SELECT * FROM bus WHERE plate='{params['plate']}'"):
            self.add_bus(params)
            return True
        return False

    def add_stop_check(self, params):
        ...

    def add_route_check(self, params):
        ...

    def add_flight_check(self, start_date, end_date, list_id):
        times = self.raw_query(f"SELECT end_time FROM flight WHERE list_id='{list_id}'")
        for t in times:
            t = str(t[0])
            if (len(t)) < 8: t = '0' + t
            if start_date < time.fromisoformat(t):
                return False
        self.add_flight(start_date, end_date, list_id)
        return True

    def add_list_check(self, params):
        if len(self.raw_query(
                f"SELECT * FROM list WHERE (driver_id='{params['driver_id']}' OR bus_id='{params['bus_id']}') AND date='{params['date']}'")) == 0:
            self.add_list(params)
            return True
        return False

    def get_lists_sorted(self, data):
        q = "SELECT l.id, date, number, CONCAT(brand, ' ', model, ' ', plate) bus, fio, name FROM list l JOIN route r, bus b, user u, status s WHERE l.route_id=r.id AND l.bus_id=b.id AND l.driver_id=u.id AND l.status_id=s.id"
        if data['driver_id']:
            q = q + f" AND l.driver_id='{data['driver_id']}'"
        if data['route_id']:
            q = q + f" AND l.route_id='{data['route_id']}'"
        if data['date1']:
            q = q + f" AND date >= '{data['date1']}'"
        if data['date2']:
            q = q + f" AND date <= '{data['date2']}'"
        q = q + ' ORDER BY date'
        return self.raw_query(q)

    def remove_list(self, id):
        self.remove_list_flights(id)
        self.rm_list(id)

    def remove_route(self, id):
        self.remove_route_lists(id)
        self.remove_route_has_stops(id)
        self.rm_route(id)

    def remove_stop(self, id):
        self.remove_stop_from_route_has_stops(id)
        self.rm_stop(id)

    def remove_bus(self, id):
        lists = self.get_lists_of_bus(id)
        for l in lists:
            self.remove_list(l[0])
        self.rm_bus(id)

    def remove_user(self, id):
        lists = self.get_lists_of_user(id)
        for l in lists:
            self.remove_list(l[0])
        self.rm_user(id)

    def hide_user_with_lists(self, id):
        lists = self.raw_query(f"SELECT id FROM list WHERE driver_id='{id}' AND status_id='1'")
        for l in lists:
            self.remove_list(l[0])
        self.hide_user(id)

    def hide_bus_with_lists(self, id):
        lists = self.raw_query(f"SELECT id FROM list WHERE bus_id='{id}' AND status_id='1'")
        for l in lists:
            self.remove_list(l[0])
        self.hide_bus(id)

    def hide_route_with_lists(self, id):
        lists = self.raw_query(f"SELECT id FROM list WHERE route_id='{id}' AND status_id='1'")
        for l in lists:
            self.remove_list(l[0])
        self.hide_route(id)

    def change_user(self, id, params):
        if params['fio'] != '':
            self.write_query(f"UPDATE user SET fio='{params['fio']}' WHERE id='{id}'")
        if params['birthday'] is not None:
            self.write_query(f"UPDATE user SET birthday='{params['birthday']}' WHERE id='{id}'")
        if params['address'] != '':
            self.write_query(f"UPDATE user SET address='{params['address']}' WHERE id='{id}'")
        if params['phone'] is not None:
            self.write_query(f"UPDATE user SET phone='{params['phone']}' WHERE id='{id}'")

    def change_bus(self, id, params):
        if params['brand'] != '':
            self.write_query(f"UPDATE bus SET brand='{params['brand']}' WHERE id='{id}'")
        if params['model'] != '':
            self.write_query(f"UPDATE bus SET model='{params['model']}' WHERE id='{id}'")
        if params['plate'] != '':
            if not self.get_query(f"SELECT * FROM bus WHERE plate='{params['plate']}'"):
                self.write_query(f"UPDATE bus SET plate='{params['plate']}' WHERE id='{id}'")
            else:
                return False
        if params['year'] is not None:
            self.write_query(f"UPDATE bus SET year='{params['year']}' WHERE id='{id}'")
        if params['mileage'] is not None:
            self.write_query(f"UPDATE bus SET mileage='{params['mileage']}' WHERE id='{id}'")
        return True

    def change_stop(self, id, params):
        if params['name'] != '':
            self.write_query(f"UPDATE stop SET name='{params['name']}' WHERE id='{id}'")
        if params['address'] != '':
            self.write_query(f"UPDATE stop SET address='{params['address']}' WHERE id='{id}'")

    def change_route(self, id, params):
        if params['number'] is not None:
            self.write_query(f"UPDATE route SET number='{params['number']}' WHERE id='{id}'")
        if params['length'] is not None:
            self.write_query(f"UPDATE route SET length='{params['length']}' WHERE id='{id}'")

    def change_flight(self, params):
        if params['start_time'] is not None:
            self.write_query(f"UPDATE flight SET start_time='{params['start_time']}' WHERE id='{params['flight_id']}'")
        if params['end_time'] is not None:
            self.write_query(f"UPDATE flight SET end_time='{params['end_time']}' WHERE id='{params['flight_id']}'")