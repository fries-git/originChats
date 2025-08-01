# Command: users_list

**Request:**
```json
{"cmd": "users_list"}
```

**Response:**
- On success:
```json
{
  "cmd": "users_list",
  "users": [ ...array of user objects... ]
}
```
- On error: see [common errors](errors.md).

**Notes:**
- User must be authenticated.

See implementation: [`handlers/message.py`](../handlers/message.py) (search for `case "users_list":`).
