from datetime import datetime, timedelta


user = {
    "subscribed": None,
    "subscribed_data": None,
    "subscription_expires": None,
    "downloads": 30,
    "language": "ru",
}
users = dict()


dates = {
    'day': timedelta(days=1),
    'month': timedelta(days=30),
    'year': timedelta(days=365)
}


def get_or_create_user(user_id):
    user = users.get(user_id, None)
    if not user:
        users[user_id] = {
            "subscribed": None,
            "downloads": 30,
            "language": "ru"
        }

    return users[user_id]


def update_user_status(user_id, now_data, subscribed_data):
    users[user_id]["subscribed_data"] = now_data
    users[user_id]["subscription_expires"] = now_data + dates[subscribed_data]
    return users[user_id]


def user_subscribed(user_id):
    users[user_id]["subscribed"] = True
    return users[user_id]

now = datetime.now()
print(now.time())