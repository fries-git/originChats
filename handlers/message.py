from db import channels
import time
import uuid
from db import users

def handle(ws, message):
    """
    Handle incoming messages from clients.
    This function should be called when a new message is received.
    """
    try:
        # Process the message here
        print(f"[OriginChatsWS] Received message: {message}")
        print(f"[OriginChatsWS] Message type: {type(message)}")  # Debug: log the type

        if not isinstance(message, dict):
            return {"cmd": "error", "val": f"Invalid message format: expected a dictionary, got {type(message).__name__}"}

        match message.get("cmd"):
            case "ping":
                # Handle ping command
                return {"cmd": "pong", "val": "pong"}
            case "message_new":
                # Handle chat message
                channel_name = message.get("channel")
                content = message.get("content")
                user = ws.username

                if not channel_name or not content or not user:
                    return {"cmd": "error", "val": "Invalid chat message format"}

                # Save the message to the channel
                out_msg = {
                    "user": user,
                    "content": content,
                    "timestamp": time.time(),  # Use current timestamp
                    "type": "message",
                    "pinned": False,
                    "id": str(uuid.uuid4())
                }

                channels.save_channel_message(channel_name, out_msg)

                # Only acknowledge to sender; broadcasting is handled elsewhere
                return {"cmd": "ok", "val": "message received"}
            case "channels_get":
                # Handle request for available channels
                user_data = users.get_user(ws.username)  # Ensure user exists
                if not user_data:
                    return {"cmd": "error", "val": "User not found"}
                channels_list = channels.get_all_channels_for_roles(user_data.get("roles", []))
                return {"cmd": "channels_get", "val": channels_list}
            case "messages_get":
                # Handle request for channel messages
                channel_name = message.get("channel")
                limit = message.get("limit", 100)

                if not channel_name:
                    return {"cmd": "error", "val": "Invalid channel name"}

                user_data = users.get_user(ws.username)
                if not user_data:
                    return {"cmd": "error", "val": "User not found"}

                # Check if user can see this channel
                allowed_channels = channels.get_all_channels_for_roles(user_data.get("roles", []))
                
                if channel_name not in [c["name"] for c in allowed_channels if c.get("type") == "text"]:
                    return {"cmd": "error", "val": "Access denied to this channel"}

                messages = channels.get_channel_messages(channel_name, limit)
                return {"cmd": "messages_get", "channel": channel_name, "messages": messages}
            case _:
                return {"cmd": "error", "val": f"Unknown command: {message.get('cmd')}"}
    except Exception as e:
        print(f"[OriginChatsWS] Error handling message: {str(e)}")
        return {"cmd": "error", "val": f"Exception: {str(e)}"}