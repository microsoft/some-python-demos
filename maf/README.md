# maf

[Microsoft Agent Framework](https://learn.microsoft.com/en-us/agent-framework/overview/?pivots=programming-language-python) demo with a FastAPI `/chat` endpoint.

The agent has a `read_tickets` tool that queries the helpdesk tickets API from the `fastapi/` demo in this repo.

## requirements

- uv -- <https://docs.astral.sh/uv/getting-started/installation/>
- task -- <https://taskfile.dev/docs/installation>
- Azure CLI logged in (`az login`)
- The `fastapi/` demo running on port 8000

## Setup

```bash
cp .env.example .env
# Edit .env with your Azure AI Foundry project endpoint
uv sync
```

## Environment variables

| Variable                       | Description                                    | Default                  |
|--------------------------------|------------------------------------------------|--------------------------|
| `AZURE_OPENAI_ENDPOINT`        | Azure OpenAI endpoint (required)               |                          |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | Azure OpenAI deployment name                   | `gpt-4o`                 |
| `TICKETS_API_BASE`             | Base URL for the FastAPI tickets demo           | `http://localhost:8000`  |

## Quickstart

Start the fastapi tickets demo first (from the `fastapi/` directory):

```bash
task run
```

Then in a separate terminal, start this demo (from the `maf/` directory):

```bash
task run
```

Send a chat message:

```bash
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What tickets are in the system?"}'
```

Continue a conversation by passing back the `session_id`:

```bash
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Which ones are high priority?", "session_id": "<session_id from previous response>"}'
```

See Taskfile for all the common operations, like `task check` and `task run`.
