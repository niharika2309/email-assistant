# Email Assistant

An LLM-powered email assistant that drafts polished replies to incoming emails. Instead of asking a model to "write a reply" in one shot, it runs a **multi-step agent pipeline** — understanding the email, planning the response, drafting, self-reviewing for accuracy, and revising when needed.

Model, endpoint, and credentials are configured entirely through a `.env` file (works with any OpenAI-compatible API).

## Design

```
email-assistant/
├── .env                    # endpoint, api key, model (never committed)
├── main.py                 # entry point — runs the pipeline on a sample email
└── assistant/
    ├── __init__.py         # public exports
    ├── config.py           # loads .env, exposes BASE_URL / API_KEY / MODEL
    ├── llm_client.py       # builds the OpenAI-compatible client
    ├── prompts.py          # all system prompts + user-prompt templates
    └── agent.py            # the pipeline: understand → plan → draft → review → revise
```

### Separation of concerns

| Module | Responsibility |
|---|---|
| `config.py` | Loads `.env` once; single source of truth for `MODEL`, `BASE_URL`, `API_KEY` |
| `llm_client.py` | Only place that touches the OpenAI SDK |
| `prompts.py` | Every prompt in one file — tune behavior without touching logic |
| `agent.py` | Pipeline steps + the `email_agent()` orchestrator |
| `main.py` | Demo / entry point |

### Pipeline

```
Incoming email + user context
        │
        ▼
┌─────────────────────┐
│ 1. understand_email │  What is being asked? Is a reply required?
└─────────┬───────────┘  What must the reply include?
          ▼
┌─────────────────────┐
│   2. plan_response  │  What should the reply communicate,
└─────────┬───────────┘  using ONLY the user-provided facts?
          ▼
┌─────────────────────┐
│    3. draft_reply   │  Polite, clear, concise reply
└─────────┬───────────┘
          ▼
┌─────────────────────┐      starts with "NEEDS_REVISION"?
│    4. review_reply  │ ─────────────────────────────┐
└─────────┬───────────┘                              │
          │ APPROVED                                 ▼
          │                              ┌──────────────────┐
          │                              │  5. revise_reply │
          │                              └────────┬─────────┘
          ◄───────────────────────────────────────┘
          ▼
     Final email
```

### Why multiple steps?

Each step has a focused system prompt with guardrails, which is far more reliable than a single mega-prompt:

- **Understand** analyzes before generating — it never drafts ("Do not draft the reply yet").
- **Plan** locks the reply to user-provided facts ("Never invent facts or commitments"), so the model can't hallucinate a delivery date.
- **Draft** only writes what the plan approved.
- **Review** acts as a separate critic checking: does it answer the request, is it professional, does it contain **unsupported information**? It must answer `APPROVED` or `NEEDS_REVISION`.
- **Revise** runs *only if* the reviewer rejects the draft, preserving all facts.

## Functioning

### Setup

```bash
python3 -m venv .venv
.venv/bin/pip install openai python-dotenv

# configure the model (any OpenAI-compatible endpoint works)
cat > .env <<'EOF'
OPENAI_BASE_URL=http://your-endpoint:8888/v1
OPENAI_API_KEY=***
MODEL=Qwen3.8-Flash-Next
EOF
```

### Run

```bash
.venv/bin/python main.py
```

### Use as a library

```python
from assistant import email_agent

final_email = email_agent(
    email="Can we reschedule Monday's review to Wednesday?",
    user_context="Wednesday before 2pm works. Monday is not possible.",
)
print(final_email)
```

Individual steps are exported too (`understand_email`, `plan_response`, `draft_reply`, `review_reply`, `revise_reply`) if you want to inspect or intervene between stages.

## Example

**Incoming email:**

> Hi,
>
> I wanted to check whether you've completed
> the project report. We need it before Friday's meeting.
>
> Thanks!

**User context** (the only facts the assistant may use):

> The project report is not complete yet.
> I expect to finish it by Thursday afternoon.

**Output:**

```
Step 1: Understanding email...
Step 2: Planning response...
Step 3: Drafting reply...
Step 4: Reviewing reply...

Final email:
Hi,

Thank you for the reminder. The project report is not yet complete, but I expect to finish it by Thursday afternoon. It will be ready before Friday’s meeting.

Best regards,
[Your Name]
```

**What happened under the hood:**

1. **Understanding** — identified the ask (status of the report), that a reply is required, and that it must include status + expected completion time.
2. **Plan** — reply should acknowledge the request, admit the report isn't done, commit only to "Thursday afternoon" (from user context), and reassure it lands before Friday's meeting.
3. **Draft** — wrote the short, polite reply using only those points.
4. **Review** — returned `APPROVED.` (every claim traces back to the email or user context), so no revision step ran.

Notice the draft commits to *Thursday afternoon* — exactly what the user said — and never claims the report is finished. That's the "never invent facts" guardrails in the plan/draft/review prompts doing their job.

## Extending

- **Change the model**: edit `MODEL` in `.env` — no code changes.
- **Tune tone/behavior**: edit prompts in `assistant/prompts.py` only.
- **Add a stage** (e.g., tone adjustment, translation): add a prompt to `prompts.py` and a function in `agent.py`, then wire it into `email_agent()`.
