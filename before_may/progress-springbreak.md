List of components and stuff done so far
- Researched agentic rag/rag with Python and langchain + vector storage (https://youtu.be/3ZDeqTIXBPM?si=KKt5lBkhYGXFeufc)
- Deployed n8n successfully
- Components + Layers
	- Integration Layer
		- REST endpoints, KSAP DataNow, Webhooks
	- Neural Network component
		- Called via API
		- User uploads data and it is sent to neural network through API
		- Results are sent back through API to drive or bucket
		- Module where chatbot prompts user with options
		- 6 months predictions loaded
	- LLM with chatbot integration and vector storage
	- Recommendation Report Module - Research 

POCs
- Neural Network full integration (drag and drop CSV or JSON, show dataframe, select column to predict, and train)
- Agentic RAG chatbot
	- first POC with local
	- second iteration try with S3


Finalize UI Changes
