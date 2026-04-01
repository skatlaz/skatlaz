import time

users = {}

def is_spam(user):
    now = time.time()

    if user not in users:
        users[user] = []

    users[user].append(now)
    users[user] = [t for t in users[user] if now - t < 10]

    return len(users[user]) > 5
