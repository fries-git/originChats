# Command: message_delete

**Request:**

```json
{
  "cmd": "message_delete",
  "id": "<message_id>",
  "channel": "<channel_name>"
}
```

- `id`: ID of the message to delete.
- `channel`: Channel name.

**Response:**

- On success:

```json
{
  "cmd": "message_delete",
  "id": "<message_id>",
  "channel": "<channel_name>",
  "global": true
}
```

- On error: see [common errors](errors.md).

**Notes:**

- User must be authenticated.
- Only the original sender or users with delete permission can delete messages.
- Rate limiting is enforced.

See implementation: [`handlers/message.py`](../handlers/message.py) (search for `case "message_delete":`).
