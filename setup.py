import os, json, sys

# OriginChats Setup Script
print("[OriginChats Setup] Starting OriginChats server configuration...")

def get_input(prompt, default=None):
    """Get user input with optional default value"""
    if default:
        user_input = input(f"{prompt} [{default}]: ").strip()
        return user_input if user_input else default
    return input(f"{prompt}: ").strip()

def yes_no(prompt, default="y"):
    """Get yes/no input from user"""
    while True:
        response = input(f"{prompt} [{default}]: ").strip().lower()
        if not response:
            response = default
        if response in ["y", "yes", "true", "1"]:
            return True
        elif response in ["n", "no", "false", "0"]:
            return False
        print("Please enter y/n")

def setup_directories():
    """Create necessary directories if they don't exist"""
    directories = ["db", "db/backup"]
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"[OriginChats Setup] Created directory: {directory}")

def create_default_files():
    """Create default database files"""
    # Default users.json
    users_file = "db/users.json"
    if not os.path.exists(users_file):
        default_users = {}
        with open(users_file, "w") as f:
            json.dump(default_users, f, indent=4)
        print(f"[OriginChats Setup] Created {users_file}")
    
    # Default channels.json
    channels_file = "db/channels.json"
    if not os.path.exists(channels_file):
        default_channels = [
            {
                "type": "text",
                "name": "general",
                "description": "General chat channel for everyone",
                "permissions": {
                    "view": ["user"],
                    "send": ["user"],
                    "delete": ["admin", "moderator"]
                }
            }
        ]
        with open(channels_file, "w") as f:
            json.dump(default_channels, f, indent=4)
        print(f"[OriginChats Setup] Created {channels_file}")
    
    # Default roles.json
    roles_file = "db/roles.json"
    if not os.path.exists(roles_file):
        default_roles = {
            "owner": {
                "description": "Server owner with ultimate permissions.",
                "color": "#9400D3"
            },
            "admin": {
                "description": "Administrator role with full permissions.",
                "color": "#FF0000"
            },
            "moderator": {
                "description": "Moderator role with elevated permissions.",
                "color": "#FFFF00"
            },
            "user": {
                "description": "Regular user role with standard permissions.",
                "color": "#FFFFFF"
            }
        }
        with open(roles_file, "w") as f:
            json.dump(default_roles, f, indent=4)
        print(f"[OriginChats Setup] Created {roles_file}")

def main():
    """Main setup function"""
    print()
    print("=" * 50)
    print("        OriginChats Server Setup")
    print("=" * 50)
    print()
    
    # Check if config already exists
    config_exists = os.path.exists("config.json")
    if config_exists:
        if not yes_no("Config file already exists. Overwrite?", "n"):
            print("[OriginChats Setup] Setup cancelled")
            return
    
    print("Let's configure your OriginChats server...")
    print()
    
    # Server configuration
    print("--- Server Configuration ---")
    server_name = get_input("Server name", "My OriginChats Server")
    server_icon = get_input("Server icon URL (optional)")
    server_url = get_input("Server URL (optional)")
    owner_name = get_input("Server owner name", "Admin")
    
    print()
    print("--- WebSocket Configuration ---")
    ws_host = get_input("WebSocket host", "127.0.0.1")
    ws_port = get_input("WebSocket port", "5613")
    
    try:
        ws_port = int(ws_port)
    except ValueError:
        print("[OriginChats Setup] Invalid port number, using default 5613")
        ws_port = 5613
    
    print()
    print("--- Rotur Integration ---")
    print("Rotur is used for user authentication")
    rotur_url = get_input("Rotur validation URL", "https://social.rotur.dev/validate")
    rotur_key = get_input("Rotur validation key", "your_key_here")
    
    print()
    print("--- Content Limits ---")
    max_message_length = get_input("Maximum message length", "2000")
    
    try:
        max_message_length = int(max_message_length)
    except ValueError:
        print("[OriginChats Setup] Invalid length, using default 2000")
        max_message_length = 2000
    
    # Create config structure
    config = {
        "limits": {
            "post_content": max_message_length
        },
        "rate_limiting": {
            "enabled": True,
            "messages_per_minute": 60,
            "burst_limit": 10,
            "cooldown_seconds": 30
        },
        "DB": {
            "channels": "db/channels.json",
            "users": {
                "file": "db/users.json", 
                "default": {
                    "roles": ["user"]
                }
            }
        },
        "websocket": {
            "host": ws_host,
            "port": ws_port
        },
        "rotur": {
            "validate_url": rotur_url,
            "validate_key": rotur_key
        },
        "service": {
            "name": "OriginChats",
            "version": "1.0.0"
        },
        "server": {
            "name": server_name,
            "owner": {
                "name": owner_name
            }
        }
    }
    
    # Add optional fields if provided
    if server_icon:
        config["server"]["icon"] = server_icon
    if server_url:
        config["server"]["url"] = server_url
    
    # Create directories and files
    print()
    print("--- Setting up directories and files ---")
    setup_directories()
    create_default_files()
    
    # Write config file
    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)
    
    print()
    print("=" * 50)
    print("[OriginChats Setup] Configuration complete!")
    print()
    print("Your server is configured with:")
    print(f"  Server Name: {server_name}")
    print(f"  WebSocket: {ws_host}:{ws_port}")
    print(f"  Owner: {owner_name}")
    print()
    print("To start your server, run:")
    print("  python init.py")
    print()
    print("Make sure to:")
    print("1. Configure your Rotur validation key properly")
    print("2. Set up any firewall rules for your WebSocket port")
    print("3. Configure SSL/TLS if running in production")
    print("=" * 50)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print("[OriginChats Setup] Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"[OriginChats Setup] Error during setup: {str(e)}")
        sys.exit(1)
