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

	c.execute('create table follows (id integer primary key, nick varchar(255), address varchar(35), profile varchar(255));')

	c.execute('create table profiles (id integer primary key, nick varchar(255), seed varchar(255));')
	
	c.execute('create table data (name varchar(255), value varchar(255), profile varchar(255));')
	
	c.execute('create table nicks (id integer primary key, nick varchar(255), address varchar(35));')
	
	c.execute('create table settings (name varchar(255), value varchar(255), profile varchar(255));')

	close(conn)
	return
	