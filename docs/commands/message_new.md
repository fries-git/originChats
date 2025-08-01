# Command: message_new

**Request:**
```json
{
  "cmd": "message_new",
  "channel": "<channel_name>",
  "content": "<message_content>",
  "reply_to": "<optional_message_id>"
}
```

- `channel`: Name of the channel to send the message to.
- `content`: Message text (required, trimmed, max length enforced by config).
- `reply_to`: (Optional) ID of the message being replied to.

**Response:**
- On success:
```json
{
  "cmd": "message_new",
  "message": { ...message object... },
  "channel": "<channel_name>",
  "global": true
}
```
- On error: see [common errors](errors.md).

**Notes:**
- User must be authenticated and have permission to send in the channel.
- Rate limiting and message length are enforced.
- Replies include a `reply_to` field in the message object.

See implementation: [`handlers/message.py`](../handlers/message.py) (search for `case "message_new":`).
