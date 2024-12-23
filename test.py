from langchain_openai import ChatOpenAI
from browser_use import Agent
import asyncio

async def main():
    agent = Agent(
        task="Tell me how many github stars 'browser-use' has -- note that you might encounter cookie policy popups - just accept them to continue",
        llm=ChatOpenAI(model="gpt-4o"),
    )
    
    result = await agent.run()
    print(result)

if __name__ == "__main__":
    asyncio.run(main()) 