# RAG Chatbot API

This API provides endpoints to manage knowledge bases and interact with a RAG chatbot.

## Setup

1.  Clone the repository.
2.  Navigate to the `envision_product/chat/backend/` directory.
3.  Create a virtual environment: `python -m venv venv`
4.  Activate the virtual environment: 
    *   Windows: `venv\Scripts\activate`
    *   macOS/Linux: `source venv/bin/activate`
5.  Install dependencies: `pip install -r requirements.txt`
6.  Create a `.env` file in the `envision_product/chat/backend/api/` directory by copying `.env.example` and fill in your `OPENAI_API_KEY`.

## Running the API

Navigate to the `envision_product/chat/backend/api/` directory and run:

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`. 