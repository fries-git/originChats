# Command: plugins_list

**Request:**
```json
{"cmd": "plugins_list"}
```

**Response:**
- On success:
```json
{
  "cmd": "plugins_list",
  "plugins": [ ...array of plugin names... ]
}
```
- On error: see [common errors](errors.md).

**Notes:**
- User must be authenticated and have the `owner` role.

See implementation: [`handlers/message.py`](../handlers/message.py) (search for `case "plugins_list":`).
