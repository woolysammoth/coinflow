import netvend.netvend as netvend
import sqlite3

def getAgent(self, command):
	"""
		connect to nedvend using the specified seed
	"""
	try:
		self.agent = netvend.Agent(command[1], seed=True)
	except netvend.NetvendResponseError as e:
		self.writeConsole('Failed to create agent - ' + str(e))
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
		response = self.chbsagent.tip(self.agentAddress, netvend.convert_value(1, 'satoshi', 'usat'), None)
	except netvend.NetvendResponseError as e:
		self.writeConsole('Failed to tip new agent - ' + str(e))
	return
	
def getBalance(self):
	"""
		get the balance for the logged in agent
	"""
	try:
		self.agentBalance = self.agent.fetch_balance()
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
		if 'f:' in e:
			self.writeConsole('Not enough funds for query - ' + query)
		else:
			self.writeConsole('Query error - ' + str(e) + '\n' + query)
		return False
	if response['command_result']['num_rows'] < 1:
		self.writeConsole('No rows returned')
		return False
	return response['command_result']
		
def getNick(self, address):
	"""
		get the nickname associated with the specified address
	"""
	conn = sqlite3.connect('coinflow.db')
	c = conn.cursor()
	c.execute('select nick from nicks where address = ?;', (address,))
	nick = c.fetchone()
	conn.close()
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
	conn = sqlite3.connect('coinflow.db')
	c = conn.cursor()
	c.execute('select nick from nicks;')
	nicks = c.fetchall()
	conn.close()
	if not nicks:
		query = "select address from accounts"
		rows = putQuery(self, query)
		if rows is False:
			return False
		self.allNicks = []
		for row in rows['rows']:
			nick = getNick(self, str(row[0]))
			self.allNicks.append(nick)
		return
	else:
		for nick in nicks:
			self.allNicks.append(nick[0])
	
def pollAllPosts(self):
	"""
		get the highest post id and compare it to our last known post id
		save it and alert if higher
	"""
	query = "select post_id from posts order by post_id desc limit 1"
	rows = putQuery(self, query)
	if rows is False:
		return False
	self.newAllPostId = rows['rows'][0]
	conn = sqlite3.connect('coinflow.db')
	c = conn.cursor()
	c.execute('select value from data where name=?;', ('all_post_id',))
	PostId = c.fetchone()
	if PostId is None:
		self.savedAllPostId = 0
	else:
		self.savedAllPostId = PostId[0]
	if self.newAllPostId > self.savedAllPostId:
		if self.savedAllPostId == 0:
			c.execute('insert into data values (?,?);', ('post_id', str(self.newAllPostId)))
		else:
			c.execute('update data set value = ? where name = ?;', (str(self.newAllPostId), 'all_post_id'))
		conn.commit()
		conn.close()
		return True
	else:
		conn.close()
		return False
		
def checkAllPosts(self):
	"""
		check any new posts for save-able information
	"""
	checkNewNicks(self)
	return
	
def checkNewNicks(self):
	"""
		check any new posts for new nicknames	
	"""
	query = "select address, data from posts where post_id > " + str(self.savedAllPostId) + " and data like 'nick:%'"
	print(query)
	rows = putQuery(self, query)
	print(rows)
	if rows is False:
		return False
	conn = sqlite3.connect('coinflow.db')
	c = conn.cursor()
	for row in rows['rows']:
		c.execute('select id from nicks where address = ?;', (row[0],))
		id = c.fetchone()
		print(id,row[1], row[0])
		if id is None:
			c.execute('insert into nicks (nick, address) values (?,?);', (row[1].split(':',1)[1], row[0]))
		else:
			c.execute('update nicks set nick = ? where address = ?;', (row[1].split(':',1)[1], row[0]))
	return
			
		
		
def getFollows(self):
	"""
		return the list of follows from the db
	"""
	conn = sqlite3.connect('coinflow.db')
	c = conn.cursor()
	c.execute('select nick, address from follows where account = ?;', (str(self.agentNick),))
	follows = c.fetchall()
	conn.close()
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
		followList += follow[1] + ','
	followList = followList[:1]
	query = "select post_id from posts where address in ('" + followList + "') order by post_id desc limit 1"
	rows = putQuery(self, query)
	if rows is False:
		return False
	self.newFollowPostId = rows['rows'][0]
	conn = sqlite3.connect('coinflow.db')
	c = conn.cursor()
	c.execute('select value from data where name=?;', ('follow_post_id',))
	PostId = c.fetchone()
	if PostId is None:
		self.savedFollowPostId = 0
	else:
		self.savedFollowPostId = PostId[0]
	if self.newFollowPostId > self.savedFollowPostId:
		if self.savedFollowPostId == 0:
			c.execute('insert into data values (?,?);', ('follow_post_id', str(self.newFollowPostId)))
		else:
			c.execute('update data set value = ? where name = ?;', (str(self.newFollowPostId), 'follow_post_id'))
		conn.commit()
		conn.close()
		return True
	else:
		conn.close()
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
		followList += follow[1] + ','
	followList = followList[:1]
	query = "select post_id, address, data, ts from posts where address in ('" + followList + "') and post_id > " + str(self.savedFollowPostId) + "order by ts desc"
	rows = putQuery(self, query)
	if rows is False:
		return False
	for row in rows['rows']:
		self.writeConsole(getNick(self, row[1]) + " [ " + row[3] + ' ] ( ' + row[0] + ' ) >> ' + row[2].split(':',1)[1])
	return