#!/bin/sh
set -e

cat > /root/.picoclaw/config.json << HEREDOC
{
  "agents": {
    "defaults": {
      "workspace": "~/.picoclaw/workspace",
      "restrict_to_workspace": false,
      "provider": "${PICOCLAW_PROVIDER:-}",
      "model": "${PICOCLAW_MODEL:-gemini-2.0-flash}",
      "max_tokens": ${PICOCLAW_MAX_TOKENS:-8192},
      "temperature": ${PICOCLAW_TEMPERATURE:-0.7},
      "max_tool_iterations": 20
    }
  },
  "providers": {
    "anthropic": {
      "api_key": "${ANTHROPIC_API_KEY:-}",
      "api_base": ""
    },
    "openrouter": {
      "api_key": "${OPENROUTER_API_KEY:-}",
      "api_base": ""
    }
  },
  "channels": {
    "telegram": {
      "enabled": ${TELEGRAM_ENABLED:-false},
      "token": "${TELEGRAM_BOT_TOKEN:-}",
      "allow_from": ["${TELEGRAM_ALLOW_FROM:-}"]
    }
  },
  "tools": {
    "web": {
      "duckduckgo": {
        "enabled": true,
        "max_results": 5
      }
    }
  },
  "heartbeat": {
    "enabled": false,
    "interval": 30
  },
  "gateway": {
    "host": "0.0.0.0",
    "port": ${GATEWAY_PORT:-18790}
  }
}
HEREDOC

# Copy scripts to workspace (volume is mounted at runtime, so copy here)
cp -n /opt/picoclaw-scripts/* /root/.picoclaw/workspace/ 2>/dev/null || true

exec picoclaw "$@"
