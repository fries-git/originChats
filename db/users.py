import json, os

_MODULE_DIR = os.path.dirname(os.path.abspath(__file__))

users_index = os.path.join(_MODULE_DIR, "users.json")
config = json.load(open(os.path.join(_MODULE_DIR, "..", "config.json"), "r"))

def user_exists(user_id):
    """
    Check if a user exists in the users database.
    """
    try:
        with open(users_index, "r") as f:
            users = json.load(f)
        return user_id in users
    except FileNotFoundError:
        return False

def get_user(user_id):
    """
    Get user data by user ID.
    """
    try:
        with open(users_index, "r") as f:
            users = json.load(f)
        return users.get(user_id, None)
    except FileNotFoundError:
        return None

def add_user(user_id):
    """
    Add a new user to the users database.
    """
    try:
        with open(users_index, "r") as f:
            users = json.load(f)
    except FileNotFoundError:
        users = {}

    if user_id in users:
        return False  # User already exists

    users[user_id] = config["DB"]["users"]["default"].copy()

    with open(users_index, "w") as f:
        json.dump(users, f, indent=4)

    return True

def get_user_roles(user_id):
    """
    Get the roles of a user.
    """
    user = get_user(user_id)
    if user:
        return user.get("roles", [])
    return []