from langchain.llms import OpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

class RAGChain:
    def __init__(self, vectorstore, temperature=0.7):
        self.vectorstore = vectorstore
        self.llm = OpenAI(temperature=temperature)
        
    def create_chain(self):
        """Create the RAG chain"""
        template = """You are a helpful assistant that answers questions based on the provided context.
        Use only the information from the context to answer the question. If you cannot find the answer
        in the context, say "I don't have enough information to answer that question."
        
        Context: {context}
        
        Question: {question}
        
        Answer:"""
        
        prompt = PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
        
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(search_kwargs={"k": 3}),
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=True
        )
        
        return qa_chain
