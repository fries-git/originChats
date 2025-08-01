# Command: rate_limit_status

**Request:**
```json
{
  "cmd": "rate_limit_status",
  "user": "<optional_username>"
}
```

- `user`: (Optional) Username to check. Users can check their own status; only `owner` can check others.

**Response:**
- On success:
```json
{
  "cmd": "rate_limit_status",
  "user": "<username>",
  "status": { ...rate limit info... }
}
```
- On error: see [common errors](errors.md).

**Notes:**
- User must be authenticated.
- Only `owner` can check other users' status.

See implementation: [`handlers/message.py`](../handlers/message.py) (search for `case "rate_limit_status":`).
