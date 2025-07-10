# OriginChats Server Architecture

## Project Structure

```
originChats/
├── init.py                 # Main entry point (simplified)
├── server.py              # Server class with core logic
├── setup.py               # Server setup script
├── config.json           # Configuration file
├── watchers.py           # File system watchers
├── db/                   # Database modules
│   ├── channels.py
│   ├── users.py
│   ├── roles.py
│   └── *.json           # Data files
└── handlers/             # Request handlers
    ├── auth.py          # Authentication logic
    ├── message.py       # Message handling
    ├── websocket_utils.py # WebSocket utilities
    └── rotur.py         # Rotur integration
```

## Modules Overview

### `init.py`
- **Purpose**: Entry point for the application
- **Responsibilities**: 
  - Initialize and start the server
  - Handle graceful shutdown
- **Dependencies**: `server.py`

### `server.py` 
- **Purpose**: Core server class
- **Responsibilities**:
  - WebSocket connection management
  - Client lifecycle handling
  - Configuration management
  - File watcher coordination
- **Dependencies**: `handlers/`, `watchers.py`

### `handlers/auth.py`
- **Purpose**: Authentication handling
- **Responsibilities**:
  - Rotur validation
  - User creation and login
  - Authentication state management
  - User connection broadcasts
- **Dependencies**: `db/users.py`, `db/roles.py`, `websocket_utils.py`

### `handlers/websocket_utils.py`
- **Purpose**: WebSocket utility functions
- **Responsibilities**:
  - Client communication (send/receive)
  - Heartbeat management
  - Broadcasting to multiple clients
  - Connection cleanup
- **Dependencies**: `asyncio`, `websockets`

### `handlers/message.py`
- **Purpose**: Message processing and routing
- **Responsibilities**:
  - Command parsing and validation
  - Message handling (CRUD operations)
  - User/channel management commands
  - Response formatting
- **Dependencies**: `db/`, `handlers/websocket_utils.py`

## Key Improvements

### 1. **Separation of Concerns**
- Authentication logic isolated in `auth.py`
- WebSocket utilities separated from business logic
- Server lifecycle management in dedicated class

### 2. **Modularity**
- Each module has a single, clear responsibility
- Dependencies are explicit and minimal
- Easy to test individual components

### 3. **Maintainability**
- Clean import structure
- Consistent error handling
- Clear function signatures and documentation

### 4. **Extensibility**
- Server class can be easily extended
- New handlers can be added without modifying core logic
- Configuration-driven behavior

## Usage

### Starting the Server
```bash
python init.py
```

### Setting Up the Server
```bash
python setup.py
```

### Configuration
The server uses `config.json` for all configuration. Key sections:
- `websocket`: Host and port settings
- `rotur`: Authentication service configuration
- `server`: Server metadata
- `DB`: Database file locations

## Error Handling

Each module implements appropriate error handling:
- WebSocket connection errors are logged and handled gracefully
- Authentication failures are communicated to clients
- Database errors are caught and reported
- Server startup errors are logged with context

## Development Guidelines

1. **Adding New Features**: Create new handlers in the `handlers/` directory
2. **Database Changes**: Modify the appropriate module in `db/`
3. **WebSocket Changes**: Update `websocket_utils.py` for utility functions
4. **Authentication Changes**: Modify `auth.py`
5. **Server Configuration**: Update the `OriginChatsServer` class in `server.py`
