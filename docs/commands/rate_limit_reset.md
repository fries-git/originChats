# Command: rate_limit_reset

**Request:**
```json
{
  "cmd": "rate_limit_reset",
  "user": "<username>"
}
```

- `user`: Username whose rate limit should be reset.

**Response:**
- On success:
```json
{
  "cmd": "rate_limit_reset",
  "user": "<username>",
  "val": "Rate limit reset for user <username>"
}
```
- On error: see [common errors](errors.md).

**Notes:**
- User must be authenticated and have the `owner` role.

See implementation: [`handlers/message.py`](../handlers/message.py) (search for `case "rate_limit_reset":`).
