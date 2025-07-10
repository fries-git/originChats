from db import channels, users, roles
import time
import uuid

def handle(ws, message, server_data=None):
    """
    Handle incoming messages from clients.
    This function should be called when a new message is received.
    
    Args:
        ws: WebSocket connection
        message: Message data from client
        server_data: Dict containing server state (connected_clients, etc.)
    """
    if True:
        # Process the message here
        print(f"[OriginChatsWS] Received message: {message}")

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
                user = getattr(ws, 'username', None)

                if not channel_name or not content or not user:
                    return {"cmd": "error", "val": "Invalid chat message format"}

                content = content.strip()
                if not content:
                    return {"cmd": "error", "val": "Message content cannot be empty"}

                user_roles = users.get_user_roles(user)
                if not user_roles:
                    return {"cmd": "error", "val": "User roles not found"}

                # Check if the user has permission to send messages in this channel
                if not channels.does_user_have_permission(channel_name, user_roles, "send"):
                    return {"cmd": "error", "val": "You do not have permission to send messages in this channel"}

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

                # Optionally broadcast to all clients
                return {"cmd": "message_new", "message": out_msg, "channel": channel_name, "global": True}
            case "message_edit":
                # Handle message edit
                message_id = message.get("id")
                channel_name = message.get("channel")
                new_content = message.get("content")

                if not message_id or not channel_name or not new_content:
                    return {"cmd": "error", "val": "Invalid message edit format"}

                if not channels.edit_channel_message(channel_name, message_id, new_content):
                    return {"cmd": "error", "val": "Failed to edit message"}
                return {"cmd": "message_edit", "id": message_id, "content": new_content, "channel": channel_name, "global": True}
            case "message_delete":
                # Handle message delete
                message_id = message.get("id")
                channel_name = message.get("channel")
                if not message_id or not channel_name:
                    return {"cmd": "error", "val": "Invalid message delete format"}

                # Check if the message exists and can be deleted
                message = channels.get_channel_message(channel_name, message_id)
                if not message:
                    return {"cmd": "error", "val": "Message not found or cannot be deleted"}
                
                user_roles = users.get_user_roles(getattr(ws, 'username', None))
                if not roles:
                    return {"cmd": "error", "val": "User roles not found"}
                
                username = getattr(ws, 'username', None)
                if not username:
                    return {"cmd": "error", "val": "User not authenticated"}
                
                if not message.get("user") == username:
                    # If the user is not the original sender, check if they have permission to delete
                    if not channels.does_user_have_permission(channel_name, roles, "delete_others"):
                        return {"cmd": "error", "val": "You do not have permission to delete this message"}

                if not channels.delete_channel_message(channel_name, message_id):
                    return {"cmd": "error", "val": "Failed to delete message"}
                return {"cmd": "message_delete", "id": message_id, "channel": channel_name, "global": True}
            case "channels_get":
                # Handle request for available channels
                username = getattr(ws, 'username', None)
                if not username:
                    return {"cmd": "error", "val": "User not authenticated"}
                    
                user_data = users.get_user(username)  # Ensure user exists
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

                username = getattr(ws, 'username', None)
                if not username:
                    return {"cmd": "error", "val": "User not authenticated"}

                user_data = users.get_user(username)
                if not user_data:
                    return {"cmd": "error", "val": "User not found"}

                # Check if user can see this channel
                allowed_channels = channels.get_all_channels_for_roles(user_data.get("roles", []))
                
                if channel_name not in [c["name"] for c in allowed_channels if c.get("type") == "text"]:
                    return {"cmd": "error", "val": "Access denied to this channel"}

                messages = channels.get_channel_messages(channel_name, limit)
                return {"cmd": "messages_get", "channel": channel_name, "messages": messages}
            case "users_list":
                # Handle request for all users list
                username = getattr(ws, 'username', None)
                if not username:
                    return {"cmd": "error", "val": "User not authenticated"}
                
                users_list = users.get_users()
                return {"cmd": "users_list", "users": users_list}
            case "users_online":
                # Handle request for online users list  
                username = getattr(ws, 'username', None)
                if not username:
                    return {"cmd": "error", "val": "User not authenticated"}
                
                if not server_data or "connected_clients" not in server_data:
                    return {"cmd": "error", "val": "Server data not available"}
                
                # Gather authenticated users' info efficiently
                online_users = []
                for client_ws in server_data["connected_clients"]:
                    if getattr(client_ws, "authenticated", False):
                        user_data = users.get_user(client_ws.username)
                        if not user_data:
                            continue
                        
                        # Get the color of the first role
                        user_roles = user_data.get("roles", [])
                        color = None
                        if user_roles:
                            first_role_name = user_roles[0]
                            first_role_data = roles.get_role(first_role_name)
                            if first_role_data:
                                color = first_role_data.get("color")
                        
                        online_users.append({
                            "username": client_ws.username,
                            "roles": user_data.get("roles"),
                            "color": color
                        })
                
                return {"cmd": "users_online", "users": online_users}
            case _:
                return {"cmd": "error", "val": f"Unknown command: {message.get('cmd')}"}
    # except Exception as e:
    #    print(f"[OriginChatsWS] Error handling message: {str(e)}")
    #    return {"cmd": "error", "val": f"Exception: {str(e)}"}