import asyncio, json, websockets
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logger import Logger

async def send_to_client(ws, message):
    """Send a message to a specific client"""
    try:
        await ws.send(json.dumps(message))
        return True
    except websockets.exceptions.ConnectionClosed:
        Logger.warning("Connection closed when trying to send message")
        return False
    except Exception as e:
        Logger.error(f"Error sending message: {str(e)}")
        return False

async def heartbeat(ws, heartbeat_interval=30):
    """Send periodic pings to keep the connection alive"""
    try:
        while True:
            await asyncio.sleep(heartbeat_interval)
            if not await send_to_client(ws, {"cmd": "ping"}):
                break
    except asyncio.CancelledError:
        Logger.info("Heartbeat task cancelled")
    except Exception as e:
        Logger.error(f"Heartbeat error: {str(e)}")

async def broadcast_to_all(connected_clients, message):
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
        Logger.delete(f"Removed {len(disconnected)} disconnected clients")
    
    return disconnected

async def disconnect_user(connected_clients, username, reason="User disconnected"):
    """Disconnect a specific user by username"""
    disconnected = []
    clients_copy = connected_clients.copy()
    
    for ws in clients_copy:
        if hasattr(ws, 'username') and ws.username == username:
            try:
                await send_to_client(ws, {"cmd": "disconnect", "reason": reason})
                await ws.close()
                disconnected.append(ws)
                Logger.delete(f"Disconnected user {username}: {reason}")
            except Exception as e:
                Logger.error(f"Error disconnecting user {username}: {str(e)}")
                disconnected.append(ws)
    
    # Clean up disconnected clients
    for ws in disconnected:
        connected_clients.discard(ws)
    
    return len(disconnected)
