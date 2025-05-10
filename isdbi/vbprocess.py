import os
import re
import PyPDF2
import numpy as np
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
import chromadb
from dotenv import load_dotenv
import config

# Load environment variables
load_dotenv()

# Use configuration from config file
PDF_FOLDER = config.PDF_FOLDER
CHUNK_SIZE = config.CHUNK_SIZE
CHUNK_OVERLAP = config.CHUNK_OVERLAP
EMBEDDING_MODEL = config.EMBEDDING_MODEL
DB_DIRECTORY = config.DB_DIRECTORY

# Set OpenAI API key
os.environ["OPENAI_API_KEY"] = config.OPENAI_API_KEY

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
    return text

def clean_text(text):
    """Clean and preprocess the extracted text."""
    # Replace multiple whitespaces with a single space
    text = re.sub(r'\s+', ' ', text)
    # Remove other unwanted characters or formatting
    text = re.sub(r'[^\x00-\x7F]+', '', text)  # Remove non-ASCII characters
    return text.strip()

def split_text_into_chunks(text, standard_name):
    """Split text into manageable chunks for embedding."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    
    chunks = text_splitter.split_text(text)
    
    # Add metadata to each chunk
    documents = []
    for i, chunk in enumerate(chunks):
        documents.append({
            "content": chunk,
            "metadata": {
                "source": standard_name,
                "chunk_id": i
            }
        })
    
    return documents

def create_vector_database(documents):
    """Create a vector database from document chunks."""
    # Initialize embeddings provider
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
    
    # Create Chroma client
    client = chromadb.PersistentClient(path=DB_DIRECTORY)
    
    # Create or get collection
    collection = client.get_or_create_collection(name="aaoifi_standards")
    
    # Process documents in batches to avoid API limits
    batch_size = 100
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i+batch_size]
        
        # Extract content and metadata
        texts = [doc["content"] for doc in batch]
        ids = [f"doc_{i+j}" for j in range(len(batch))]
        metadatas = [doc["metadata"] for doc in batch]
        
        # Generate embeddings
        embeds = embeddings.embed_documents(texts)
        
        # Add to collection
        collection.add(
            embeddings=embeds,
            documents=texts,
            ids=ids,
            metadatas=metadatas
        )
    
    return client

def main():
    """Main function to process PDFs and create vector database."""
    if not os.path.exists(PDF_FOLDER):
        print(f"Error: The folder '{PDF_FOLDER}' does not exist.")
        return
    
    # Create directory for vector database if it doesn't exist
    os.makedirs(DB_DIRECTORY, exist_ok=True)
    
    all_documents = []
    pdf_files = [f for f in os.listdir(PDF_FOLDER) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print(f"No PDF files found in '{PDF_FOLDER}'.")
        return
    
    print(f"Found {len(pdf_files)} PDF files.")
    
    for pdf_file in pdf_files:
        pdf_path = os.path.join(PDF_FOLDER, pdf_file)
        standard_name = os.path.splitext(pdf_file)[0]
        
        print(f"Processing {pdf_file}...")
        
        # Extract text from PDF
        raw_text = extract_text_from_pdf(pdf_path)
        
        # Clean the text
        cleaned_text = clean_text(raw_text)
        
        # Split into chunks
        chunks = split_text_into_chunks(cleaned_text, standard_name)
        all_documents.extend(chunks)
        
        print(f"Extracted {len(chunks)} chunks from {pdf_file}")
    
    print(f"Total chunks extracted: {len(all_documents)}")
    
    # Create vector database
    print("Creating vector database...")
    client = create_vector_database(all_documents)
    
    print(f"Vector database created successfully in '{DB_DIRECTORY}'")

if __name__ == "__main__":
    main()