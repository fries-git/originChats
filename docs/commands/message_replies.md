# Command: message_replies

**Request:**
```json
{
  "cmd": "message_replies",
  "channel": "<channel_name>",
  "id": "<message_id>",
  "limit": <optional_limit>
}
```

- `channel`: Channel name.
- `id`: Message ID.
- `limit`: (Optional) Number of replies to fetch (default 50).

**Response:**
- On success:
```json
{
  "cmd": "message_replies",
  "channel": "<channel_name>",
  "message_id": "<message_id>",
  "replies": [ ...array of message objects... ]
}
```
- On error: see [common errors](errors.md).

**Notes:**
- User must be authenticated and have access to the channel.

See implementation: [`handlers/message.py`](../handlers/message.py) (search for `case "message_replies":`).
