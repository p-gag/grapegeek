#!/usr/bin/env python3

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def test_web_search():
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    try:
        response = client.responses.create(
            model="gpt-4o",
            tools=[{
                "type": "web_search_preview",
                "search_context_size": "high"
            }],
            input="Search for recent information about Itasca grape variety from University of Minnesota. Find real research papers and actual grower experiences."
        )
        
        print("Response:")
        print(response.output_text)
        print("\n" + "="*50)
        print("Raw response object:")
        print(response)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_web_search()