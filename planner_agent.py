from agents import Agent
from ollama_model import MODEL
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv(override=True)

HOW_MANY_SEARCHES = int(os.getenv("HOW_MANY_SEARCHES", 5))

class WebSearchItem(BaseModel):
    reason: str = Field(description="Your reasoning for why this search is important to the query.")
    query: str = Field(description="The search term to use for the web search.")


class WebSearchPlan(BaseModel):
    searches: list[WebSearchItem] = Field(description="A list of web searches to perform to best answer the query.")

INSTRUCTIONS = f"""
You are a research assistant. Given a user query, come up with a set of web searches
to perform to best answer the query. Output {HOW_MANY_SEARCHES} terms to query for.
"""

planner_agent = Agent(
    name="Planner Agent",
    instructions=INSTRUCTIONS,
    model=MODEL,
    output_type=WebSearchPlan
)