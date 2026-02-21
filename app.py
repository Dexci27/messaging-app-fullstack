from cs50 import SQL
from datetime import datetime
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

# Configure the application
app = Flask(__name__)

# Configuring the session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# This is the database that contains all information related to this message app
database = SQL("sqlite:///messageApp.db")

# Checking if the user is already logged in
def check_login_status() :
    try :
        if session["user_id"] is None :
            return False
        return True
    except :
        return False

def find_conversation_name(conversation_id) :
    conversation_info = database.execute("SELECT * FROM conversations WHERE id = ?", conversation_id)[0]
    if conversation_info["type"] == "group" :
        return conversation_info["name"]
    else :
        conversation_name = database.execute("SELECT username FROM users WHERE id = (SELECT user_id FROM conversation_members WHERE conversation_id = ? AND user_id <> ?)", conversation_id, session["user_id"])[0]["username"]
        return conversation_name

def find_username(user_id) :
    return database.execute("SELECT username FROM users WHERE id = ?", user_id)[0]["username"]


def sort_key(m):
    msg = m.get("last_conversation_message")
    if not msg:
        return datetime.max
    return datetime.fromisoformat(msg["date"])


@app.route("/", methods=["GET", "POST"])
def index() :

    # checking if there is a user logged in
    if not check_login_status() :
        return redirect("/login")

    # list of all the id of conversation that the user has made
    user_conversations_info = database.execute("SELECT conversation_id, last_seen_message_id FROM conversation_members WHERE user_id = ? ", session["user_id"])

    for i in range(len(user_conversations_info)) :
        user_conversations_info[i]["type"] = database.execute("SELECT type FROM conversations WHERE id = ?", user_conversations_info[i]["conversation_id"])[0]["type"]
        # if it is a new conversation and thus there is not yet a single message
        try :
            user_conversations_info[i]["last_conversation_message"] = database.execute("SELECT * FROM messages WHERE conversation_id = ? ORDER BY date DESC LIMIT 1", user_conversations_info[i]["conversation_id"])[0]
        except:
            pass


    # sorting the conversation list by most recent message
    user_conversations_info.sort(key=sort_key, reverse=True)


    username = database.execute("SELECT username FROM users WHERE id = ?", session["user_id"])[0]["username"]

    return render_template("index.html", username=username, user_id=session["user_id"], user_conversations_info=user_conversations_info,
                           find_conversation_name=find_conversation_name, find_username=find_username)

@app.route("/login", methods=["GET", "POST"])
def login() :

    # remove any previous user's session that was log in
    session.clear()

    if request.method == "GET" :
        return render_template("login.html")

    username = request.form.get("username")
    if not username :
        return render_template("login.html", error_message="Error : Must enter username")

    password = request.form.get("password")
    if not password :
        return render_template("login.html", error_message="Error : Must enter password")

    row = database.execute("SELECT * FROM users WHERE username = ?", username)

    if len(row) != 1:
        return render_template("login.html", error_message="Error : invalid username and/or password (u)")

    if not check_password_hash(row[0]["password_hash"], password) :
        return render_template("login.html", error_message=f"Error : invalid username and/or password (p)")

    session["user_id"] = row[0]["id"]

    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register() :
    if request.method == "GET" :
        return render_template("register.html")

    username = request.form.get("username")
    if not username :
        return render_template("register.html", error_message="Error : Must enter username")

    password = request.form.get("password")
    if not password :
        return render_template("register.html", error_message="Error : Must enter password")
    hash = generate_password_hash(password)


    user_exists = database.execute("SELECT id FROM users WHERE username = ?", username)
    if user_exists :
        return render_template("register.html", error_message="Error : This user already exists")

    database.execute("INSERT INTO users (username, password_hash) VALUES(?, ?)", username, hash)

    return redirect("/")


@app.route("/logout")
def logout() :
    session.clear()
    return redirect("/")

@app.route("/conversations/new", methods=["GET", "POST"])
def new_conversation() :

    # checking if there is a user logged in
    if not check_login_status() :
        return redirect("/login")

    # redirect the user to the normal page if the request method is "GET"
    if request.method == "GET" :
        return render_template("new_conversation.html")

    # getting the name of the member that the user wants to add
    member_username = request.form.get("member_username")
    if not member_username :
        return render_template("new_conversation.html", error_message="Error : Must have new member's username")

    # checking if the member username exists in the database
    member_id = database.execute("SELECT * FROM users WHERE username = ?", member_username)
    if not member_id :
        return render_template("new_conversation.html", error_message="Error : member not found")
    member_id = member_id[0]["id"]

    # checking if the member id is the same as the user id i.e user cannot create conversation with himself (for the moment at least)
    if member_id == session["user_id"] :
        return render_template("new_conversation.html", error_message="Error : member cannot be yourself")


    # checking if a discussion between the user and that member already exists
    existing_discussion = database.execute("""  SELECT conversation_id FROM conversation_members
                                                JOIN conversations ON conversation_members.conversation_id = conversations.id
                                                WHERE user_id = ?
                                                AND type = 'person'
                                                AND conversation_id IN
                                                (
                                                    SELECT conversation_id FROM conversation_members WHERE user_id = ?
                                                )""", session["user_id"], member_id)
    if existing_discussion :
        return render_template("new_conversation.html", error_message="Error : a conversation already exist between you two")



    # creating a new discussion between the user and that member
    database.execute("INSERT INTO conversations (type) VALUES('person')")
    conversation_id = database.execute("SELECT id FROM conversations ORDER BY date_created DESC LIMIT 1")[0]["id"]

    # adding these two as members of that conversation
    database.execute("INSERT INTO conversation_members (conversation_id, user_id) VALUES(?, ?)", conversation_id, session["user_id"])
    database.execute("INSERT INTO conversation_members (conversation_id, user_id) VALUES(?, ?)", conversation_id, member_id)

    return redirect("/")


@app.route("/conversations/<int:conversation_id>", methods=["GET", "POST"])
def conversations(conversation_id) :
    # checking if there is a user logged in
    if not check_login_status() :
        return redirect("/login")

    # checking if the user is a member of the conversation to be able to view it and send messages
    authorization = database.execute("SELECT id FROM conversation_members WHERE conversation_id = ? AND user_id = ?", conversation_id, session["user_id"])
    if not authorization :
        return render_template("conversations.html", error_message="ERROR : No Conversation found")

    if request.method == "GET" :

        conversation_info = {
            "messages" : database.execute("SELECT * FROM messages WHERE conversation_id = ? ORDER BY date DESC", f"{conversation_id}"),
            "type" : database.execute("SELECT type FROM conversations WHERE id = ?", conversation_id)[0]["type"],
            "name" : find_conversation_name(conversation_id),
            "id" : conversation_id,
            "members" : database.execute("""
                                            SELECT id, username FROM users WHERE id IN(
                                                SELECT user_id FROM conversation_members WHERE conversation_id = ?
                                            )
                                        """, conversation_id)
        }

        # updating user's last seen message for that conversation
        database.execute("""
                         UPDATE conversation_members SET last_seen_message_id =
                         (
                            SELECT id FROM messages WHERE conversation_id = ? ORDER BY date DESC LIMIT 1
                         )
                         WHERE user_id = ? AND conversation_id = ?
                         """, conversation_id, session["user_id"], conversation_id)

        return render_template("conversations.html", conversation_info=conversation_info, user_id=session["user_id"], authorization=authorization)

    message = request.form.get("message")
    if not message :
        return render_template("conversations.html", error_message=f"Error : Must enter message")

    # storing the message in the messages table in the database
    database.execute("INSERT INTO messages (content, type, sender_id, conversation_id) VALUES(?, 'message', ?, ?)", message, session["user_id"], conversation_id)

    return redirect(f'/conversations/{conversation_id}')


@app.route("/conversations/groups/new", methods=["GET", "POST"])
def new_group() :
    # checking if there is a user logged in
    if not check_login_status() :
        return redirect("/login")

    if request.method == "GET" :
        return render_template("new_group.html")

    group_name = request.form.get("group_name")
    if not group_name :
        return render_template("new_group.html", error_message=f"Error: Group name is empty")

    # add the group to the conversations table in the database
    database.execute("INSERT INTO conversations (type, name) VALUES('group', ?)", group_name)

    # getting the group id in the database
    group_id = database.execute("SELECT id FROM conversations WHERE name = ? ORDER BY date_created DESC LIMIT 1", group_name)[0]["id"]

    # Add the user to that group by linking them together in the conversation members table
    database.execute("INSERT INTO conversation_members (conversation_id, user_id) VALUES(?, ?)", group_id, session["user_id"])

    return redirect(f'/')

@app.route("/conversations/groups/<int:group_id>/members/add", methods=["GET", "POST"])
def add_group_member(group_id) :

    # checking if there is a user logged in
    if not check_login_status() :
        return redirect("/login")

    if request.method == "GET" :
        return render_template("add_group_member.html", group_id=group_id)

    # checking authorization (i.e if the user is in the group and if the group_id is indeed that of a group)

    authorization = database.execute("""
                                    SELECT * FROM conversations JOIN conversation_members ON conversations.id = conversation_members.conversation_id
                                    WHERE user_id = ? AND conversation_id = ?
                                    """, session["user_id"], group_id)
    if not authorization :
        return render_template("add_group_member.html", error_message="Error : Unauthorized. Try again!", group_id=group_id)

    # getting the name of the member that the user wants to add
    member_username = request.form.get("member_username")
    if not member_username :
        return render_template("add_group_member.html", error_message="Error : Must have new member's username", group_id=group_id)

    # checking if the member username exists in the database
    member_id = database.execute("SELECT * FROM users WHERE username = ?", member_username)
    if not member_id :
        return render_template("add_group_member.html", error_message="Error : member not found", group_id=group_id)
    member_id = member_id[0]["id"]

    # checking if the member id is the same as the user id i.e user cannot add himself
    if member_id == session["user_id"] :
        return render_template("add_group_member.html", error_message="Error : member cannot be yourself", group_id=group_id)

    # checking if user is already in the group
    is_in_group = database.execute("SELECT id FROM conversation_members WHERE conversation_id = ? AND user_id = ?", group_id, member_id)
    if is_in_group :
        return render_template("add_group_member.html", error_message=f"Error : member is already in the group", group_id=group_id)

    # adding the new member to the group by linking in the conversation_members table in the database
    database.execute("INSERT INTO conversation_members (conversation_id, user_id) VALUES(?, ?)", group_id, member_id)

    return redirect(f"/")
