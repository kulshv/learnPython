# Streamlit Chatbot - Technical Execution Plan

**Status:** Proposed  
**Scope:** Planning only; no application code has been implemented.

## 1. Objective

Implement the chatbot described in `spec.md`: a Streamlit frontend sends one
message per request to a FastAPI backend, which calls a reusable LangChain
function configured for Google Gemini. The backend remains stateless.

## 2. Decisions to reconcile in `spec.md` before implementation

The following decisions were clarified during review but are not yet fully
represented in the current specification. Update `spec.md` before treating it
as the implementation contract:

- Set a 30-second model-call timeout. Return HTTP `504` on timeout.
- Check for a missing Gemini API key when `/chat` is called; return HTTP `503`
  with the standard safe error response.
- Log operational metadata only. Do not log message or model-response content.
- Normalize validation errors to `{"detail": "<safe message>"}` for every
  invalid request, rather than returning FastAPI's default validation format.
- Trim leading/trailing whitespace before enforcing the 1-300-character
  message limit and pass the trimmed message to LangChain.
- Document which status code and safe response are used for each error case:
  validation (`422`), model-provider failure (`502`), timeout (`504`),
  missing backend configuration (`503`), and unexpected failure (`500`).

## 3. Proposed project structure

Keep the initial implementation small and separate the UI, API, and model
integration:

```text
Learn-ChatBot/
  app.py                 # Streamlit UI
  api.py                 # FastAPI routes and HTTP error mapping
  chatbot.py             # Reusable LangChain model invocation
  requirements.txt       # Runtime dependencies
  .env.example           # Variable names and safe placeholders only
  .gitignore              # Ignore local secrets, virtual environments, caches
  tests/
    test_api.py           # API contract and model-call behavior
    test_chatbot.py       # LangChain wrapper behavior with mocked model
```

Do not add a database, persistent history, authentication, deployment
configuration, or unrelated features in this version. Use the existing
repository conventions if they conflict with the proposed filenames.

## 4. Execution phases

### Phase 1 - Align specification and inspect environment

1. Update `spec.md` with the clarified timeout, missing-key, logging,
   normalization, and status-code decisions above.
2. Inspect the repository's Python version, dependency state, and `.gitignore`.
3. Confirm the installed Google LangChain integration's supported Gemini
   credential configuration and model invocation interface.
4. Choose and document a local environment setup without placing real secrets in
   source control.

**Exit check:** Requirements and dependency/API choices are explicit; no
application code has been written yet.

### Phase 2 - Establish dependencies and configuration

1. Add only the required runtime dependencies for Streamlit, FastAPI, an ASGI
   server, HTTP requests from Streamlit, LangChain's Google integration, and
   environment loading if needed.
2. Add an `.env.example` containing variable names and placeholder values only.
3. Ensure local `.env` files and virtual-environment/cache directories are
   ignored by Git.
4. Verify imports and package versions in the selected Python environment.

**Exit check:** The project can import its required libraries, and no secret
value is tracked.

### Phase 3 - Implement the reusable LangChain layer

1. Create a function that accepts one already-validated message and returns
   response text.
2. Configure the specified Gemini model and temperature from the agreed
   specification; do not add conversation history.
3. Ensure importing the module does not make a network request.
4. Make missing credentials and provider failures distinguishable to the API
   layer without exposing secret values.

**Exit check:** Unit tests can invoke the function through a mocked model
without network access or credentials.

### Phase 4 - Implement the FastAPI service

1. Define typed request and response schemas for `POST /chat`.
2. Validate message type, whitespace normalization, blank input, and the
   300-character maximum before invoking LangChain.
3. Normalize validation failures to the documented `{"detail": "..."}` shape
   with status `422`.
4. Apply the 30-second model-call timeout and map failures consistently:
   missing key to `503`, timeout to `504`, provider failure to `502`, and
   unexpected failure to `500`.
5. Add `GET /health`; it reports API process availability and does not call
   Gemini.
6. Log operational metadata only. Never log request/response text or
   credentials; return safe error messages without stack traces.

**Exit check:** API tests verify response schemas, status codes, normalization,
and that invalid requests do not call the model.

### Phase 5 - Implement the Streamlit interface

1. Add a chat-style interface using Streamlit's chat input and message display.
2. Keep display history only in Streamlit session state.
3. Send only the newly submitted message to `POST /chat`.
4. Read the backend base URL from Streamlit configuration/environment, default
   to `http://localhost:8000` for local development.
5. Display successful replies and a brief, non-sensitive failure message with
   a clear way to retry.
6. Do not collect, display, or transmit the Gemini API key.

**Exit check:** UI behavior can be checked against a mocked API, and its
request contains no prior conversation messages or Gemini credentials.

### Phase 6 - End-to-end verification and run instructions

1. Run focused unit and API tests without making live Gemini requests.
2. Verify `GET /health` and the documented `POST /chat` request/response
   contract locally.
3. Manually run Streamlit and FastAPI as separate processes and verify one
   successful message round-trip using a configured key.
4. Verify safe UI behavior for backend unavailable, validation failure, model
   provider failure, timeout, and missing-key cases.
5. Document exact local commands for starting both processes and configuring
   the backend key.
6. Review the final diff for accidental secrets, unintended history forwarding,
   and changes outside the chatbot project.

**Exit check:** Acceptance criteria in `spec.md` pass, and a developer can run
the application locally using the documented setup.

## 5. Test matrix

| Area | Case | Expected result |
|---|---|---|
| Input validation | Missing `message` | `422`, standard `detail` shape; no model call |
| Input validation | Non-string `message` | `422`, standard `detail` shape; no model call |
| Input validation | Empty or whitespace-only message | `422`; no model call |
| Input validation | Message trims to 1 character | Accepted and trimmed value is sent to model |
| Input validation | Message trims to 300 characters | Accepted |
| Input validation | Message trims to 301 characters | `422`; no model call |
| Model/API | Successful mocked response | `200` with `{"reply": "<text>"}` |
| Model/API | Missing Gemini key | `503`; no secret in response |
| Model/API | Model provider error | `502`; safe response |
| Model/API | Request exceeds 30 seconds | `504`; safe response |
| Model/API | Unexpected backend exception | `500`; no stack trace or secret in response |
| Health | API process available | `200` with `{"status": "ok"}` |
| Frontend | New user turn | Only that turn is sent to backend |
| Frontend | Backend/model error | Safe retryable message; no credentials displayed |
| Logging | Requests and responses | Metadata only; no message/reply content or API key |

## 6. Out-of-scope follow-ups

- Sending prior turns to the model or adding server-side conversation memory.
- Persisting chat history.
- User identity, authentication, rate limiting, or multi-user controls.
- Deployment, monitoring infrastructure, and production hardening beyond the
  error handling and secret protections specified above.
