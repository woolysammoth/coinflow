coinflow
========

Phase 1 CoinFlow app for the netvend network

Installation
============

I have included PyCrypto in the repository so there is no longer a need to download that separately

Visit http://kivy.org to get the latest package (kivy is used to build the graphical interface. This may be overkill at the moment but it does allow for future expansion)
The installation of kivy will vary depending on your operating system

On windows you will use what is known as a portable package. To use this you download the zip file from http://kivy.org and unzip it on your computer.
open up a command prompt and navigate to the kivy directory you just unzipped
run 'kivy.bat'
this will tell that command window to use the kivy directory as it's base and so kivy will work.
In the same command window, navigate to the coinflow directory and run 'python coinflow.py'

For Linux and Mac, the kivy instructions are a bit different in that it's a full install rather than a portable package like for Windows.
Probably best to follow the instructions on the kivy website  
Once installed go to the coinflow directory and run 'python coinflow.py'



current coinflow commands are:

/add [seed value] - create a new agent (small initial funding supplied)
ATTENTION - there is an issue with this currently. Until it is resolved, login as the 'correct horse battery staple' agent to test coinflow

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
Either change the password property in the code or wait for me to add the functionality  


More commands are coming as well as further functionality.   
This software is just me finding out what netvend can do and messing around.   
Don't trust it as it is fairly rough around the edges.   


Comments welcome
