# Design

## Overview

Build a PDF question-answering application using retrieval-augmented generation (RAG). Users upload or select PDF files, then ask questions in a conversational chatbot interface. For each question, the application retrieves relevant passages from the selected documents and asks a language model to answer using that evidence. The UI presents the answer with source references.

The initial version is a local, single-user application. The UI, API, PDF processing, embedding model, answer-generation model, and Chroma vector store run on the user's computer. After dependencies and model files are downloaded, normal application use should not require internet access or send document content off-device. Keep document processing, retrieval, answer generation, and UI code separated so components can be replaced or tested independently.

## User flow

1. The user opens the application and uploads one or more PDFs.
2. The application extracts text, splits it into chunks, creates embeddings, and indexes the chunks.
3. The user selects the indexed document or collection and asks a question in the chat.
4. The application retrieves relevant chunks, generates an answer grounded in those chunks, and returns source references.
5. The UI displays the answer and cited document pages. Follow-up questions remain in the conversation and trigger retrieval again.

## Architecture

```text
                    +--------------------+
                    |      Chat UI       |
                    | Upload, chat, refs |
                    +---------+----------+
                              | HTTP/JSON
                              v
                    +--------------------+
                    |     API layer      |
                    | Routes, validation |
                    | response schemas   |
                    +---------+----------+
                              |
                              v
                    +--------------------+
                    |  Service layer     |
                    | Document + chat    |
                    | orchestration      |
                    +----+----------+----+
                         |          |
               PDF upload|          |Question + history
                         v          v
                  +-------------+  +-------------------+
                  | Ingestion   |  | RAG pipeline      |
                  | Extract     |  | Retrieve + prompt |
                  | Chunk       |  | Generate answer   |
                  +------+------+  +----+---------+----+
                         |               |         |
                         v               v         v
                  +-------------+  +----------+ +-------------+
                  | Embeddings  |  | Vector   | | Language    |
                  |             |  | store    | | model       |
                  +-------------+  +----------+ +-------------+
                                         |
                                         v
                                  Chunks + metadata

                    +-------------------------------+
                    | Evaluation dataset and runner |
                    +-------------------------------+
```

## Components

### Chat UI

- Provide a conversational message history and question input.
- Let users upload PDFs and select which indexed documents are in scope.
- Show loading, ingestion progress, and clear errors.
- Display answers with document name, page number, and relevant source snippets.
- Initial implementation candidate: Streamlit.

### API layer

- Provide the only interface the UI uses to access application functionality; the UI must not call service, ingestion, vector-store, or model code directly.
- Use HTTP with JSON request/response bodies, except PDF upload, which uses multipart form data.
- Validate inputs and return consistent response schemas and meaningful HTTP status codes.
- Translate expected service errors into clear client errors; do not expose stack traces or provider secrets.
- Initial implementation candidate: FastAPI.

### Service layer

- Own document and chat workflows and coordinate ingestion, retrieval, and answer generation.
- Keep business logic independent of HTTP and the UI framework so it can be tested directly.
- Return typed domain results for the API to serialize.
- The API layer handles transport concerns; services handle application behavior.

### Session management

- Track the selected documents and conversation history per session.
- Keep session state behind the service layer; the UI does not own application state beyond presentation.
- Start with in-memory sessions; persistent accounts and conversation storage are out of scope for the MVP.

### MVP API contract

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Report whether the API is running. |
| `POST` | `/api/documents` | Upload and index a PDF; return its document ID and processing result. |
| `GET` | `/api/documents` | List documents available to the local user. |
| `DELETE` | `/api/documents/{document_id}` | Remove a document and its indexed chunks. |
| `POST` | `/api/chat/sessions` | Create an in-memory chat session, optionally scoped to document IDs. |
| `POST` | `/api/chat/sessions/{session_id}/messages` | Submit a question and return an answer with citations. |

For the MVP, document processing and message generation can be synchronous requests. Apply request/file size limits and timeouts; move long-running ingestion to background jobs only if real usage requires it.

Chat responses should have a stable shape, for example:

```json
{
  "answer": "The answer grounded in the selected PDFs.",
  "sources": [
    {
      "document_id": "doc_123",
      "filename": "guide.pdf",
      "page": 4,
      "snippet": "Relevant supporting text."
    }
  ]
}
```

Return a clear answer with an empty `sources` list when no supporting evidence is found, rather than fabricating citations.

### PDF ingestion

- Validate uploaded file types and handle invalid or empty PDFs with explicit errors.
- Extract text page by page and preserve page numbers.
- Split extracted text into overlapping chunks.
- Attach metadata to each chunk, including document identifier, filename, page number, and chunk identifier.
- Generate embeddings and index the chunks.
- Detect PDFs with no extractable text and report that OCR is not supported in the initial text-based MVP.

### Vector store

- Store chunk embeddings and metadata and expose operations to add, search, and remove document chunks.
- Filter retrieval to the documents selected for the current chat.
- Use Chroma with local persistence for the MVP.
- Keep the rest of the application dependent on a small vector-store interface.

### RAG question-answering pipeline

1. Accept the current question, selected documents, and relevant conversation context.
2. Embed the question and retrieve the most relevant chunks from the selected documents.
3. Construct a prompt containing the question and retrieved evidence.
4. Instruct the language model to answer only from the supplied evidence, cite its sources, and state when the evidence is insufficient.
5. Return a structured result containing the answer and source references.

Retrieve evidence again for every question, including follow-ups. Use conversation history to clarify the user's intent, not as a substitute for document evidence.

### Model and embedding providers

- Run both embedding generation and answer generation locally; do not make hosted model API calls.
- Use `sentence-transformers/all-MiniLM-L6-v2` as the initial embedding-model candidate, with 384 dimensions for both document chunks and question queries.
- Select a local language model and runtime before implementation, considering available RAM, CPU/GPU, answer quality, and model license. Use the same configured model consistently for evaluation runs.
- Download required model files before offline use, then configure runtime loading to use local files only and fail clearly if required files are unavailable.
- Isolate embedding and language-model calls behind small interfaces to enable testing and model replacement.
- Keep model files and local indexes on the user's computer; never require API credentials for normal use.

### Evaluation

- Maintain a version-controlled dataset of questions, expected answers, and relevant source pages or chunks.
- Evaluate retrieval separately from generated answers.
- Track retrieval recall or hit rate, answer relevance, faithfulness to retrieved evidence, and citation correctness.
- Save metrics and representative outputs so changes to chunking, prompts, embeddings, or models can be compared.
- Treat automated model-based scores as signals; include human review for a small representative sample.

## Suggested project structure

```text
Learn-VectorDB/
  app.py                    # Streamlit entry point and chat UI
  api.py                    # FastAPI routes and request/response schemas
  services/
    documents.py            # Document workflow orchestration
    chat.py                 # Chat workflow orchestration
  ingestion.py              # PDF extraction, chunking, and indexing
  rag.py                    # Retrieval and answer generation
  vector_store.py            # Vector-store interface and local implementation
  models.py                  # Embedding and language-model provider interfaces
  evaluation/
    dataset.json             # Questions, expected answers, and evidence
    run.py                   # Evaluation runner and report output
  tests/
    test_ingestion.py
    test_rag.py
    test_evaluation.py
```

The UI calls the API over HTTP; API routes call services; services coordinate domain modules. Do not let UI code import services or infrastructure modules directly. Keep this structure flexible and avoid adding modules until implementation needs them.

## Error handling and safety

- Report unsupported, corrupt, password-protected, or text-empty PDFs clearly.
- Handle local model loading and inference errors visibly; do not silently return an empty or fabricated answer.
- Limit answer context to retrieved chunks and require the model to acknowledge insufficient evidence.
- Treat document contents as untrusted input. They are evidence to summarize, not instructions to follow.
- Avoid logging uploaded document contents, questions, or secrets by default.
- Run local services on loopback by default; do not expose the API to the network unless explicitly configured.

## Testing strategy

- Unit-test text extraction, chunk boundaries, metadata preservation, and citation mapping.
- Test retrieval filtering, no-result behavior, and structured answer/source output with fake provider implementations.
- Test API request validation, response schemas, status codes, and service-error mapping.
- Test user-visible upload and chat behavior, including invalid PDFs and insufficient evidence.
- Evaluate against the fixed dataset and compare retrieval and answer metrics across changes.

## MVP scope and future work

### MVP

- Local, single-user chatbot UI backed by a separate HTTP API and service layer.
- Text-based PDF upload and ingestion.
- Semantic retrieval over selected documents.
- Evidence-grounded answers with page-level source references.
- Repeatable evaluation dataset and report.
- Fully local execution with a persistent Chroma index and local embedding and answer-generation models after initial model download.

### Out of scope for MVP

- OCR for scanned PDFs.
- Multi-user authentication, authorization, and shared workspaces.
- Hosted deployment and distributed storage.
- Advanced hybrid search, reranking, and long-term chat persistence.

## Decisions to make before implementation

- Select a local answer-generation model and runtime that fit the target computer's hardware and license requirements.
- Confirm the application works with network access disabled after model files and dependencies are installed.
- Choose PDF parsing and chunking libraries and tune chunk size/overlap against the evaluation dataset.
- Decide whether the application must support multiple PDFs in one chat and how users remove/re-index documents.
