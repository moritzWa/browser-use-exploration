from langchain_openai import ChatOpenAI
from browser_use import Agent
import asyncio
import re
from urllib.parse import urlparse

async def validate_url(url: str) -> bool:
    """Validate if a string is a proper URL"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

async def process_company(company, llm):
    task = f"""For the company {company}, follow these steps EXACTLY:
    1. Search Google for "{company} founder" and "{company} co-founder"
    2. From the search results, identify the founders' names
    3. For each founder identified:
        a. Search Google for "[Founder Name] [Company Name] LinkedIn"
        b. From the search results, find and extract the LinkedIn profile URL (must start with 'https://www.linkedin.com/in/')
           DO NOT click or open the link - just extract it from the search results
        c. Search Google for "[Founder Name] [Company Name] Twitter"
        d. From the search results, find and extract the Twitter/X profile URL (must start with 'https://twitter.com/' or 'https://x.com/')
           DO NOT click or open the link - just extract it from the search results
    4. Format the output as a bullet-point list with:
       - Company name
         - Founder name
           - LinkedIn: [URL from search results]
           - Twitter/X: [URL from search results]
    5. If a profile URL cannot be found in search results, write "Profile not found" instead.
    
    IMPORTANT: 
    - Extract URLs directly from the search results
    - DO NOT click or open the profile links
    - Only use URLs that match the correct format (linkedin.com/in/ or twitter.com/ or x.com/)
    - Do not create or guess URLs
    """
    
    agent = Agent(task=task, llm=llm)
    result = await agent.run()
    
    # Extract only the relevant part of the result
    final_result = result.final_result()
    if not final_result:
        return "No relevant data found."
    
    # Validate URLs in the result
    lines = final_result.split('\n')
    validated_lines = []
    for line in lines:
        if 'http' in line:
            # Extract URL from the line
            url_match = re.search(r'https?://[^\s<>"]+|www\.[^\s<>"]+', line)
            if url_match:
                url = url_match.group()
                # Validate the URL
                if await validate_url(url):
                    if ('linkedin.com/in/' in url) or ('twitter.com/' in url) or ('x.com/' in url):
                        validated_lines.append(line)
                    else:
                        # Replace invalid social media URL with "Profile not found"
                        validated_lines.append(line.replace(url, "Profile not found"))
                else:
                    validated_lines.append(line.replace(url, "Profile not found"))
            else:
                validated_lines.append(line)
        else:
            validated_lines.append(line)
    
    return '\n'.join(validated_lines)

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
        print("-" * 50)  # Add separator between companies

if __name__ == "__main__":
    asyncio.run(main())