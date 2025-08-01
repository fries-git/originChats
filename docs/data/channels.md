# Channel Object Structure

A channel object represents a chat channel. Example structure:

```json
{
  "type": "text",
  "name": "general",
  "description": "General chat channel for everyone",
  "permissions": {
    "view": ["user"],
    "send": ["user"],
    "delete": ["admin", "moderator"],
    "delete_own": ["user"],
    "edit_own": ["user"]
  }
}
```

- `type`: Channel type (e.g., `text`).
- `name`: Channel name (string).
- `description`: Description of the channel.
- `permissions`: Object with arrays of roles for each action (`view`, `send`, `delete`, `delete_own`, `edit_own`).
  - `delete_own`: (optional) Roles allowed to delete their own messages. If not present, all roles can delete their own messages by default.
  - `edit_own`: (optional) Roles allowed to edit their own messages. If not present, all roles can edit their own messages by default.

**Permissions:** See [permissions documentation](../permissions.md) for details on how permissions work.

Returned by: [channels_get](../commands/channels_get.md)
