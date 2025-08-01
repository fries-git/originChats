# OriginChats: Additional Protocol & Client Setup Documentation

This page documents protocol details and server packets not covered elsewhere, useful for client developers.

---

## Handshake Packet

When a client connects, the server sends a handshake packet before authentication:

```json
{
  "cmd": "handshake",
  "val": {
    "server": { ... },        // Server info from config.json
    "limits": { ... },        // Message/content limits
    "version": "1.1.0",     // Server version
    "validator_key": "originChats-<key>" // Used for Rotur validation
  }
}
```

- The client should use this to display server info and prepare for authentication.

---

## Authentication Flow

1. **Client sends:** `{ "cmd": "auth", "validator": "<token>" }`
2. **Server responds:**
   - On success: `{ "cmd": "auth_success", "val": "Authentication successful" }`
   - On failure: `{ "cmd": "auth_error", "val": "<reason>" }`
   - On success, also: `{ "cmd": "ready", "user": { ...user object... } }`

---

## User Connection Broadcast

When a user connects, all clients receive:

```json
{
  "cmd": "user_connect",
  "user": {
    "username": "<username>",
    "roles": [ ... ],
    "color": "#RRGGBB" // Color of user's primary role, if set
  }
}
```

---

## Heartbeat

The server sends periodic pings to keep the connection alive:

```json
{ "cmd": "ping" }
```

Clients do not need to respond, but should keep the connection open.

---

## Error Packets

All errors are sent as:

```json
{ "cmd": "error", "val": "<error message>" }
```

---

## Rate Limiting

If a user is rate limited, the server responds:

```json
{ "cmd": "rate_limit", "length": <milliseconds> }
```

- The client should wait the specified time before retrying.

---

## General Notes

- All packets have a `cmd` field indicating the command type.
- Most responses include a `val` or other data field.
- See also the [commands documentation](./commands/) for all supported commands.

---

**For more details, see:**

- [`handlers/message.py`](../handlers/message.py)
- [`handlers/auth.py`](../handlers/auth.py)
- [`server.py`](../server.py)
- [`handlers/websocket_utils.py`](../handlers/websocket_utils.py)
