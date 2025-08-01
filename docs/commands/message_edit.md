# Command: message_edit

**Request:**

```json
{
  "cmd": "message_edit",
  "id": "<message_id>",
  "channel": "<channel_name>",
  "content": "<new_content>"
}
```

- `id`: ID of the message to edit.
- `channel`: Channel name.
- `content`: New message content.

**Response:**

- On success:

```json
{
  "cmd": "message_edit",
  "id": "<message_id>",
  "content": "<new_content>",
  "channel": "<channel_name>",
  "global": true
}
```

- On error: see [common errors](errors.md).

**Notes:**

- User must be authenticated.
- Rate limiting is enforced.
- Only the original sender or users with permission can edit messages (see code for details).

See implementation: [`handlers/message.py`](../handlers/message.py) (search for `case "message_edit":`).
