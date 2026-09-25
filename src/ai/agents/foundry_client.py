from agent_framework.foundry import FoundryChatClient
from azure.identity import AzureCliCredential

from src.ai.config import settings


def get_client() -> FoundryChatClient:
    return FoundryChatClient(
        project_endpoint=settings.foundry_project_endpoint,
        model=settings.foundry_model,  
        credential=AzureCliCredential(),
    )
    

import asyncio
from agent_framework import Agent


async def hello():
    agent = Agent(
        client=get_client(),
        name="Hello",
        instructions="You are a helpful assistant.",
    )
    result = await agent.run("Say hello in one sentence.")
    print(result)


if __name__ == "__main__":
    asyncio.run(hello())    