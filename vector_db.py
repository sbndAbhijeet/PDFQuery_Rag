from pathlib import Path
import os
import streamlit as st
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse

load_dotenv()

qdrant_url = "http://localhost:6333"


def create_vector_db(saved_file,uploaded_file):
    #Book in injested
    pdf_path = Path(__file__).parent/f"{saved_file}"
    loader = PyPDFLoader(file_path=pdf_path)

    docs = loader.load()

    #chunking
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=400,
    )

    split_docs = text_splitter.split_documents(documents=docs)

    #creating Vector embeddings
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=os.getenv("GEMINI_API_KEY")
    )

    #storing vectordb in qdrant

    vector_store = QdrantVectorStore.from_documents(
        documents=split_docs,
        url=qdrant_url,
        collection_name=uploaded_file.name,
        embedding=embeddings
    )
    print("Indexing of Documents done ...")
    return True


client = QdrantClient(
    url=qdrant_url
)

def delete_vector_db(collection_name):
    try:
        # get list of existing collections
        collections = client.get_collections().collections
        collection_names = [col.name for col in collections]

        # checking our current collection
        if collection_name not in collection_names:
            st.warning(f"Collection '{collection_name}' does not exist.")
            return
        
        # deleting collection
        client.delete_collection(collection_name=collection_name)
        st.success(f"Deleted vector store collection: {collection_name}")
    except UnexpectedResponse as e:
        st.error(f"Error deleting collection: {e}")