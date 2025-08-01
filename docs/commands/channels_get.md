# Command: channels_get

**Request:**

```json
{
  "cmd": "channels_get"
}
```

- No additional parameters required.

**Response:**

- On success:

```json
{
  "cmd": "channels_get",
  "val": [
    {
      "name": "<channel_name>",
      "type": "<channel_type>",
      "permissions": { ... }
      // other channel fields, e.g., description
    },
    // ...more channels
  ]
}
```

- On error: see [common errors](../errors.md).

**Notes:**

- User must be authenticated.
- Only channels viewable by the user's roles are returned.
- Rate limiting is enforced.

See implementation: [`handlers/message.py`](../../handlers/message.py) (search for `case "channels_get":`).
