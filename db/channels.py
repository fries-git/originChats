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
    # Ensure the channels directory exists
    os.makedirs(channels_db_dir, exist_ok=True)
    
    # Load existing channel data or create a new one
    try:
        with open(f"{channels_db_dir}/{channel_name}.json", 'r') as f:
            channel_data = json.load(f)
    except FileNotFoundError:
        channel_data = []

    # Append the new message
    channel_data.append(message)

    # Save the updated channel data with compact formatting
    with open(f"{channels_db_dir}/{channel_name}.json", 'w') as f:
        json.dump(channel_data, f, separators=(',', ':'), ensure_ascii=False)

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
            permissions = channel.get("permissions", {})
            view_roles = permissions.get("view", [])
            if any(role in view_roles for role in roles):
                channels.append(channel)
    except FileNotFoundError:
        return []
    return channels

def edit_channel_message(channel_name, message_id, new_content):
    """
    Edit a message in a specific channel.

    Args:
        channel_name (str): The name of the channel.
        message_id (str): The ID of the message to edit.
        new_content (str): The new content for the message.

    Returns:
        bool: True if the message was edited successfully, False otherwise.
    """
    try:
        with open(f"{channels_db_dir}/{channel_name}.json", 'r') as f:
            channel_data = json.load(f)

        for msg in channel_data:
            if msg.get("id") == message_id:
                msg["content"] = new_content
                break
        else:
            return False  # Message not found

        # Ensure the channels directory exists
        os.makedirs(channels_db_dir, exist_ok=True)
        
        with open(f"{channels_db_dir}/{channel_name}.json", 'w') as f:
            json.dump(channel_data, f, separators=(',', ':'), ensure_ascii=False)

        return True
    except FileNotFoundError:
        return False

def get_channel_message(channel_name, message_id):
    """
    Retrieve a specific message from a channel by its ID.

    Args:
        channel_name (str): The name of the channel.
        message_id (str): The ID of the message to retrieve.

    Returns:
        dict: The message if found, None otherwise.
    """
    try:
        with open(f"{channels_db_dir}/{channel_name}.json", 'r') as f:
            channel_data = json.load(f)

        for msg in channel_data:
            if msg.get("id") == message_id:
                return msg
        return None  # Message not found
    except FileNotFoundError:
        return None  # Channel not found
    
def does_user_have_permission(channel_name, user_roles, permission_type):
    """
    Check if a user with specific roles has permission to perform an action on a channel.

    Args:
        channel_name (str): The name of the channel.
        user_roles (list): A list of roles assigned to the user.
        permission_type (str): The type of permission to check (e.g., "view", "edit").

    Returns:
        bool: True if the user has the required permission, False otherwise.
    """
    try:
        with open(channels_index, 'r') as f:
            channels_data = json.load(f)

        for channel in channels_data:
            if channel.get("name") == channel_name:
                permissions = channel.get("permissions", {})
                allowed_roles = permissions.get(permission_type, [])
                return any(role in allowed_roles for role in user_roles)
    except FileNotFoundError:
        return False  # Channel index not found

    return False  # Channel not found
    
def delete_channel_message(channel_name, message_id):
    """
    Delete a message from a specific channel.

    Args:
        channel_name (str): The name of the channel.
        message_id (str): The ID of the message to delete.

    Returns:
        bool: True if the message was deleted successfully, False otherwise.
    """
    try:
        with open(f"{channels_db_dir}/{channel_name}.json", 'r') as f:
            channel_data = json.load(f)

        new_data = [msg for msg in channel_data if msg.get("id") != message_id]

        # Ensure the channels directory exists
        os.makedirs(channels_db_dir, exist_ok=True)
        
        with open(f"{channels_db_dir}/{channel_name}.json", 'w') as f:
            json.dump(new_data, f, separators=(',', ':'), ensure_ascii=False)

        return True
    except FileNotFoundError:
        return False