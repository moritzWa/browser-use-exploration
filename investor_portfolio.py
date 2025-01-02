from langchain_openai import ChatOpenAI
from browser_use import Agent
import asyncio

async def process_company(company, llm):
    task = f"""For the company {company}:
    1. Search Google for "{company} founder" and "{company} co-founder"
    2. From the search results, identify the founders' names
    3. For each founder identified, search Google for "[Founder Name] [Company Name] LinkedIn" and "[Founder Name] [Company Name] Twitter"
    4. Extract their LinkedIn and Twitter/X profile URLs from the search results
    5. Format the output as a bullet-point list with:
       - Company name
       - Founder name(s)
       - Their social links (LinkedIn, Twitter/X)
    """
    
    agent = Agent(task=task, llm=llm)
    result = await agent.run()
    
    # Extract only the relevant part of the result
    final_result = result.final_result()
    if final_result:
        return final_result
    return "No relevant data found."

async def main():
    print("Please enter the list of companies (one per line).")
    print("Press Enter twice when done:")
    
    # Collect companies until user enters a blank line
    companies = []
    while True:
        line = input().strip()
        if not line:
            break
        companies.append(line)
    
    llm = ChatOpenAI(model='gpt-4o', temperature=0.0)
    
    # Process all companies in parallel
    results = await asyncio.gather(*[process_company(company, llm) for company in companies])
    
    # Summarize and print all results
    print("\nFounders and Social Links for All Companies:")
    for result in results:
        print(result)

if __name__ == "__main__":
    asyncio.run(main())