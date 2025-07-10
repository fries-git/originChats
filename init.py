import asyncio, websockets, json, os, requests
from db import channels, users, roles
from handlers import message as message_handler
import watchers

config = open(os.path.join(os.path.dirname(__file__), "config.json"), "r")
config_data = json.load(config)
config.close()

# OriginChats WebSocket server configuration
connected_clients = set()
VERSION = config_data["service"]["version"]
HEARTBEAT_INTERVAL = 30  # seconds

# Store the main event loop for reference from other threads
main_event_loop = None

# Helper functions for WebSocket communications
async def send_to_client(ws, message):
    """Send a message to a specific client"""
    try:
        await ws.send(json.dumps(message))
        return True
    except websockets.exceptions.ConnectionClosed:
        print(f"[OriginChatsWS] Connection closed when trying to send message")
        return False
    except Exception as e:
        print(f"[OriginChatsWS] Error sending message: {str(e)}")
        return False

async def heartbeat(ws):
    """Send periodic pings to keep the connection alive"""
    try:
        while True:
            await asyncio.sleep(HEARTBEAT_INTERVAL)
            if not await send_to_client(ws, {"cmd": "ping"}):
                break
    except asyncio.CancelledError:
        print(f"[OriginChatsWS] Heartbeat task cancelled")
    except Exception as e:
        print(f"[OriginChatsWS] Heartbeat error: {str(e)}")

async def broadcast_to_all(message):
    """Broadcast a message to all connected clients"""
    disconnected = set()
    # Create a copy of the set to avoid "Set changed size during iteration" error
    clients_copy = connected_clients.copy()
    for ws in clients_copy:
        success = await send_to_client(ws, message)
        if not success:
            disconnected.add(ws)
    
    # Clean up disconnected clients
    for ws in disconnected:
        connected_clients.discard(ws)  # Use discard instead of remove to avoid KeyError
    
    if disconnected:
        print(f"[OriginChatsWS] Removed {len(disconnected)} disconnected clients")

# Main WebSocket handler
async def handler(websocket):
    """WebSocket connection handler"""
    # Get client info
    headers = websocket.request.headers
    client_ip = headers.get('CF-Connecting-IP') or headers.get('X-Forwarded-For') or websocket.remote_address[0]
    print(f"[OriginChatsWS] New connection from {client_ip}")
    
    # Add to connected clients
    connected_clients.add(websocket)
    print(f"[OriginChatsWS] Total connected clients: {len(connected_clients)}")
    
    # Start heartbeat task
    heartbeat_task = asyncio.create_task(heartbeat(websocket))
    
    try:
        # Send handshake message
        await send_to_client(websocket, {
            "cmd": "handshake",
            "val": {
                "server": config_data["server"],
                "version": VERSION,
                "validator_key": "originChats-" + config_data["rotur"]["validate_key"]
            }
        })
            
        # Keep connection open and handle client messages
        async for message in websocket:
            try:
                data = json.loads(message)
                if data.get("cmd") == "auth" and not getattr(websocket, "authenticated", False):
                    url = config_data["rotur"]["validate_url"]
                    key = "originChats-" + config_data["rotur"]["validate_key"]
                    validator = data.get("validator")
                    response = requests.get(url, params={"key": key, "v": validator}, timeout=5)
                    if response.status_code != 200 or response.json().get("valid") != True:
                        await send_to_client(websocket, {"cmd": "auth_error", "val": "Invalid authentication"})
                        print(f"[OriginChatsWS] Client {client_ip} failed authentication")
                        continue

                    websocket.authenticated = True
                    websocket.username = validator.split(",")[0].lower()  # Extract username from validator

                    if not users.user_exists(websocket.username):
                        users.add_user(websocket.username)
                        print(f"[OriginChatsWS] User {websocket.username} created")

                    await send_to_client(websocket, {"cmd": "auth_success", "val": "Authentication successful"})
                    # Gather authenticated users' info efficiently
                    online_users = []
                    for ws in connected_clients:
                        if getattr(ws, "authenticated", False):
                            user_data = users.get_user(ws.username)
                            if ws.username == websocket.username:
                                continue
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
                                "username": ws.username,
                                "roles": user_data.get("roles"),
                                "color": color
                            })
                    await send_to_client(websocket, {
                        "cmd": "users_online",
                        "users": online_users
                    })
                    # send down all the users and their colours
                    await send_to_client(websocket, {
                        "cmd": "users_list",
                        "users": users.get_users()
                    })

                    user = users.get_user(websocket.username)
                    if not user:
                        await send_to_client(websocket, {"cmd": "auth_error", "val": "User not found"})
                        print(f"[OriginChatsWS] User {websocket.username} not found after authentication")
                        continue

                    user["username"] = websocket.username
                    await send_to_client(websocket, {
                        "cmd": "ready",
                        "user": user
                    })
                    # Get the color of the first role
                    user_roles = user.get("roles", [])
                    color = None
                    if user_roles:
                        first_role_name = user_roles[0]
                        first_role_data = roles.get_role(first_role_name)
                        if first_role_data:
                            color = first_role_data.get("color")
                    
                    await broadcast_to_all({
                        "cmd": "user_connect",
                        "user": {
                            "username": websocket.username,
                            "roles": user.get("roles"),
                            "color": color
                        }
                    })
                    print(f"[OriginChatsWS] Client {client_ip} authenticated")
                    continue

                if not getattr(websocket, "authenticated", False):
                    await send_to_client(websocket, {"cmd": "auth_error", "val": "Authentication required"})
                    continue

                response = message_handler.handle(websocket, data)
                if not response:
                    print(f"[OriginChatsWS] No response for message: {data}")
                    continue
                if response.get("global", False):
                    # Broadcast to all clients if global flag is set
                    await broadcast_to_all(response)
                    continue
                if response:
                    await send_to_client(websocket, response)

            except json.JSONDecodeError:
                print(f"[OriginChatsWS] Received invalid JSON: {message[:50]}...")
            except Exception as e:
                print(f"[OriginChatsWS] Error processing message: {str(e)}")
    except websockets.exceptions.ConnectionClosed:
        print(f"[OriginChatsWS] Connection closed by {client_ip}")
    except Exception as e:
        print(f"[OriginChatsWS] Error handling connection: {str(e)}")
    finally:
        # Clean up
        heartbeat_task.cancel()
        if websocket in connected_clients:
            connected_clients.remove(websocket)
            print(f"[OriginChatsWS] Client {client_ip} removed. {len(connected_clients)} clients remaining")
            if getattr(websocket, "authenticated", False):
                await broadcast_to_all({
                    "cmd": "user_disconnect",
                    "username": websocket.username
                })

# Start the WebSocket server
async def main():
    global posts_buffer
    global main_event_loop
    
    # Store the main event loop for use in other threads
    main_event_loop = asyncio.get_event_loop()

    # Setup file watchers for users.json and channels.json
    file_observer = watchers.setup_file_watchers(broadcast_to_all, main_event_loop)

    # Create the WebSocket server
    port = 5613
    print(f"[OriginChatsWS] Starting WebSocket server on port {port}")
    
    try:
        async with websockets.serve(handler, "127.0.0.1", port, ping_interval=None):
            print(f"[OriginChatsWS] WebSocket server running at ws://127.0.0.1:{port}")
            
            # Keep the server running
            await asyncio.Future()
    finally:
        # Stop file watcher when server stops
        file_observer.stop()
        file_observer.join()
        print("[OriginChatsWS] File watcher stopped")

if __name__ == "__main__":
    print(f"[OriginChatsWS] OriginChats WebSocket Server v{VERSION} starting...")
    asyncio.run(main())
