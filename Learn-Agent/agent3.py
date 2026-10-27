from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv


load_dotenv()

# Initialize the Google Gemini chat model
llm = ChatGoogleGenerativeAI(
    model="gemini-3-flash-preview",
    temperature=0.7,
)

# Invoke the model with a simple prompt
response = llm.invoke("Say hello world and explain what LangChain is in one sentence.")

# Print the result
print(response.content)
