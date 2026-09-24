from agents import OpenAIChatCompletionsModel, AsyncOpenAI
import subprocess

subprocess.run(["ollama", "pull", "llama3.2"], check=True)

client = AsyncOpenAI(
    api_key='anything',
    base_url="http://localhost:11434/v1"
)

MODEL = OpenAIChatCompletionsModel(
    model="llama3.2",
    openai_client=client
)