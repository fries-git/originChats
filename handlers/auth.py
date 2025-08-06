import requests
from db import users, roles
from handlers.websocket_utils import send_to_client, broadcast_to_all
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logger import Logger

async def handle_authentication(websocket, data, config_data, connected_clients, client_ip, server_data=None):
    """Handle user authentication"""
    url = config_data["rotur"]["validate_url"]
    key = "originChats-" + config_data["rotur"]["validate_key"]
    validator = data.get("validator")
    
    # Validate with rotur service
    response = requests.get(url, params={"key": key, "v": validator}, timeout=5)
    if response.status_code != 200 or response.json().get("valid") != True:
        await send_to_client(websocket, {"cmd": "auth_error", "val": "Invalid authentication"})
        Logger.error(f"Client {client_ip} failed authentication")
        return False

    # Set authentication state
    websocket.authenticated = True
    websocket.username = validator.split(",")[0].lower()  # Extract username from validator

    # Check if user is banned
    if users.is_user_banned(websocket.username):
        await send_to_client(websocket, {"cmd": "auth_error", "val": "Access denied: You are banned from this server"})
        Logger.warning(f"Banned user {websocket.username} attempted to connect from {client_ip}")
        websocket.authenticated = False
        return False

    # Create user if doesn't exist
    if not users.user_exists(websocket.username):
        users.add_user(websocket.username)
        Logger.add(f"User {websocket.username} created")

    # Send success message
    await send_to_client(websocket, {"cmd": "auth_success", "val": "Authentication successful"})
    
    # Get user data and send ready packet
    user = users.get_user(websocket.username)
    if not user:
        await send_to_client(websocket, {"cmd": "auth_error", "val": "User not found"})
        Logger.error(f"User {websocket.username} not found after authentication")
        return False

    user["username"] = websocket.username
    await send_to_client(websocket, {
        "cmd": "ready",
        "user": user
    })
    
    # Get the color of the first role for user_connect broadcast
    user_roles = user.get("roles", [])
    color = None
    if user_roles:
        first_role_name = user_roles[0]
        first_role_data = roles.get_role(first_role_name)
        if first_role_data:
            color = first_role_data.get("color")
    
    # Broadcast user connection to all clients
    await broadcast_to_all(connected_clients, {
        "cmd": "user_connect",
        "user": {
            "username": websocket.username,
            "roles": user.get("roles"),
            "color": color
        }
    })
    
    # Trigger user_connect event for plugins
    if server_data and "plugin_manager" in server_data:
        server_data["plugin_manager"].trigger_event("user_connect", websocket, {
            "username": websocket.username,
            "roles": user.get("roles"),
            "color": color,
            "user": user
        }, server_data)
    
    Logger.success(f"Client {client_ip} authenticated")
    return True
