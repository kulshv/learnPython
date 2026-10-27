# Intent: Streamlit Chatbot

Build a simple chatbot with a Streamlit frontend, a FastAPI backend, and a LangChain module that calls Gemini.

## Architecture

Streamlit sends each user message to the FastAPI backend. The backend calls the LangChain module and returns the model’s reply.

## API

- `POST /chat` accepts `{"message": "<user message>"}` and returns `{"reply": "<assistant reply>"}`.
- Optionally provide `GET /health` to check whether the backend is available.
- Return clear errors for invalid input or model/API failures.

## Scope

- Each request contains only the current user message; the backend does not retain conversation history.
- The Streamlit UI may display messages during the current page session, but does not send previous messages to the API.
- Do not add a database, persistent chat history, or authentication in this first version.
- Keep the Gemini API key on the backend, loaded from an environment variable or backend `.env` file. Never expose it to Streamlit or the browser.
- Keep the LangChain model call in a reusable Python function.

## Validation

Test the API’s request/response behavior and error handling, then run the frontend and backend locally.
``` You can switch to a coding agent to apply it to the file.