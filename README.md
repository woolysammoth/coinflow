coinflow
========

Phase 1 CoinFlow app for the netvend network

current commands are:

/add [seed value] - create a new agent (small initial funding supplied)

/login [nickname / address / seed value] - login to existing agent

/tip [nickname / address / post id] - tip a user or post

/balance - view the balance of your current agent

/post [message] - post a message 

/feed - fetch an updated list of the posts made by agents you follow

/history [nickname / address] - show the last 10 posts for the specified agent. If address is blank, the currently logged in agent is used

/nick [nickname] - set a nickname for the logged in agent. nickname is checked for uniqueness

/listagents - display a list of all agents on the system. Shows nick name if they have one otherwise default to address

/follow [nickname / address] - follow the specified agent. can specify address or nickname

/listfollows - display a list of every one you follow with your currently logged in agent

/listprofiles - display a list of all agents you have created or logged in as. updated as nick changes

/gettipamount - display the current tip amount in mu-sat (defaults to 1 each time you log in. saving this value is on the roadmap)

/settipamount [amount] - set the tip amount to the specified value in mu-sat

/whisper [nickname / address] - start a whisper. The next thing you enter in the text input will be encrypted and sent as a single message to the specified agent.

WARNING - as this is only a proof of concept, all messages are encrypted using the same default password.
Do not use this functionality for anything that you want to keep secret. 
Either change the password property in the code or wait for me to add the functionality to change it from within the app



More commands are coming as well as further functionality.
This software is just me finding out what netvend can do and messing around.
Don't trust it as it is fairly rough around the edges


It will require kivy <http://kivy.org> and pyCrypto <https://www.dlitz.net/software/pycrypto/> in order to work


Comments welcome
