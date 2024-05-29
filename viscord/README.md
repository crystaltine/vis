# Information about Viscord (Discord in the Terminal!) 

**Languages, Libraries, etc** 

- Python (3.11 or newer)
  
- HTML backend language <- for the framework/UI
  
- Blessed <- for connecting to the Terminal and working within it
  
- PostSQL software <- for Database
  
- datetime <- for timestamp
  
- uuid <- for generating a unique user id for each user 

and much more! 

**Database**

  - The Database is written using PostSQL and consists of several tables such as UserInfo, MemberInfo, SeverInfo, etc. Each table contains various columns, each which hold a specific data necessary to make our viscord app function similarly to its inspiration: Discord 
  
  - Throughout the backend code, we communicate with this PostSQL Database in order to fetch, select, and send data. In order to make sure the database is running properly and getting updated as it recieves queries and calls, we will always fill up the database with prewritten data. 

  - Open CreateDiscordDB.sql and populateDB.py to see all of this in code!
  
**Server/Client**

  - Using the data in the database, the server allows us to perform everything to make viscord work like Discord. The server communicates with the client side (obviously 😁) and collects data on the username, password, messages, and more which then gets sent to the server which sends it to the database to use for security checks, password checks, username checks, etc.
    
  - Using the Server, we perform a login authorization check, which means if the username and password match up to an account in our postSQL database, we let the user login, else we throw an exception. This also lets us provide the ability of account creation.
    
**User Interface**

  - The user interface was originally going to be created using blessed.py, but after realizing that printing everything to the terminal for a certain amount of time was going to be hectic and and issue. We decided to use a self created framework. <- *basic UI done, need to fully connect server and database to user interface* 

  - The user interface gives users the ability to login in to their accounts <- *UI done, login works, server recognizes a user has logged in* 

  - The user interface contains the ability for users to create their own viscord servers, chat channels, and assign specific roles to each member in a viscord server. <- *code done, UI implementation in progress* 
    
  - It also contains the ability for users to go into 2 people voice channels and have a conversation with each other. on the UI there will be a specific spot for roles, chats, servers, and voice chats for ease of access for users. <- *code done, UI implementation in progress*

  - through the use of the database, every user will have a unique color and symbol associated with their name and they will also have the ability to create a nickname, this will be displayed on the UI. <- *code done, UI implementation in progress* 

  - Users are able to pin and reply to messages as well as scroll through prior messages that were sent. <- *work in progress* 

  - Users are able to send to invites to other servers to other users <- *code done, UI implementation in progress*
  - 
**IMPORTANT LINKS**
  - https://blessed.readthedocs.io/en/latest/
  - https://github.com/crystaltine/visage 
