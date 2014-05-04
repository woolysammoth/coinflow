import sqlite3


def open():
	return sqlite3.connect('store.dat')


def close(conn):
	conn.commit()
	conn.close()
	return


def gen():
	conn = open()
	c = conn.cursor()

	try:
		c.execute(
			'create table follows (id integer primary key, nick varchar(255), address varchar(35), profile varchar(255));')
	except sqlite3.OperationalError as e:
		print(str(e))
	try:
		c.execute('create table profiles (id integer primary key, nick varchar(255), seed varchar(255));')
	except sqlite3.OperationalError as e:
		print(str(e))
	try:
		c.execute('create table data (name varchar(255), value varchar(255), profile varchar(255));')
	except sqlite3.OperationalError as e:
		print(str(e))
	try:
		c.execute('create table nicks (id integer primary key, nick varchar(255), address varchar(35));')
	except sqlite3.OperationalError as e:
		print(str(e))
	try:
		c.execute('create table settings (name varchar(255), value varchar(255), profile varchar(255));')
	except sqlite3.OperationalError as e:
		print(str(e))

	close(conn)
	return


def getData(self, name, default):
	"""
		return a data value from the database
		return default if no value exists
	"""
	conn = open()
	c = conn.cursor()
	c.execute('select value from data where name=? and profile=?;', (str(name), str(self.agentAddress)))
	data = c.fetchone()
	close(conn)
	if data is None:
		return default
	else:
		return data[0]


def setData(self, name, value):
	"""
		set the value of the named data to value
	"""
	conn = open()
	c = conn.cursor()
	c.execute('select value from data where name=? and profile=?;', (str(name), str(self.agentAddress)))
	data = c.fetchone()
	if data is None:
		c.execute('insert into data values (?,?,?);', (str(name), str(value), str(self.agentAddress)))
	else:
		c.execute('update data set value=? where name=? and profile=?;',
				  (str(value), str(name), str(self.agentAddress)))
	close(conn)
	return


def getSetting(self, name, default):
	"""
		return a settings value from the database
		return default if no value exists
	"""
	conn = open()
	c = conn.cursor()
	c.execute('select value from settings where name=? and profile=?;', (str(name), str(self.agentAddress)))
	data = c.fetchone()
	close(conn)
	if data is None:
		return default
	else:
		return data[0]


def setSetting(self, name, value):
	"""
		set the value of the named setting to value
	"""
	conn = open()
	c = conn.cursor()
	c.execute('select value from settings where name=? and profile=?;', (str(name), str(self.agentAddress)))
	data = c.fetchone()
	if data is None:
		c.execute('insert into settings values (?,?,?);', (str(name), str(value), str(self.agentAddress)))
	else:
		c.execute('update settings set value=? where name=? and profile=?;',
				  (str(value), str(name), str(self.agentAddress)))
	close(conn)
	return
