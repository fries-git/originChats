# Roles Structure

Roles define user capabilities and permissions in OriginChats. Each user can have one or more roles, such as `user`, `admin`, `moderator`, or `owner`.

Example role object:

```json
{
  "name": "moderator",
  "color": "#00aaff",
  "description": "Moderators can manage messages and users."
}
```

- `name`: Role name (string).
- `color`: Hex color code for UI display.
- `description`: Description of the role.

Roles are referenced in permissions and user objects. See also: [permissions](permissions.md)
