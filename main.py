from dotenv import load_dotenv
import os
from google import genai
from google.genai import types
import sys

def main():
    load_dotenv()
    print(os.environ.get("GOOGLE_API_KEY"))
    client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

    print("Args: "+str(sys.argv))
    query = sys.argv[1]

    if(len(sys.argv) < 2):
        print("Please provide a query")
        return

    verbose_flag = False
    if(len(sys.argv)==3 and sys.argv[2] == "--verbose"):
        verbose_flag = True

    message =[
        types.Content(
            role="user",
            parts=[types.Part(text=query)]
        )
    ]

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=message
    )
    print(response.text)


    if response.usage_metadata is None or response.text is None:
        print("No usage metadata or text")
        return

    if verbose_flag:
        print("\nUsage Metadata:")
        print(f"Query: {query}")
        print(response.usage_metadata.prompt_token_count)
        print(response.usage_metadata.candidates_token_count)



if __name__ == "__main__":
    main()