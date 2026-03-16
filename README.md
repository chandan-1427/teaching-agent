# ai-teaching-agent

`ai-teaching-agent` is a Bindu agent that turns a topic into a structured learning package. The implementation uses LangGraph to run a small teaching team: one agent builds the core explanation first, then three agents generate a roadmap, resource list, and practice workbook in parallel, and a final compiler step assembles the response into Markdown.

## What the codebase does

The runtime in `ai_teaching_agent/main.py` defines a four-step workflow:

1. `professor_node` creates a topic knowledge base.
2. `parallel_team_node` runs three concurrent sub-agents:
   - Academic Advisor
   - Research Librarian
   - Teaching Assistant
3. `compiler_node` combines all outputs into a single Markdown document.
4. `handler` lazily initializes the graph once and serves requests through Bindu.

Prompt instructions for the sub-agents live in [ai_teaching_agent/skills/skills.md](/d:/bindu-work/demo-agents/agent-1/ai-teaching-agent/ai_teaching_agent/skills/skills.md).

## Stack

- Python 3.12
- [Bindu](https://github.com/getbindu/bindu) for agent hosting
- LangGraph for orchestration
- LangChain OpenAI client pointed at OpenRouter
- `python-dotenv` for environment loading

## Requirements

- Python `>=3.12,<3.13`
- [uv](https://github.com/astral-sh/uv)
- `OPENROUTER_API_KEY`

Optional environment variables supported by the code:

- `MODEL_NAME` to override the default model (`anthropic/claude-3-haiku`)

Note: `docker-compose.yml` and the `Makefile` still include some template-era variables such as `MEM0_API_KEY`, but the current application code does not use them.

## Installation

```bash
uv sync
```

If you want the development tooling too:

```bash
uv sync --dev
```

Create a `.env` file with at least:

```env
OPENROUTER_API_KEY=your-key
MODEL_NAME=anthropic/claude-3-haiku
```

## Run locally

```bash
uv run python -m ai_teaching_agent
```

The agent config in [ai_teaching_agent/agent_config.json](/d:/bindu-work/demo-agents/agent-1/ai-teaching-agent/ai_teaching_agent/agent_config.json) exposes the service on `http://0.0.0.0:3773`.

You can also use the Make target:

```bash
make run
```

## Request shape

The Bindu handler expects a message list and uses the last message's `content` as the topic:

```python
[
    {"role": "user", "content": "Python for Data Science"}
]
```

If the content is empty or whitespace, the agent falls back to `"General Learning"`. Inputs are trimmed to 500 characters before execution.

## Output

The compiler returns Markdown with these sections:

- `Knowledge Base`
- `Learning Roadmap`
- `Resource Library`
- `Practice Workbook`

## Docker

Build and run with Docker Compose:

```bash
docker compose up --build
```

Or use the provided image build file directly:

```bash
docker build -f Dockerfile.agent -t ai_teaching_agent:latest .
docker run --rm -p 3773:3773 --env-file .env ai_teaching_agent:latest
```

## Development

Common commands from [Makefile](/d:/bindu-work/demo-agents/agent-1/ai-teaching-agent/Makefile):

- `make format`
- `make lint`
- `make test`
- `make test-cov`
- `make docs`

## Tests

The test suite in [tests/test_main.py](/d:/bindu-work/demo-agents/agent-1/ai-teaching-agent/tests/test_main.py) covers:

- handler success and fallback behavior
- one-time async initialization
- missing API key failure
- parallel error handling
- compiler output integrity

Run it with:

```bash
uv run pytest
```

## Project layout

```text
ai_teaching_agent/
|-- ai_teaching_agent/
|   |-- agent_config.json
|   |-- main.py
|   `-- skills/
|       `-- skills.md
|-- tests/
|   `-- test_main.py
|-- Dockerfile.agent
|-- docker-compose.yml
|-- Makefile
`-- pyproject.toml
```

## Known gaps

- The repository contains some scaffold leftovers in metadata and helper files, so package versions and exported symbols are not fully consistent across files.
- The README previously referenced features such as Mem0-backed tooling and richer API examples, but those are not implemented in the current runtime.

## License

MIT. See [LICENSE](/d:/bindu-work/demo-agents/agent-1/ai-teaching-agent/LICENSE).
