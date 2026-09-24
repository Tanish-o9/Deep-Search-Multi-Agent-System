# Deep Research Agent

A multi-agent deep research pipeline built with the **OpenAI Agents SDK**, running entirely on **local models via Ollama** with **free web search via DuckDuckGo** — no paid API calls anywhere in the stack.

Give it a research question. It plans the searches, runs them in parallel, writes a full report, and emails it out.

---

## Architecture

Four agents, orchestrated by plain Python code rather than handoffs — each step is a separate `Runner.run()` call, which keeps the flow explicit and every agent's contract clear.

| # | Agent | Role | Output |
|---|-------|------|--------|
| 1 | **Planner Agent** | Turns one query into a set of targeted search terms, each with a stated reason | Structured output (`WebSearchPlan`) |
| 2 | **Search Agent** | Runs a web search and condenses results into a short summary | Plain text summary |
| 3 | **Writer Agent** | Synthesizes all search summaries into a long-form markdown report | Structured output (`ReportData`) |
| 4 | **Email Agent** | Converts the report to clean HTML and sends it via SMTP | Tool call (`send_email_tool`) |

**Flow:**

```
query
  → Planner Agent        → N search terms
  → Search Agent × N     → run concurrently with asyncio.gather
  → Writer Agent         → markdown report + summary + follow-up questions
  → Email Agent          → HTML email delivered to the inbox
```

The search step fans out with `asyncio.gather`, so N searches run concurrently rather than sequentially.

---

## Design choices

**Local inference via Ollama.** Rather than using hosted models, the SDK is pointed at Ollama's OpenAI-compatible endpoint:

```python
client = AsyncOpenAI(api_key='anything', base_url="http://localhost:11434/v1")
MODEL_NAME = OpenAIChatCompletionsModel(model="llama3.2", openai_client=client)
```

Ollama speaks **Chat Completions**, not the Responses API, so `OpenAIChatCompletionsModel` is the right abstraction here — it binds the agent directly to the local client rather than leaving model resolution to the SDK's default provider.

**Free search instead of hosted tools.** `WebSearchTool()` is an OpenAI-hosted tool billed per call. Swapped for a `@function_tool`-wrapped DuckDuckGo search — no API key, no cost, no vendor lock-in.

```python
@function_tool
def web_search_tool(query: str) -> str:
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=5))
    return "\n\n".join(f"{r['title']}\n{r['body']}\nSource: {r['href']}" for r in results)
```

**Structured outputs where structure matters.** The Planner and Writer agents use Pydantic models as `output_type`, so downstream code relies on typed fields (`plan.searches`, `report.markdown_report`) instead of parsing free text.

```python
class WebSearchItem(BaseModel):
    reason: str = Field(description="Your reasoning for why this search is important to the query.")
    query: str = Field(description="The search term to use for the web search.")

class WebSearchPlan(BaseModel):
    searches: list[WebSearchItem] = Field(description="A list of web searches to perform to best answer the query.")
```

**Forced tool use.** The Search and Email agents set `ModelSettings(tool_choice="required")` so the model must actually invoke its tool rather than describing what it would do.

**Code orchestration over agent handoffs.** Each stage is a discrete, awaitable function with a typed input and output. The pipeline is readable top to bottom, and any single stage can be run or swapped in isolation.

---

## Configuration surface

| Setting | Where | Default |
|---------|-------|---------|
| Number of searches | `HOW_MANY_SEARCHES` | `5` |
| Model | `MODEL_NAME` | `llama3.2` |
| Results per search | `max_results` in `web_search_tool` | `5` |
| Report length target | Writer Agent instructions | ~1000+ words |

---

## Stack

`openai-agents` · `ollama` · `pydantic` · `ddgs` · `asyncio` · `smtplib`
