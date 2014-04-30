import sqlite3 

def genDB():
	conn = sqlite3.connect('coinflow.db')
	c = conn.cursor()

	c.execute('create table follows (id integer primary key, nick varchar(255), address varchar(35), account varchar(255));')

	c.execute('create table profiles (id integer primary key, nick varchar(255), seed varchar(255));')

	conn.commit()
	conn.close()
	return
