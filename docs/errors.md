# Common Errors

The server may respond with error objects for various reasons. All errors use the following format:

```json
{
  "cmd": "error",
  "val": "<error message>"
}
```

Below is a list of common error messages and what they mean. Refer to the [source code](../handlers/message.py) for exact logic.

---

## Error List

- **User not authenticated**
  - The user is not logged in or the WebSocket session is missing a username.
- **Invalid message format: expected a dictionary, got ...**
  - The client sent a message that is not a JSON object.
- **Invalid chat message format**
  - Required fields are missing in a `message_new` request.
- **Message content cannot be empty**
  - The message text is empty or only whitespace.
- **Message too long. Maximum length is ... characters**
  - The message exceeds the configured length limit.
- **Rate limited**
  - The user is sending messages too quickly. (See also the `rate_limit` response.)
- **User roles not found**
  - The server could not find any roles for the user.
- **You do not have permission to send messages in this channel**
  - The user's roles do not allow sending messages in the specified channel.
- **The message you're trying to reply to was not found**
  - The `reply_to` message ID does not exist in the channel.
- **Failed to edit message**
  - The message could not be edited (may not exist or user lacks permission).
- **Invalid message edit format**
  - Required fields are missing in a `message_edit` request.
- **Message not found or cannot be edited**
  - The message does not exist or cannot be edited (e.g., not found or permission denied).
- **You do not have permission to edit your own message in this channel**
  - The user's roles do not allow editing their own messages in this channel.
- **You do not have permission to edit this message**
  - The user tried to edit someone else's message and does not have permission.
- **Message not found or cannot be deleted**
  - The message does not exist or cannot be deleted.
- **You do not have permission to delete your own message in this channel**
  - The user's roles do not allow deleting their own messages in this channel.
- **You do not have permission to delete this message**
  - The user is not the sender and lacks delete permission.
- **Invalid message delete format**
  - Required fields are missing in a `message_delete` request.
- **Invalid channel name**
  - The channel name is missing or invalid.
- **User not found**
  - The user does not exist in the database.
- **Access denied to this channel**
  - The user does not have permission to view the channel.
- **Message not found**
  - The requested message ID does not exist in the channel.
- **Channel name and message ID are required**
  - Required fields are missing in a `message_get` or `message_replies` request.
- **Plugin manager not available**
  - The plugin manager is not loaded or available in the server state.
- **Access denied: owner role required**
  - The command requires the `owner` role.
- **Failed to reload plugin '...'**
  - The named plugin could not be reloaded.
- **Rate limiter not available or disabled**
  - The rate limiter is not enabled in the server state.
- **Access denied: can only check your own rate limit status**
  - Only the user or an owner can check rate limit status for a user.
- **User parameter is required**
  - The `user` field is missing in a request that requires it.
- **Unknown command: ...**
  - The `cmd` field is missing or not recognized by the server.

---

For more details, see [`handlers/message.py`](../handlers/message.py).
