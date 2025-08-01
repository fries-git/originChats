# Command: ping

**Request:**
```
{"cmd": "ping"}
```

**Response:**
```
{"cmd": "pong", "val": "pong"}
```

No authentication required for this command.

See implementation: [`handlers/message.py`](../handlers/message.py) (search for `case "ping":`).
