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

- `system` — on-device Apple Foundation Model (default)
- `pcc` — Private Cloud Compute

Change the model by editing `MODEL` in `agent.py`.
