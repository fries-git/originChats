import asyncio, websockets, json, os
from handlers.websocket_utils import send_to_client, heartbeat, broadcast_to_all
from handlers.auth import handle_authentication
from handlers import message as message_handler
from handlers.rate_limiter import RateLimiter
import watchers
from plugin_manager import PluginManager

class OriginChatsServer:
    """OriginChats WebSocket server"""
    
    def __init__(self, config_path="config.json"):
        # Load configuration
        with open(os.path.join(os.path.dirname(__file__), config_path), "r") as f:
            self.config = json.load(f)
        
        # Server state
        self.connected_clients = set()
        self.version = self.config["service"]["version"]
        self.heartbeat_interval = 30
        self.main_event_loop = None
        self.file_observer = None
        
        # Initialize rate limiter if enabled
        rate_config = self.config.get("rate_limiting", {})
        if rate_config.get("enabled", False):
            self.rate_limiter = RateLimiter(
                messages_per_minute=rate_config.get("messages_per_minute", 30),
                burst_limit=rate_config.get("burst_limit", 5),
                cooldown_seconds=rate_config.get("cooldown_seconds", 60)
            )
        else:
            self.rate_limiter = None
        
        # Initialize plugin manager
        self.plugin_manager = PluginManager()
        
        print(f"[OriginChatsWS] OriginChats WebSocket Server v{self.version} initialized")
        if self.rate_limiter:
            print(f"[OriginChatsWS] Rate limiting enabled: {rate_config.get('messages_per_minute', 30)} msg/min, burst: {rate_config.get('burst_limit', 5)}")
        else:
            print(f"[OriginChatsWS] Rate limiting disabled")
    
    async def handle_client(self, websocket):
        """WebSocket connection handler"""
        # Get client info
        headers = websocket.request.headers
        client_ip = headers.get('CF-Connecting-IP') or headers.get('X-Forwarded-For') or websocket.remote_address[0]
        print(f"[OriginChatsWS] New connection from {client_ip}")
        
        # Add to connected clients
        self.connected_clients.add(websocket)
        print(f"[OriginChatsWS] Total connected clients: {len(self.connected_clients)}")
        
        # Start heartbeat task
        heartbeat_task = asyncio.create_task(heartbeat(websocket, self.heartbeat_interval))
        
        try:
            # Send handshake message
            await send_to_client(websocket, {
                "cmd": "handshake",
                "val": {
                    "server": self.config["server"],
                    "version": "1.1.0",
                    "validator_key": "originChats-" + self.config["rotur"]["validate_key"]
                }
            })
                
            # Keep connection open and handle client messages
            async for message in websocket:
                try:
                    data = json.loads(message)
                    
                    # Handle authentication
                    if data.get("cmd") == "auth" and not getattr(websocket, "authenticated", False):
                        await handle_authentication(
                            websocket, data, self.config, 
                            self.connected_clients, client_ip
                        )
                        continue

                    # Require authentication for other commands
                    if not getattr(websocket, "authenticated", False):
                        await send_to_client(websocket, {"cmd": "auth_error", "val": "Authentication required"})
                        continue

                    # Create server data object for message handler
                    server_data = {
                        "connected_clients": self.connected_clients,
                        "config": self.config,
                        "plugin_manager": self.plugin_manager,
                        "rate_limiter": self.rate_limiter
                    }
                    
                    # Handle message
                    response = message_handler.handle(websocket, data, server_data)
                    if not response:
                        print(f"[OriginChatsWS] No response for message: {data}")
                        continue
                    
                    if response.get("global", False):
                        # Broadcast to all clients if global flag is set
                        await broadcast_to_all(self.connected_clients, response)
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
            if websocket in self.connected_clients:
                self.connected_clients.remove(websocket)
                print(f"[OriginChatsWS] Client {client_ip} removed. {len(self.connected_clients)} clients remaining")
                
                if getattr(websocket, "authenticated", False):
                    await broadcast_to_all(self.connected_clients, {
                        "cmd": "user_disconnect",
                        "username": websocket.username
                    })
    
    async def broadcast_wrapper(self, message):
        """Wrapper for broadcast_to_all to maintain compatibility with watchers"""
        await broadcast_to_all(self.connected_clients, message)
    
    async def start_server(self):
        """Start the WebSocket server"""
        # Store the main event loop for use in other threads
        self.main_event_loop = asyncio.get_event_loop()

        # Setup file watchers for users.json and channels.json
        self.file_observer = watchers.setup_file_watchers(self.broadcast_wrapper, self.main_event_loop)

        # Get port from config or use default
        port = self.config.get("websocket", {}).get("port", 5613)
        host = self.config.get("websocket", {}).get("host", "127.0.0.1")
        
        print(f"[OriginChatsWS] Starting WebSocket server on {host}:{port}")
        
        try:
            async with websockets.serve(self.handle_client, host, port, ping_interval=None):
                print(f"[OriginChatsWS] WebSocket server running at ws://{host}:{port}")
                
                # Keep the server running
                await asyncio.Future()
        finally:
            # Stop file watcher when server stops
            if self.file_observer:
                self.file_observer.stop()
                self.file_observer.join()
                print("[OriginChatsWS] File watcher stopped")
