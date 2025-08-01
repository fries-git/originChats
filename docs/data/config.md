# Config Structure

The server configuration (`config.json`) controls global settings, limits, and features for OriginChats.

Example config snippet:

```json
{
  "limits": {
    "post_content": 2000,
    "channels": 100
  },
  "features": {
    "rate_limiting": true
  }
}
```

- `limits`: Object with various server limits (e.g., message length, channel count).
- `features`: Object with feature flags (e.g., rate limiting).

See your server's `config.json` for all available options.
