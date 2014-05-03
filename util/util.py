import netvend.netvend as netvend
import db as db
import sqlite3

def getAgent(self):
	"""
		connect to netvend agent using the specified seed
		agent is created if it doesn't already exist
	"""
	try:
		self.agent = netvend.Agent(self.agentSeed, seed=True)
	except netvend.NetvendResponseError as e:
		self.writeConsole('Failed to get agent - ' + str(e))
	return
	
def getAddress(self):
	"""
		get the address for the currently logged in agent
	"""
	try:
		self.agentAddress = self.agent.get_address()
	except netvend.NetvendResponseError as e:
		self.writeConsole('Failed to get address - ' + str(e))
	return
	
def initialTip(self):
	"""
		send a tip from the correct horse battery staple agent to get the new agent funded
	"""
	try:
		chbsagent = netvend.Agent('correct horse battery staple', seed=True)
		response = chbsagent.tip(self.agentAddress, netvend.convert_value(10, 'satoshi', 'usat'), None)
	except netvend.NetvendResponseError as e:
		self.writeConsole('Failed to tip new agent - ' + str(e))
	return
	
def getBalance(self):
	"""
		get the balance for the logged in agent
	"""
	self.unit = getSetting(self, 'unit', 'satoshi')
	try:
		self.agentBalance = netvend.convert_value(self.agent.fetch_balance(), 'usat', self.unit)
	except netvend.NetvendResponseError:
		self.agentBalance = 0
	return
	
def putQuery(self, query):
	"""
		send the supplied query to netvend and return the response or False on error
	"""
	try:
		response = self.agent.query(query)
	except netvend.NetvendResponseError as e:
		if 'f:' in str(e):
			self.writeConsole('Not enough funds for query - ' + str(e) + ' - ' + query)
		else:
			self.writeConsole('Query error - ' + str(e) + ' - ' + query)
		return False
	if response['command_result']['num_rows'] < 1:
		self.writeConsole('No rows returned - ' + query)
		return False
	return response['command_result']
		
def getNick(self, address):
	"""
		get the nickname associated with the specified address
	"""
	conn = db.open()
	c = conn.cursor()
	c.execute('select nick from nicks where address = ?;', (address,))
	nick = c.fetchone()
	db.close(conn)
	if nick is None:
		return address
	else:
		return nick[0]	
	
def isAddress(check):
	"""
		return True if the check string is a bitcoin address
	"""
	import re
	if re.search('^[13][a-zA-Z0-9]{26,33}$', check):
		return True
	else:
		return False

def getAllNicks(self):
	"""
		return a list of nicknames for all users
	"""
	self.allNicks = []
	query = "select address from accounts" 
	rows = putQuery(self, query)
	if rows is False:
		return False
	for row in rows['rows']:
		nick = getNick(self, str(row[0]))
		self.allNicks.append(nick)
	return
	
	
def pollAllPosts(self):
	"""
		get the highest post id and compare it to our last known post id
		save it and alert if higher
	"""
	query = "select post_id from posts order by post_id desc limit 1"
	rows = putQuery(self, query)
	if rows is False:
		return False
	self.newAllPostId = rows['rows'][0][0]
	conn = db.open()
	c = conn.cursor()
	c.execute('select value from data where name=? and profile=?;', ('all_post_id',str(self.agentAddress)))
	PostId = c.fetchone()
	if PostId is None:
		self.savedAllPostId = 0
	else:
		self.savedAllPostId = PostId[0]
	if self.newAllPostId > self.savedAllPostId:
		if self.savedAllPostId == 0:
			c.execute('insert into data values (?,?,?);', ('all_post_id', str(self.newAllPostId), str(self.agentAddress)))
		else:
			c.execute('update data set value = ? where name = ? and profile = ?;', (str(self.newAllPostId), 'all_post_id', str(self.agentAddress)))
		db.close(conn)
		return True
	else:
		db.close(conn)
		return False
		
def checkAllPosts(self):
	"""
		check any new posts for save-able information
	"""
	return
	
def checkNewNicks(self):
	"""
		check any new posts for new nicknames	
	"""
	query = "select address, data from posts where post_id > " + str(self.savedAllPostId) + " and data like 'nick:%'"
	rows = putQuery(self, query)
	if rows is False:
		return False
	conn = db.open()
	c = conn.cursor()
	for row in rows['rows']:
		c.execute('select id from nicks where address = ?;', (row[0],))
		id = c.fetchone()
		nick = row[1].split(':',1)
		if id is None:
			c.execute('insert into nicks (nick, address) values (?,?);', (nick[1], row[0]))
		else:
			c.execute('update nicks set nick = ? where address = ?;', (nick[1], row[0]))
		#also check follows for potential updates
		c.execute('select nick from follows where address = ?;', (row[0],))
		checkNick = c.fetchone()
		if checkNick is not None:
			if nick[1] != checkNick[0]:
				c.execute('update follows set nick=? where address=?;', (nick[1], row[0]))
	db.close(conn)
	return		
		
def getFollows(self):
	"""
		return the list of follows from the db
		update the list of nicks first
	"""
	if pollAllPosts(self):
		checkNewNicks(self)
	conn = db.open()
	c = conn.cursor()
	c.execute('select nick, address from follows where profile=?;', (str(self.agentAddress),))
	follows = c.fetchall()
	db.close(conn)
	return follows
	
def pollFollowsPosts(self):
	"""
		get the highest post id of posts made by our follows
		compare to our stored id and report
	"""
	follows = getFollows(self)
	if not follows:
		return False
	followList = ''
	for follow in follows:
		followList += '\'' + str(follow[1]) + '\','
	query = "select post_id from posts where address in (" + followList[:-1] + ") order by post_id desc limit 1"
	rows = putQuery(self, query)
	if rows is False:
		return False
	self.newFollowPostId = rows['rows'][0][0]
	conn = db.open()
	c = conn.cursor()
	c.execute('select value from data where name=? and profile=?;', ('follow_post_id',str(self.agentAddress)))
	PostId = c.fetchone()
	if PostId is None:
		self.savedFollowPostId = 0
	else:
		self.savedFollowPostId = PostId[0]
	if self.newFollowPostId > self.savedFollowPostId:
		if self.savedFollowPostId == 0:
			c.execute('insert into data values (?,?,?);', ('follow_post_id', str(self.newFollowPostId),str(self.agentAddress)))
		else:
			c.execute('update data set value=? where name=? and profile=?;', (str(self.newFollowPostId), 'follow_post_id',str(self.agentAddress)))
		db.close(conn)
		return True
	else:
		db.close(conn)
		return False
	
def displayFollowsPosts(self):
	"""
		display latest posts by your follows
	"""
	follows = getFollows(self)
	if not follows:
		return False
	followList = ''
	for follow in follows:
		followList += '\'' + str(follow[1]) + '\','
	query = "select post_id, address, data, ts from posts where address in (" + followList[:-1] + ") and post_id > " + str(self.savedFollowPostId) + " order by ts asc"
	rows = putQuery(self, query)
	if rows is False:
		return False
	self.writeConsole('\n== New Posts from your followed agents ==\n')
	for row in rows['rows']:
		if 'post:' in row[2]:
			post = row[2].split(':', 1)[1]
		else:
			post = row[2]
		self.writeConsole(str(getNick(self, row[1])) + " [" + str(row[3]) + '] (' + str(row[0]) + ') >> ' + str(post))
	return
	
def getSeedFromNick(nick):
	"""
		find and return the seed value for the associated nick
		check profiles as we only store seeds for those
		nick is automatically the address if no nick is set
		return False if nick not found
	"""
	conn = db.open()
	c = conn.cursor()
	c.execute('select seed from profiles where nick=?;', (nick,))
	data = c.fetchone()
	if data is None:
		return False
	else:
		return data[0]
		
def getAddressFromNick(nick):
	"""
		find and return the address value for the associated nick
		check nicks as we should store every possible one
		nick is automatically the address if no nick is set
		return False if nick not found
	"""
	conn = db.open()
	c = conn.cursor()
	c.execute('select address from nicks where nick=?;', (nick,))
	data = c.fetchone()
	if data is None:
		return False
	else:
		return data[0]	

def getAddressFromPostID(self, postId):
	"""
		get the address of the agent who created the post with the specified ID
		For tipping purposes
		return False if nothing found
	"""
	query = "select address from posts where post_id = " + postId
	rows = putQuery(self, query)
	if rows is False:
		return False
	return rows['rows'][0][0]
	
def getSetting(self, name, default):
	"""
		return a settings value from the database
		return default if no value exists
	"""
	conn = db.open()
	c = conn.cursor()
	c.execute('select value from settings where name=? and profile=?;', (str(name), str(self.agentAddress)))
	data = c.fetchone()
	db.close(conn)
	if data is None:
		return default
	else:
		return data[0]
		
def setSetting(self, name, value):
	"""
		set the value of the named setting to value
	"""
	conn = db.open()
	c = conn.cursor()
	c.execute('select value from settings where name=? and profile=?;', (str(name), str(self.agentAddress)))
	data = c.fetchone()
	if data is None:
		c.execute('insert into settings values (?,?,?);', (str(name), str(value), str(self.agentAddress)))
	else:
		c.execute('update settings set value=? where name=? and profile=?;', (str(value), str(name), str(self.agentAddress)))
	db.close(conn)
	return