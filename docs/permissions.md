# Permissions Structure

Permissions in OriginChats are defined per channel and per action. Each action (such as `view`, `send`, `delete`, `delete_own`, `edit_own`) is mapped to an array of roles allowed to perform it.

Example:

```json
{
  "view": ["user"],
  "send": ["user"],
  "delete": ["admin", "moderator"],
  "delete_own": ["user"],
  "edit_own": ["user"]
}
```

- `view`: Roles that can see the channel.
- `send`: Roles that can send messages.
- `delete`: Roles that can delete any message.
- `delete_own`: Roles that can delete their own messages. If omitted, all roles can delete their own messages by default.
- `edit_own`: Roles that can edit their own messages. If omitted, all roles can edit their own messages by default.

If a role is not listed for an action, users with that role cannot perform the action (except for `delete_own` and `edit_own` as noted above).

See also: [roles](roles.md), [channel object](channels.md)
