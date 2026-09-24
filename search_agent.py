from agents import Agent, function_tool
from agents.model_settings import ModelSettings
from ddgs import DDGS
from ollama_model import MODEL

@function_tool
def web_search_tool(query: str) -> str:
    """
    Search the web for a given query and return a summary of results.

    Args:
        query: The search term to look up.
    """
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=5))
    return "\n\n".join(f"{r['title']}\n{r['body']}\nSource: {r['href']}" for r in results)

INSTRUCTIONS = """
You are a research assistant. Given a search term, you search the web for that term and 
produce a concise summary of the results. The summary must 2-3 paragraphs and less than 300 words.
Capture the main points and be succinct. Reply only with the summary.
"""
tools = [web_search_tool]
settings = ModelSettings(tool_choice="required")

search_agent = Agent(
    name= "Search Agent",
    instructions= INSTRUCTIONS,
    model= MODEL,
    model_settings= settings,
    tools= [web_search_tool]
)

print('succeeded')