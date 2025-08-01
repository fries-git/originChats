# Authentication

All commands require the user to be authenticated. Authentication is managed via the WebSocket connection. The server expects the `ws` object to have a `username` attribute set for all authenticated users. If a command is sent without authentication, the server responds with an error:

```json
{"cmd": "error", "val": "User not authenticated"}
```

See authentication checks in [`handlers/message.py`](../handlers/message.py) (search for `getattr(ws, 'username', None)`).

User roles are also checked for permissions. Roles are retrieved using `users.get_user_roles(username)`. Some commands require specific roles (e.g., `owner`).

See role checks in [`handlers/message.py`](../handlers/message.py) (search for `get_user_roles`).
