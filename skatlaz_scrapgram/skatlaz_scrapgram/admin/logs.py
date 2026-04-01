import datetime

_logs = []

def add_log(action, user=None, extra=None):
    _logs.append({
        "time": str(datetime.datetime.utcnow()),
        "action": action,
        "user": user,
        "extra": extra
    })

def get_logs():
    return _logs

def clear_logs():
    _logs.clear()
