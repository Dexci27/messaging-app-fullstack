# Message App

### Video Demo:  https://youtu.be/ZI1hYLPCu7E

### Description:

##### What the project is about
In this project, I created a standard messaging app inspired by those of WhatsApp and Instagram etc. In this messaging app, the user can create a conversation with another user and a group conversation with more than one user. For group conversations, it is possible to add new members to the group even after the group discussion as been created.

To make this project I used the following technologies:
- Python with Flask
- SQLite3 using cs50 SQL module
- HTML, CSS, and JavaScript.

##### Features
- User registration and login with secure password hashing
- One-to-one private conversations between two users
- Group conversations with more than two users
- Adding new members to group conversations
- Front end JavaScript API to display conversations in order to improve user experience and prevent too much navigation between pages
- User authorization checks on the server to prevent unauthorized access and actions on conversations that the user is not part of
- Responsive web app that adapts to different screen sizes
- Display of conversations sorted by most recent messages
- Tracking "last seen message" per user and conversation to notify when a new message that the user has not yet seen arrives

##### Project files

###### Server/Backend - app.py
This is the main app file of the messaging app. It contains the flask server side code that renders the page.

The server has the following routes :
- "/login" : This is the route for the user to enter their username and password to log in their account.
- "/register" : This is where the user can create a new account by entering a new username (username are unique in the database) and a password.
- "/logout" : This is where the user can log out of their account. This will clear the user's session.
- "/" : This is the main page of the web app. It contains two main sections. The first section is the conversation list section which contains a list of all the conversation that the user has had, sorted by most recent message. The second section is the conversation area section. It is empty at first, but then when a user clicks on one of the item in conversation list, the conversation area displays that conversation. The conversation area is where the user can see the messages in the conversation, send messages etc.
- "/conversations/<int:conversation_id>" : This is the route that displays an existing conversation. It is only called as an API by the front end "script.js" file and it returns the template for conversations. This templates contains information such as the name of the conversation, and all the messages that have been sent to that conversation. There is also a form with an input box for the user to send a message in the conversation.
- "/conversations/new" : This is the route to create a new conversation between two users. The user must enter the username of the person with which they want to create a new conversation and the conversation will be created between the two.
- "/conversations/groups/new" : This is the route to create a new group conversation. Unlike normal conversations, a group conversation can include more than two users. The user will be prompted for the name of the group, and then later on can add new members as wished to the group (using their username).
- "/conversations/groups/<int:group_id>/members/add" : This is the route to add a new member to a group conversation. The user will be asked for the username of the member they want to add and then that member will be added to the group and will thus be able to see and send messages in the group.

###### Frontend - script.js
This is the frontend part of the webapp. This file mainly sends API request to "/conversations/<int:conversation_id>" in order to show a conversation (when the user clicks on that conversation) or to add a message to a conversation (when the user sends a message).
I decided to do it this way to improve user experience. I did not want the user to be redirected to a new page to see a conversation, and so I thought that making API request and then displaying the conversation on the page the user already is would be best.

###### Database - messageApp.db
This is the database of the web app where all information are stored. This database uses SQLite3 as used in CS50X. It is a relational database with the following tables:

- users: This table stores information about the user such as id, username, and password hash.
- conversations: This table stores information about each conversation. These information include id, type (if it is a private or group conversations), date when the conversation was created, name of the conversation (only for group conversations else null).
- conversation_members: This links users to conversations and also tracks last seen message by each user in a given conversation. It enables to know if a user is part of a given conversation or not. This tables contains foreign keys linking conversation id, user id, and last seen message id.
- messages: This table stores the messages sent by users to their conversations. For each message, information about the id of the sender and the id of the conversation to which the message was sent is kept. We also keep the type of the message (can be a simple message or a notification sent automatically), and the date the message was sent. I created an index on the messages table by conversation id and date such that messages of a given conversation can be retrieved fast.

###### Other files
Other files used for the project include :
- Flask session folder : Sessions are stored in a file system. Thus this folder contains all the user sessions.
- Styling files : These are CSS files used for styling the web app.
- Template files : These are the HTML templates used in the web app.


##### Design decisions and tradeoffs

###### Route naming and proper syntax
Having proper syntax and code was something that I deemed to be very important. At first, when I started working on the code, my routes add just the same name as functions (such as "/new_conversation" to create a new conversation). But then I understood that this wasn't the proper way to do it.  So I learnt about REST APIs naming convention, and I used this knowledge to name my routes. This made that I used "/conversations/new" for the route to create a new conversation.

###### Storing conversation messages in the database
As I wanted to have fast retrieval of messages for each conversations, I first thought that having just one single messages table to store all messages would be slow. So at first I created one table per conversation because I thought that querying having a single table for each conversation will make it faster to query messages for that conversation. However, as I made research on proper database design, I realized that this assumption was wrong. I thus learned about the proper way and implemented a singles message table to store all messages as well as an index on messages to ensure fast retrieval of messages. This is a better way to have fast queries.

###### User experience
I made several decisions with the aim of improving user experience. One of these decisions that was major was fetching for conversations with JavaScript and then displaying it on the home page instead of redirecting the user to another page for each discussion. This makes it more fluid and natural for the user. Doing this change required that I changed the logic of the route so as it works proper to return the page content to the front end.


##### Limitations and future improvements

Due to time constraints, I could not implement more of the features that I wanted to. I focused on making a Minimum Viable Product to have a functioning web app with the most essential features for the project submission. Here are a list of improvements that could be made for future versions of the web app:

- More features such as deleting a conversation, removing a member from a group conversation, having more information about users and conversations such as profile pictures, descriptions etc.
- Automatic loading of messages and reloading of the webpage when changes occurs such a new message was sent.
- Adding notifications for when an action occurs in a conversation such as a new conversation being created, a new member being added to a group conversation etc.
