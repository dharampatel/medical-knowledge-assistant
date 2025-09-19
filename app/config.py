import os
import ssl
import certifi
import urllib.request
from dotenv import load_dotenv
from langchain_community.retrievers import PubMedRetriever
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

# --- SSL Fix ---
_original_urlopen = urllib.request.urlopen
ssl_context = ssl.create_default_context(cafile=certifi.where())
urllib.request.urlopen = lambda url, *args, **kwargs: _original_urlopen(
    url, *args, context=ssl_context, **kwargs
)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0,
    api_key=GOOGLE_API_KEY,
)

retriever = PubMedRetriever(max_results=20)

