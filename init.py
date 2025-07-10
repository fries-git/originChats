import asyncio
from server import OriginChatsServer

async def main():
    """Main function to start the OriginChats server"""
    server = OriginChatsServer()
    await server.start_server()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("[OriginChatsWS] Server stopped by user")
    except Exception as e:
        print(f"[OriginChatsWS] Server error: {str(e)}")
