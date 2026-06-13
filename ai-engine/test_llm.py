import os
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

for model in ["gemini-1.5-flash", "gemini-1.5-flash-latest", "gemini-2.0-flash", "gemini-1.5-pro"]:
    try:
        print(f"Testing {model}...")
        llm = ChatGoogleGenerativeAI(model=model, google_api_key=api_key, max_retries=1, timeout=5)
        response = llm.invoke("Say hi")
        print(f"Success! {model} responded: {response.content}")
        break
    except Exception as e:
        print(f"Failed {model}: {e}")
