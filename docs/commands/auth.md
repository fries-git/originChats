# Authentication

All commands require the user to be authenticated. Authentication is managed via the WebSocket connection using a validator token from the Rotur service. This process ensures that only verified users can interact with the server and its features.

---

## Step-by-Step Authentication Flow

1. **Handshake**
   - When a client connects, the server sends a handshake packet:

     ```json
     {
       "cmd": "handshake",
       "val": {
         "server": { ... },
         "limits": { ... },
         "version": "1.1.0",
         "validator_key": "originChats-<key>"
       }
     }
     ```

   - The client uses `validator_key` to request a validator from Rotur:

     ```txt
     https://social.rotur.dev/generate_validator?key=<validator_key>&auth=<roturToken>
     ```

2. **Client Authentication**
   - After receiving the validator from Rotur, the client sends:

     ```json
     {
       "cmd": "auth",
       "validator": "<validator_token>"
     }
     ```

3. **Server Response**
   - On success, the server replies:

     ```json
     { "cmd": "auth_success", "val": "Authentication successful" }
     ```

     and then:

     ```json
     {
       "cmd": "ready",
       "user": { ...user object... }
     }
     ```

   - On failure:

     ```json
     { "cmd": "auth_error", "val": "<reason>" }
     ```

4. **User Connection Broadcast**
   - When a user connects, all clients receive:

     ```json
     {
       "cmd": "user_connect",
       "user": {
         "username": "<username>",
         "roles": [ ... ],
         "color": "#RRGGBB"
       }
     }
     ```

---

## Error Handling

If a command is sent without authentication, the server responds with:

```json
{"cmd": "error", "val": "User not authenticated"}
```

---

## Permissions and Roles

User roles are checked for permissions on various commands. Roles are retrieved using:

```python
users.get_user_roles(username)
```

Some commands require specific roles (e.g., `owner`). See role checks in [`handlers/message.py`](../../handlers/message.py) (search for `get_user_roles`).

---

## Related Protocol

For more details on the handshake, error packets, and other protocol-level messages, see the [protocol documentation](../protocol.md).
