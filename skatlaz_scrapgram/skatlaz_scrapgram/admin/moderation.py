from skatlaz_scrapgram.models import messages

banned_users = set()

def ban_user(username):
    banned_users.add(username)

def unban_user(username):
    banned_users.discard(username)

def is_banned(username):
    return username in banned_users

def delete_message(msg_id):
    global messages
    messages[:] = [m for m in messages if m.get("id") != msg_id]
