import json, os

_MODULE_DIR = os.path.dirname(os.path.abspath(__file__))

channels_db_dir = os.path.join(_MODULE_DIR, "channels")
channels_index = os.path.join(_MODULE_DIR, "channels.json")

def get_channel_messages(channel_name, limit=100):
    """
    Retrieve messages from a specific channel.

    Args:
        channel_name (str): The name of the channel to retrieve messages from.
        limit (int): The maximum number of messages to retrieve.

    Returns:
        list: A list of messages from the specified channel.
    """
    # Load the channel data
    try:
        with open(f"{channels_db_dir}/{channel_name}.json", 'r') as f:
            channel_data = json.load(f)
    except FileNotFoundError:
        return []

    # Return the last 'limit' messages
    return channel_data[-limit:]

def save_channel_message(channel_name, message):
    """
    Save a message to a specific channel.

    Args:
        channel_name (str): The name of the channel to save the message to.
        message (dict): The message to save, should contain 'user', 'content', and 'timestamp'.

    Returns:
        bool: True if the message was saved successfully, False otherwise.
    """
    # Load existing channel data or create a new one
    try:
        with open(f"{channels_db_dir}/{channel_name}.json", 'r') as f:
            channel_data = json.load(f)
    except FileNotFoundError:
        channel_data = []

    # Append the new message
    channel_data.append(message)

    # Save the updated channel data
    with open(f"{channels_db_dir}/{channel_name}.json", 'w') as f:
        json.dump(channel_data, f, indent=4)

    return True

def get_all_channels_for_roles(roles):
    """
    Get all channels available for the specified roles.

    Args:
        roles (list): A list of roles to filter channels by.

    Returns:
        list: A list of channel info dicts available for the specified roles.
    """
    channels = []
    try:
        with open(channels_index, 'r') as f:
            all_channels = json.load(f)
        for channel in all_channels:
            if channel.get("type") != "text":
                continue
            permissions = channel.get("permissions", {})
            view_roles = permissions.get("view", [])
            if any(role in view_roles for role in roles):
                channels.append({
                    "name": channel.get("name"),
                    "description": channel.get("description"),
                    "wallpaper": channel.get("wallpaper")
                })
    except FileNotFoundError:
        return []
    return channels
