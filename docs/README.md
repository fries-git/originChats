# OriginChats Server API Documentation

This documentation is for developers building custom clients for OriginChats. Each page covers a server command, its expected request/response format, and authentication details. All references link directly to the relevant code in [`handlers/message.py`](../handlers/message.py).

## Commands

- [Authentication](commands/auth.md)
- [Ping](commands/ping.md)
- [Send Message](commands/message_new.md)
- [Edit Message](commands/message_edit.md)
- [Delete Message](commands/message_delete.md)
- [Get Messages](commands/messages_get.md)
- [Get Single Message](commands/message_get.md)
- [Get Replies](commands/message_replies.md)
- [Get Channels](commands/channels_get.md)
- [List Users](commands/users_list.md)
- [List Online Users](commands/users_online.md)
- [List Plugins](commands/plugins_list.md)
- [Reload Plugins](commands/plugins_reload.md)
- [Rate Limit Status](commands/rate_limit_status.md)
- [Rate Limit Reset](commands/rate_limit_reset.md)

## Data Structures

- [Channel Object](data/channels.md)
- [Message Object](data/messages.md)

## Other

- [Permissions](data/permissions.md)
- [Roles](data/roles.md)