# standards_analysis/services/pdf_processor.py
import os
import re
import PyPDF2
import chromadb
import logging
from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings

# from .ai_config import aicfg, generate_new_db_directory_path, update_ai_config_db_directory
# Example from standards_analysis/services/ai_orchestration.py
from standards_analysis.services.ai_config import aicfg, update_ai_config_db_directory
# or if ai_orchestration.py is in the same services/ directory:
# from .ai_config import aicfg

# Example from standards_analysis/views.py
from .services.ai_config import aicfg
from .services.ai_orchestration import AIOperationsOrchestrator
logger = logging.getLogger('standards_analysis.ai_system.pdf_processor')

def extract_text_from_pdf_pypdf2(pdf_path: str) -> str: # Renamed to avoid conflict
    logger.info(f"Extracting text from PDF (PyPDF2): {pdf_path}")
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num, page in enumerate(pdf_reader.pages):
                extracted_page_text = page.extract_text()
                if extracted_page_text:
                    text += extracted_page_text + "\n"
                else:
                    logger.warning(f"No text extracted from page {page_num + 1} of {pdf_path} by PyPDF2")
        logger.info(f"PyPDF2 successfully extracted text from {pdf_path}. Length: {len(text)}")
    except Exception as e:
        logger.error(f"Error extracting text with PyPDF2 from {pdf_path}: {e}", exc_info=True)
        # Fallback or re-raise depends on desired behavior
    return text

def clean_document_text(text: str) -> str: # Renamed
    logger.debug("Cleaning document text...")
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    cleaned = text.strip()
    logger.debug(f"Text cleaned. Original length: {len(text)}, Cleaned length: {len(cleaned)}")
    return cleaned

def split_text_into_chunks_with_metadata(text: str, standard_name: str) -> list[dict[str, Any]]:
    # (Copied from FastAPI pdf_processing.py)
    logger.debug(f"Splitting text for standard: {standard_name}")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=aicfg.CHUNK_SIZE,
        chunk_overlap=aicfg.CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    chunks_content = text_splitter.split_text(text)
    documents = []
    for i, chunk_text in enumerate(chunks_content):
        documents.append({
            "content": chunk_text,
            "metadata": {"source": standard_name, "chunk_id": i}
        })
    logger.info(f"Split text for '{standard_name}' into {len(documents)} chunks.")
    return documents

class DocumentProcessorUtils: # Renamed to avoid class name conflict if DocumentProcessor agent exists
    @staticmethod
    def split_text_into_chunks(text: str, standard_name: str) -> list[dict[str, Any]]:
        return split_text_into_chunks_with_metadata(text, standard_name)

def create_vector_db(documents: list[dict[str, Any]], db_path: str, collection_name: str) -> chromadb.PersistentClient:
    # (Adapted from FastAPI pdf_processing.py's create_vector_database_in_configured_path)
    logger.info(f"Creating vector database in directory: {db_path} with collection: {collection_name}")
    if not aicfg.OPENAI_API_KEY:
        logger.error("OpenAI API key not available for embeddings.")
        raise ValueError("OpenAI API key is required for embeddings.")

    embeddings_provider = OpenAIEmbeddings(model=aicfg.EMBEDDING_MODEL, openai_api_key=aicfg.OPENAI_API_KEY)
    os.makedirs(db_path, exist_ok=True)
    client = chromadb.PersistentClient(path=db_path)
    collection = client.get_or_create_collection(name=collection_name) # Use get_or_create
    
    batch_size = 50 # Smaller batch size for potentially less robust environments
    num_batches = (len(documents) + batch_size - 1) // batch_size
    logger.info(f"Total documents to process for DB: {len(documents)}, in {num_batches} batches.")

    for i in range(0, len(documents), batch_size):
        batch_documents = documents[i:i+batch_size]
        current_batch_num = (i // batch_size) + 1
        logger.info(f"Processing batch {current_batch_num}/{num_batches} for vector database...")
        texts = [doc["content"] for doc in batch_documents]
        ids = [f"{doc['metadata']['source']}_chunk_{doc['metadata']['chunk_id']}_{j}" for j, doc in enumerate(batch_documents, start=i)]
        metadatas = [doc["metadata"] for doc in batch_documents]

        if not texts:
            logger.info(f"Skipping empty batch {current_batch_num}.")
            continue
        try:
            embeds = embeddings_provider.embed_documents(texts)
            collection.add(embeddings=embeds, documents=texts, ids=ids, metadatas=metadatas)
            logger.info(f"Added {len(texts)} documents in batch {current_batch_num} to collection.")
        except Exception as e:
            logger.error(f"Error embedding/adding batch {current_batch_num} to collection {collection_name} at {db_path}: {e}")
            logger.error(f"Problematic texts (first 50 chars of first text): {texts[0][:50] if texts else 'N/A'}")
            continue
    
    logger.info(f"Vector database operations completed in '{db_path}' for collection '{collection_name}'.")
    return client

def process_all_pdfs_from_input_folder_and_build_db(force_recreate: bool = False) ->  chromadb.PersistentClient | None:
    # (Adapted from FastAPI pdf_processing.py's process_all_pdfs_and_build_db)
    pdf_folder_path = aicfg.PDF_INPUT_FOLDER
    logger.info(f"Starting PDF processing from folder: {pdf_folder_path}. Force recreate: {force_recreate}")

    if not os.path.exists(pdf_folder_path):
        logger.error(f"PDF input folder '{pdf_folder_path}' does not exist.")
        return None
    
    pdf_files = [f for f in os.listdir(pdf_folder_path) if f.lower().endswith('.pdf')]
    if not pdf_files:
        logger.info(f"No PDF files found in '{pdf_folder_path}'.")
        return None
        
    all_document_chunks = []
    for pdf_file in pdf_files:
        pdf_path = os.path.join(pdf_folder_path, pdf_file)
        standard_name = os.path.splitext(pdf_file)[0]
        raw_text = extract_text_from_pdf_pypdf2(pdf_path)
        if not raw_text: continue
        cleaned_text = clean_document_text(raw_text)
        doc_chunks = split_text_into_chunks_with_metadata(cleaned_text, standard_name)
        all_document_chunks.extend(doc_chunks)

    if not all_document_chunks:
        logger.info("No document chunks extracted. Cannot create vector database.")
        return None

    current_db_path = aicfg.DB_DIRECTORY
    if force_recreate:
        new_db_path = generate_new_db_directory_path()
        update_ai_config_db_directory(new_db_path) # This updates aicfg.DB_DIRECTORY globally for subsequent use
        current_db_path = new_db_path
        logger.info(f"New database will be created in: {current_db_path}")
    else:
        logger.info(f"Using DB directory: {current_db_path} for adding/updating collection.")
        os.makedirs(current_db_path, exist_ok=True)

    try:
        client = create_vector_db(all_document_chunks, current_db_path, aicfg.COLLECTION_NAME)
        logger.info(f"PDF processing and vector DB build/update successful in '{current_db_path}'.")
        return client
    except Exception as e:
        logger.error(f"Failed to process PDFs and build vector database: {e}", exc_info=True)
        return None
