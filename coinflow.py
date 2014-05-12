import commands.commands as com
import util.db as db
import util.util as util
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.clock import Clock

db.gen()

class CoinFlowApp(App):
	"""
		The base Application class needed for Kivy
		chbsagent is for the alpha/beta phase to ensure new agents have funds
		agent starts off as None to indicate a logged out state
	"""

	#define some properties

	agent = None
	allNicks = []
	unit = 'satoshi'
	tipAmount = 1
	pollInterval = 10
	isChat = False
	isWhisper = False
	password = 'T3stFl0w'


	def poll(self, dt):
		"""
			Poll the server for new information every %pollInterval% seconds
		"""
		#check for new whisper posts directed to us
		util.whisperPoll(self)
		if self.isChat is False:
			pass
		else:
			util.chatPoll(self)


	def togglePoll(self, active):
		"""
			set or unset the automatic polling based on the vale of active
		"""
		if active is True:
			Clock.schedule_interval(self.poll, self.pollInterval)
		else:
			Clock.unschedule(self.poll)


	def sendCommand(self, instance, value=False):
		"""
			This method is called whenever the input box looses focus
			It looses focus on a click out side itself or when Enter is pressed
			We list the available commands here but the grunt work of the functions is done in commands.py
		"""

		if value:
			return

		#get the command and clear the input box
		inText = self.input.text
		if inText == '':
			return
		self.input.text = ''

		#if chat has been activated we send the inputted text as a chat message
		if self.isChat is True:
			com.commandSendChat(self, inText)
			return

		if self.isWhisper is True:
			com.commandWhisper(self, inText)

		#options
		command = inText.split(None, 1)

		#/add [seed] - set up a new agent using the supplied seed
		#for the time being we add a simple balance to allow for testing
		if command[0].lower() == '/add':
			com.commandAdd(self, command)
			return

		#/login [nickname / address / seed] - login as an existing agent
		elif command[0].lower() == '/login':
			com.commandLogin(self, command)
			return

		#/tip [nickname / address] - send a tip to another user or post
		elif command[0].lower() == '/tip':
			com.commandTip(self, command)
			return

		#/balance - view the balance of your current agent
		elif command[0].lower() == '/balance':
			com.commandBalance(self, command)
			return

		#/post [message] - post a message to netvend
		elif command[0].lower() == '/post':
			com.commandPost(self, command)
			return

		#/history [address] - view the last ten posts for the specified user (defaults to self)
		elif command[0].lower() == '/history':
			com.commandHistory(self, command)
			return

		#/nick - set your nickname
		elif command[0].lower() == '/nick':
			com.commandNick(self, command)
			return

		#/listagents - list all users on the system
		elif command[0].lower() == '/listagents':
			com.commandListAgents(self, command)
			return

		#/follow [agent] - follow the specified agent
		elif command[0].lower() == '/follow':
			com.commandFollow(self, command)
			return

		#/listfollows [agent] - list everyone you follow
		elif command[0].lower() == '/listfollows':
			com.commandListFollows(self, command)
			return

		#/listprofiles [agent] - list all available profiles
		elif command[0].lower() == '/listprofiles':
			com.commandListProfiles(self, command)
			return

		#/gettipammount - get the current tip amount
		elif command[0].lower() == '/gettipamount':
			com.commandGetTipAmount(self, command)
			return

		#/settipammount [amount] - set the current tip amount
		elif command[0].lower() == '/settipamount':
			com.commandSetTipAmount(self, command)
			return

		#/feed - update the feed of posts from your followed agents
		elif command[0].lower() == '/feed':
			com.commandFeed(self, command)
			return

		#/getunit - show the currency display unit
		elif command[0].lower() == '/getunit':
			com.commandGetUnit(self, command)
			return

		#/setunit - set the currency display unit
		elif command[0].lower() == '/setunit':
			com.commandSetUnit(self, command)
			return

		#/chat - initiate a chat session
		elif command[0].lower() == '/chat':
			com.commandChat(self, command)

		#/whisper [nick / address] - initiate an encrypted chat with the specified agent
		elif command[0].lower() == '/whisper':
			com.commandWhisper(self, command)


		#otherwise we don't know what's going on
		else:
			self.writeConsole(command[0] + ' is not a recognised command')
			return


	def writeConsole(self, text):
		"""
			Write the text to a new line on the Output console
		"""

		#get the current output text and store it
		outText = self.output.text
		#once we've figured out what to do, write to the console and return focus to the input box
		self.output.text = str(outText) + str(text) + '\n'
		self.input.focus = True


	def build(self):
		"""
			Add the widgets and build the UI
		"""

		self.root = BoxLayout(orientation='vertical')
		self.input = TextInput(size_hint_y=None, height=30, multiline=False, focus=True)
		self.output = TextInput(size_hint=(1, .9), background_color=[0, 0, 0, 0], foreground_color=[1, 1, 1, 1],
								readonly=True,
								text='Welcome to CoinFlow\n===================\n\n/add [seed value] will create a new agent.\n/login [nickname/address/seed value] will login to an existing agent\n/nick [nickname] sets your agents nickname.\n/post [message] will post a message to netvend.\n/tip [nickname/address/post_id] will send a tip\n\nHave fun!\n\n')


		self.input.bind(focus=self.sendCommand)
		self.root.add_widget(self.output)
		self.root.add_widget(self.input)

		return self.root


if __name__ == '__main__':
	CoinFlowApp().run()
