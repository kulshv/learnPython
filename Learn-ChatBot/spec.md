# Streamlit Chatbot - Requirements and Design Specification

**Status:** Draft  
**Version:** 1.0

## 1. Purpose

Build a general-purpose chatbot with a Streamlit user interface, a FastAPI
backend, and a reusable LangChain module that calls Google Gemini.

## 2. Scope

### In scope

- Users submit one text message at a time through the Streamlit interface.
- FastAPI validates the message, calls the LangChain module, and returns the
  model's reply.
- LangChain calls the `gemini-3-flash-preview` model.
- Streamlit displays user and assistant messages for the current page session.
- Each API request contains only the newly submitted message. The backend does
  not retain or send conversation history to the model.
- Invalid input and API/model failures are handled without exposing credentials
  or sensitive technical details to users.

### Out of scope

- Conversation memory sent to the model.
- Persistent conversation history or database storage.
- User accounts, authentication, or authorization.
- Production deployment and production-scale hosting.

## 3. Architecture

```text
User
  |
Streamlit frontend
  | HTTP/JSON
FastAPI backend
  | Python function call
Reusable LangChain module
  |
Google Gemini API
```

- Streamlit communicates with FastAPI over HTTP.
- FastAPI invokes a reusable Python function in the LangChain module.
- The LangChain module is responsible for making the model request and
  returning response text.
- Importing the LangChain module must not make a model request.
- The Gemini API key is configured and used only on the backend. It must not be
  included in frontend code, API responses, or logs.
- Local development defaults are `http://localhost:8000` for FastAPI and
  `http://localhost:8501` for Streamlit. The frontend backend URL should be
  configurable.

## 4. Functional requirements

### FR-1: Submit a message

The Streamlit interface shall provide a text input and a way to submit the
current message to the backend.

### FR-2: Validate input

The backend shall accept a message only when it is a string containing 1 to
300 characters after trimming leading and trailing whitespace.

The backend shall reject missing, non-string, blank, and over-limit messages.
Invalid requests shall not trigger a model call.

### FR-3: Generate a response

For a valid request, the backend shall call the reusable LangChain function
with only the submitted message. The model shall be
`gemini-3-flash-preview`.

The backend shall return the assistant response as a string.

### FR-4: Display the conversation

The Streamlit interface may retain and display messages in its current page
session. It shall send only the newly submitted message to the API, not prior
messages.

### FR-5: Handle failures

- Invalid input shall produce a client error with a clear validation message.
- A model-provider failure shall produce a gateway error.
- An unexpected backend failure shall produce a server error.
- The Streamlit interface shall show a brief, non-sensitive error and allow the
  user to retry.
- The backend may log technical details needed for diagnosis, but must not log
  API keys or return stack traces, credentials, or other sensitive details to
  the client.

### FR-6: Health check

The backend should expose `GET /health` to indicate that the API process is
available. This endpoint need not make a Gemini request.

## 5. API specification

### `POST /chat`

Request:

```json
{
  "message": "Hello"
}
```

Success response (`200 OK`):

```json
{
  "reply": "Hello! How can I help?"
}
```

Error responses:

- `422 Unprocessable Entity` for missing, non-string, blank, or over-limit
  messages.
- `502 Bad Gateway` when the Gemini provider/model request fails.
- `500 Internal Server Error` for unexpected backend failures. The response
  must not contain secrets or stack traces.

Error response format:

```json
{
  "detail": "A safe, user-readable error message."
}
```

### `GET /health`

Success response (`200 OK`):

```json
{
  "status": "ok"
}
```

## 6. Non-functional requirements

- The Gemini API key shall be loaded from backend environment configuration or
  a backend-only `.env` file.
- Secrets and `.env` files containing secrets shall not be committed to source
  control.
- The frontend shall not receive or store the Gemini API key.
- The FastAPI URL shall be configurable for the Streamlit frontend.
- The first version shall run locally with the frontend and backend as separate
  processes.

## 7. Acceptance criteria

1. A valid message of 1 to 300 characters is sent to the API and its reply is
   displayed in Streamlit.
2. A missing, non-string, blank, or over-300-character message is rejected and
   does not invoke the model.
3. Only the current message is sent to LangChain; previous UI messages are not
   sent to the API.
4. The Gemini API key is absent from frontend requests and API responses.
5. If the model call fails, the API returns a gateway error and the UI presents
   a safe error with a retry path.
6. Unexpected backend failures do not expose stack traces or secrets to
   clients.
7. `GET /health` returns the documented success response when the API process
   is available.

## 8. Implementation notes

- Refactor the existing LangChain example into a reusable function before
  connecting it to FastAPI.
- Confirm the environment-variable name supported by the installed Google
  LangChain integration when implementing backend credential loading.
- Keep the model ID, 300-character limit, error behavior, and API contract
  consistent across implementation, tests, and documentation.
