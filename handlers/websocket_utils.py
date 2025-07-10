import asyncio, json, websockets

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

async def heartbeat(ws, heartbeat_interval=30):
    """Send periodic pings to keep the connection alive"""
    try:
        while True:
            await asyncio.sleep(heartbeat_interval)
            if not await send_to_client(ws, {"cmd": "ping"}):
                break
    except asyncio.CancelledError:
        print(f"[OriginChatsWS] Heartbeat task cancelled")
    except Exception as e:
        print(f"[OriginChatsWS] Heartbeat error: {str(e)}")

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
        print(f"[OriginChatsWS] Removed {len(disconnected)} disconnected clients")
    
    return disconnected
