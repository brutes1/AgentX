# AgentX

A minimal local AI agent powered by [Apple Foundation Models](https://developer.apple.com/machine-learning/foundation-models/) via `fm serve`.

## Requirements

- macOS with `fm` installed and running (`fm serve`)
- Python 3.11+

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

Start the model server, then run the agent:

```bash
fm serve &
python agent.py
```

```
AgentX online (model: system). Type 'exit' to quit.

You: What is 123 * 456?
AgentX: 123 * 456 is 56,088.

You: exit
```

## Tools

| Tool | Description |
|------|-------------|
| `get_current_time` | Returns the current local date and time |
| `calculate` | Evaluates arithmetic expressions safely (no `eval`) |

## Models

The `fm serve` endpoint exposes two models:

- `system` — on-device Apple Foundation Model (~4K token context)
- `pcc` — Private Cloud Compute (larger context, recommended)

Change the model by editing `MODEL` in `agent.py`.

## Using with Hermes Agent

[Hermes Agent](https://github.com/NousResearch/hermes-agent) can be wired to `fm serve` as a drop-in OpenAI-compatible backend.

**`~/.hermes/config.yaml`**

```yaml
model:
  api_key: fm
  base_url: http://127.0.0.1:1976/v1
  default: pcc
  provider: fm

providers:
  fm:
    api: http://127.0.0.1:1976/v1
    default_model: pcc
    models:
      - system
      - pcc
    name: Apple Foundation Models

streaming:
  enabled: true

# Disable built-in toolsets — Apple models reject many Hermes tool schemas
platform_toolsets:
  cli: []
toolsets: []
```

Then run:

```bash
hermes --oneshot "What is 12 * 34?"
# → 12 * 34 = 408
```

> **Note:** The `system` model has a ~4K token context window — too small for Hermes's system prompt. Use `pcc` instead.
