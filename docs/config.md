# Configuration: config.json

This file contains the main configuration for the OriginChats server. Below is a description of each section and field:

---

## limits

- **post_content**: *(int)*
  - Maximum number of characters allowed in a single message/post.

## rate_limiting

- **enabled**: *(bool)*
  - Whether rate limiting is enabled for message sending.
- **messages_per_minute**: *(int)*
  - Maximum number of messages a user can send per minute.
- **burst_limit**: *(int)*
  - Maximum number of messages allowed in a short burst before cooldown is enforced.
- **cooldown_seconds**: *(int)*
  - Number of seconds a user must wait after hitting the burst limit.

## DB

- **channels**: *(str)*
  - Path to the channels database file.
- **users**: *(object)*
  - **file**: *(str)*
    - Path to the users database file.
  - **default**: *(object)*
    - **roles**: *(list of str)*
      - Default roles assigned to new users.

## websocket

- **host**: *(str)*
  - Host address for the websocket server.
- **port**: *(int)*
  - Port number for the websocket server.

## rotur

- **validate_url**: *(str)*
  - URL used for validating users via Rotur service.
- **validate_key**: *(str)*
  - API key for Rotur validation.

## service

- **name**: *(str)*
  - Name of the service.
- **version**: *(str)*
  - Version of the service.

## server

- **name**: *(str)*
  - Name of the server instance.
- **owner**: *(object)*
  - **name**: *(str)*
    - Name of the server owner.
- **icon**: *(str)*
  - URL to the server icon image.
- **url**: *(str)*
  - Public URL of the server.

---

**Location:** `config.json`

This file should be kept secure, especially fields containing API keys or sensitive URLs.
