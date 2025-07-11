
# this plugin will be accessible to any user with any of the following roles
# "owner" is the highest level of access, allowing full control over the server
# "admin" role is also allowed for administrative commands
required_permission = ["owner", "admin"]


import os, json
from db import channels, users

def getInfo():
    """Get information about the plugin"""
    info = {
       "name": "CLI Plugin",
        "description": "A command line interface for OriginChats that lets you manage your server, channels, and users from the chat with commands.",
        "handles": [
            "new_message"
        ]
    }
    return info

def send_message_to_channel(channel, content, server_data):
    """Send a message to a channel through the server's broadcast system"""
    import asyncio
    import time
    import uuid
    
    # Create a message object similar to how regular messages are created
    out_msg = {
        "user": "OriginChats",
        "content": content.strip(),
        "timestamp": time.time(),
        "type": "message",
        "pinned": False,
        "id": str(uuid.uuid4())
    }
    
    # Save to channel
    channels.save_channel_message(channel, out_msg)
    
    # Broadcast the message if we have server data
    if server_data and "connected_clients" in server_data:
        message = {"cmd": "message_new", "message": out_msg, "channel": channel, "global": True}
        # We need to schedule this to run in the event loop
        from handlers.websocket_utils import broadcast_to_all
        loop = asyncio.get_event_loop()
        loop.create_task(broadcast_to_all(server_data["connected_clients"], message))

def on_new_message(ws, message_data, server_data=None):
    """Handle new chat messages"""
    
    if not ws or not hasattr(ws, 'authenticated') or not ws.authenticated:
        print(f"[CLI Plugin] Authentication check failed: ws={ws}, authenticated={getattr(ws, 'authenticated', False)}")
        return

    username = getattr(ws, 'username', None)
    user_roles = users.get_user_roles(username)
    
    if not user_roles:
        print("[CLI Plugin] No user roles found")
        return

    if not any(role in user_roles for role in required_permission):
        print(f"[CLI Plugin] User lacks required permissions")
        return

    content = message_data.get("content", "").strip()
    channel = message_data.get("channel", "general")
    parts = content.split(" ")
    
    if content.startswith("!server "):
        match parts[1]:
            case "ban":
                if len(parts) < 3:
                    send_message_to_channel(channel, "Usage: !server ban <username>", server_data)
                    return
                username_to_ban = parts[2]
                if users.ban_user(username_to_ban):
                    # Disconnect the banned user if they're online
                    if server_data and "connected_clients" in server_data:
                        import asyncio
                        from handlers.websocket_utils import disconnect_user
                        loop = asyncio.get_event_loop()
                        loop.create_task(disconnect_user(
                            server_data["connected_clients"], 
                            username_to_ban, 
                            "You have been banned from this server"
                        ))
                    send_message_to_channel(channel, f"User {username_to_ban} has been banned.", server_data)
                else:
                    send_message_to_channel(channel, f"Failed to ban user {username_to_ban}.", server_data)
            case "unban":
                if len(parts) < 3:
                    send_message_to_channel(channel, "Usage: !server unban <username>", server_data)
                    return
                username = parts[2]
                if users.unban_user(username):
                    send_message_to_channel(channel, f"User {username} has been unbanned.", server_data)
                else:
                    send_message_to_channel(channel, f"Failed to unban user {username}.", server_data)
            case "list_banned":
                banned_users = users.get_banned_users()
                if banned_users:
                    send_message_to_channel(channel, "Banned users: " + ", ".join(banned_users), server_data)
                else:
                    send_message_to_channel(channel, "No users are currently banned.", server_data)
            case "list_users":
                user_list = users.get_users()
                if user_list:
                    user_info = [f"{user['username']} (Roles: {', '.join(user['roles'])})" for user in user_list]
                    send_message_to_channel(channel, "Users: " + ", ".join(user_info), server_data)
                else:
                    send_message_to_channel(channel, "No users found.", server_data)
            case "list_channels":
                channels_list = channels.get_channels()
                if channels_list:
                    channel_info = [f"{channel['name']} (Type: {channel['type']})" for channel in channels_list]
                    send_message_to_channel(channel, "Channels: " + ", ".join(channel_info), server_data)
                else:
                    send_message_to_channel(channel, "No channels found.", server_data)
            case "create_channel":
                if len(parts) < 4:
                    send_message_to_channel(channel, "Usage: !server create_channel <channel_name> <channel_type>", server_data)
                    return
                channel_name = parts[2]
                channel_type = parts[3].lower()
                if channel_type not in ["text", "separator"]:
                    send_message_to_channel(channel, "Invalid channel type. Use 'text' or 'separator'.", server_data)
                    return
                if channels.create_channel(channel_name, channel_type):
                    send_message_to_channel(channel, f"Channel '{channel_name}' of type '{channel_type}' created successfully.", server_data)
                else:
                    send_message_to_channel(channel, f"Failed to create channel '{channel_name}'. It may already exist.", server_data)
            case "delete_channel":
                if len(parts) < 3:
                    send_message_to_channel(channel, "Usage: !server delete_channel <channel_name>", server_data)
                    return
                channel_name = parts[2]
                if channels.delete_channel(channel_name):
                    send_message_to_channel(channel, f"Channel '{channel_name}' deleted successfully.", server_data)
                else:
                    send_message_to_channel(channel, f"Failed to delete channel '{channel_name}'. It may not exist.", server_data)
            case "reorder_channel":
                if len(parts) < 4:
                    send_message_to_channel(channel, "Usage: !server reorder_channel <channel_name> <new_position>", server_data)
                    return
                channel_name = parts[2]
                new_position = parts[3]
                if channels.reorder_channel(channel_name, new_position):
                    send_message_to_channel(channel, f"Channel '{channel_name}' reordered to position '{new_position}' successfully.", server_data)
                else:
                    send_message_to_channel(channel, f"Failed to reorder channel '{channel_name}'. It may not exist or the position is invalid.", server_data)
            case "get_channel":
                if len(parts) < 3:
                    send_message_to_channel(channel, "Usage: !server get_channel <channel_name>", server_data)
                    return
                channel_name = parts[2]
                channel_info = channels.get_channel(channel_name)
                if channel_info:
                    channel_details = f"Channel '{channel_info['name']}' (Type: {channel_info['type']})"
                    if "permissions" in channel_info:
                        permissions = ", ".join([f"{role}: {', '.join(perms)}" for role, perms in channel_info["permissions"].items()])
                        channel_details += f" | Permissions: {permissions}"
                    send_message_to_channel(channel, channel_details, server_data)
                else:
                    send_message_to_channel(channel, f"Channel '{channel_name}' not found.", server_data)
            case "add_channel_permission":
                if len(parts) < 4:
                    send_message_to_channel(channel, "Usage: !server add_channel_permissions <channel_name> <role> [permission]", server_data)
                    return
                channel_name = parts[2]
                role = parts[3]
                permission = parts[4] if len(parts) > 4 else None
                if channels.set_channel_permissions(channel_name, role, permission, True):
                    send_message_to_channel(channel, f"Permissions for role '{role}' on channel '{channel_name}' updated successfully.", server_data)
                else:
                    send_message_to_channel(channel, f"Failed to set permissions for role '{role}' on channel '{channel_name}'. Channel may not exist or role may not be valid.", server_data)
            case "rem_channel_permission":
                if len(parts) < 4:
                    send_message_to_channel(channel, "Usage: !server rem_channel_permissions <channel_name> <role> [permission]", server_data)
                    return
                channel_name = parts[2]
                role = parts[3]
                permission = parts[4] if len(parts) > 4 else None
                if channels.set_channel_permission(channel_name, role, permission, False):
                    send_message_to_channel(channel, f"Permissions for role '{role}' on channel '{channel_name}' removed successfully.", server_data)
                else:
                    send_message_to_channel(channel, f"Failed to remove permissions for role '{role}' on channel '{channel_name}'. Channel may not exist or role may not be valid.", server_data)
            case "get_channel_permissions":
                if len(parts) < 3:
                    send_message_to_channel(channel, "Usage: !server get_channel_permissions <channel_name>", server_data)
                    return
                channel_name = parts[2]
                permissions = channels.get_channel_permissions(channel_name)
                if permissions:
                    perm_info = [f"{role}: {', '.join(perms)}" for role, perms in permissions.items()]
                    send_message_to_channel(channel, f"Permissions for channel '{channel_name}': " + ", ".join(perm_info), server_data)
                else:
                    send_message_to_channel(channel, f"Failed to get permissions for channel '{channel_name}'. It may not exist.", server_data)
            case "create_role":
                if len(parts) < 3:
                    send_message_to_channel(channel, "Usage: !server create_role <role_name>", server_data)
                    return
                role_name = parts[2]
                if users.create_role(role_name):
                    send_message_to_channel(channel, f"Role '{role_name}' created successfully.", server_data)
                else:
                    send_message_to_channel(channel, f"Failed to create role '{role_name}'. It may already exist.", server_data)
            case "delete_role":
                if len(parts) < 3:
                    send_message_to_channel(channel, "Usage: !server delete_role <role_name>", server_data)
                    return
                role_name = parts[2]
                if users.delete_role(role_name):
                    send_message_to_channel(channel, f"Role '{role_name}' deleted successfully.", server_data)
                else:
                    send_message_to_channel(channel, f"Failed to delete role '{role_name}'. It may not exist.", server_data)
            case "give_role":
                if len(parts) < 4:
                    send_message_to_channel(channel, "Usage: !server give_role <username> <role_name>", server_data)
                    return
                username_to_give = parts[2]
                role_name = parts[3]
                if users.give_role(username_to_give, role_name):
                    send_message_to_channel(channel, f"Role '{role_name}' given to user '{username_to_give}' successfully.", server_data)
                else:
                    send_message_to_channel(channel, f"Failed to give role '{role_name}' to user '{username_to_give}'. User may not exist or role may not be valid.", server_data)
            case "remove_role":
                if len(parts) < 4:
                    send_message_to_channel(channel, "Usage: !server remove_role <username> <role_name>", server_data)
                    return
                username_to_remove = parts[2]
                role_name = parts[3]
                if users.remove_role(username_to_remove, role_name):
                    send_message_to_channel(channel, f"Role '{role_name}' removed from user '{username_to_remove}' successfully.", server_data)
                else:
                    send_message_to_channel(channel, f"Failed to remove role '{role_name}' from user '{username_to_remove}'. User may not exist or role may not be valid.", server_data)
            case "list_roles":
                roles = users.get_roles()
                if roles:
                    role_info = [f"{role_name} (Color: {role_data.get('color', 'default')})" for role_name, role_data in roles.items()]
                    send_message_to_channel(channel, "Roles: " + ", ".join(role_info), server_data)
                else:
                    send_message_to_channel(channel, "No roles found.", server_data)
            case "update_role_color":
                if len(parts) < 4:
                    send_message_to_channel(channel, "Usage: !server update_role_color <role_name> <new_color>", server_data)
                    return
                role_name = parts[2]
                new_color = parts[3]
                if users.update_role(role_name, {"color": new_color}):
                    send_message_to_channel(channel, f"Role '{role_name}' updated successfully with new color '{new_color}'.", server_data)
                else:
                    send_message_to_channel(channel, f"Failed to update role '{role_name}'. It may not exist.", server_data)
            case "message_purge":
                if len(parts) < 3 or not parts[2].isdigit():
                    send_message_to_channel(channel, "Usage: !server message_purge <number>", server_data)
                    return
                number = int(parts[2])
                if number <= 0:
                    send_message_to_channel(channel, "Number must be greater than 0.", server_data)
                    return
                if channels.purge_messages(channel, number):
                    send_message_to_channel(channel, f"Purged the last {number} messages from channel '{channel}'.", server_data)
                else:
                    send_message_to_channel(channel, f"Failed to purge messages from channel '{channel}'.", server_data)
            case "help":
                help_text = ""
                match parts[2] if len(parts) > 2 else None:
                    case "users":
                        help_text += (
                            "!server list_users - List all users\n"
                            "!server get_user_info <username> - Get information about a user\n"
                            "!server update_user_info <username> <info> - Update information about a user\n"
                        )
                    case "channels":
                        help_text += (
                            "!server list_channels - List all channels\n"
                            "!server create_channel <channel_name> <channel_type> - Create a new channel\n"
                            "!server delete_channel <channel_name> - Delete a channel\n"
                            "!server add_channel_permission <channel_name> <role> [permission] - Add permissions to a role for a channel\n"
                            "!server rem_channel_permission <channel_name> <role> [permission] - Remove permissions from a role for a channel\n"
                            "!server get_channel_permissions <channel_name> - Get permissions for a channel\n"
                            "!server reorder_channel <channel_name> <new_position> - Reorder a channel\n"
                            "!server get_channel <channel_name> - Get information about a channel\n"
                        )
                    case "roles":
                        help_text += (
                            "!server create_role <role_name> - Create a new role\n"
                            "!server delete_role <role_name> - Delete a role\n"
                            "!server give_role <username> <role_name> - Give a role to a user\n"
                            "!server remove_role <username> <role_name> - Remove a role from a user\n"
                            "!server list_roles - List all roles\n"
                            "!server update_role_color <role_name> <new_color> - Update the color of a role\n"
                        )
                    case "server":
                        help_text += (
                            "!server ban <username> - Ban a user from the server\n"
                            "!server unban <username> - Unban a user from the server\n"
                            "!server list_banned - List all banned users\n"
                        )
                    case "messages":
                        help_text += (
                            "!server message_purge number - Purge the last 'number' of messages from the current channel\n"
                        )
                    case None:
                        help_text += (
                            "!server help [users|channels|roles|server] - Show this help message or specific help for a section\n"
                        )

                send_message_to_channel(channel, help_text, server_data)
            case _:
                send_message_to_channel(channel, "Unknown command. Use !server help for a list of commands.", server_data)