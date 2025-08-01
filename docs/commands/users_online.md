# Command: users_online

**Request:**
```json
{"cmd": "users_online"}
```

**Response:**
- On success:
```json
{
  "cmd": "users_online",
  "users": [ ...array of user objects... ]
}
```
- On error: see [common errors](errors.md).

**Notes:**
- User must be authenticated.
- Returns all currently connected and authenticated users, including their roles and role color.

See implementation: [`handlers/message.py`](../handlers/message.py) (search for `case "users_online":`).
