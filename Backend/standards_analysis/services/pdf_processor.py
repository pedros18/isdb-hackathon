# KARIMDATA/Backend/standards_analysis/services/pdf_processor.py

import os
import re
import PyPDF2 # For PDF text extraction
import chromadb # For vector database interaction
import logging # For logging
from typing import List, Dict, Any, Optional #

# LangChain components for text processing and embeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings # Ensure this is the correct import for your LangChain version

# Imports from within the 'services' package (or app if structured differently)
from .ai_config import aicfg, generate_new_db_directory_path, update_ai_config_db_directory

# Get a logger instance for this module
logger = logging.getLogger('standards_analysis.ai_system.pdf_processor')


def extract_text_from_pdf_pypdf2(pdf_path: str) -> str:
    """
    Extracts text from a PDF file using the PyPDF2 library.
    Args:
        pdf_path: The file system path to the PDF file.
    Returns:
        A string containing the extracted text, or an empty string if extraction fails.
    """
    logger.info(f"Attempting to extract text from PDF (using PyPDF2): {pdf_path}")
    text_content = ""
    try:
        with open(pdf_path, 'rb') as pdf_file_object:
            pdf_reader = PyPDF2.PdfReader(pdf_file_object)
            num_pages = len(pdf_reader.pages)
            logger.debug(f"PDF '{pdf_path}' has {num_pages} pages.")
            for page_num in range(num_pages):
                page_object = pdf_reader.pages[page_num]
                page_text = page_object.extract_text()
                if page_text:
                    text_content += page_text + "\n"
                else:
                    logger.warning(f"No text extracted by PyPDF2 from page {page_num + 1} of '{pdf_path}'.")
        if text_content:
            logger.info(f"PyPDF2 successfully extracted text from '{pdf_path}'. Total length: {len(text_content)} characters.")
        else:
            logger.warning(f"PyPDF2 extracted no text content from '{pdf_path}'.")
    except FileNotFoundError:
        logger.error(f"PDF file not found at path: {pdf_path}", exc_info=True)
    except Exception as e:
        logger.error(f"Error extracting text with PyPDF2 from '{pdf_path}': {e}", exc_info=True)
    return text_content

def clean_document_text(text: str) -> str:
    """
    Cleans and preprocesses extracted text.
    - Replaces multiple whitespaces with a single space.
    - Removes non-ASCII characters.
    - Strips leading/trailing whitespace.
    Args:
        text: The raw text string to clean.
    Returns:
        The cleaned text string.
    """
    if not text:
        return ""
    logger.debug(f"Cleaning document text. Original length: {len(text)} characters.")
    # Replace multiple whitespaces (including newlines, tabs) with a single space
    cleaned_text = re.sub(r'\s+', ' ', text)
    # Remove non-ASCII characters (optional, depending on needs)
    # cleaned_text = re.sub(r'[^\x00-\x7F]+', '', cleaned_text)
    cleaned_text = cleaned_text.strip()
    logger.debug(f"Text cleaned. New length: {len(cleaned_text)} characters.")
    return cleaned_text

def split_text_into_chunks_with_metadata(text: str, standard_name: str) -> List[Dict[str, Any]]:
    """
    Splits a large text into smaller, manageable chunks with associated metadata.
    Args:
        text: The text content to split.
        standard_name: The name of the standard, used for metadata.
    Returns:
        A list of dictionaries, where each dictionary represents a chunk
        and contains 'content' and 'metadata'.
    """
    logger.debug(f"Splitting text for standard: '{standard_name}' into chunks.")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=aicfg.CHUNK_SIZE,
        chunk_overlap=aicfg.CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""] # Common separators
    )
    chunks_content = text_splitter.split_text(text)
    
    documents_with_metadata = []
    for i, chunk_text in enumerate(chunks_content):
        documents_with_metadata.append({
            "content": chunk_text,
            "metadata": {
                "source": str(standard_name), # Ensure source is a string
                "chunk_id": i
            }
        })
    logger.info(f"Split text for '{standard_name}' into {len(documents_with_metadata)} chunks.")
    return documents_with_metadata

class DocumentProcessorUtils:
    """
    A utility class that wraps document processing functionalities,
    primarily text splitting. This provides a consistent interface if used by other modules.
    """
    @staticmethod
    def split_text_into_chunks(text: str, standard_name: str) -> List[Dict[str, Any]]:
        """
        Static method to split text into chunks with metadata.
        Delegates to the standalone `split_text_into_chunks_with_metadata` function.
        """
        return split_text_into_chunks_with_metadata(text, standard_name)

import chromadb
from typing import List, Dict, Any, Optional # Make sure Optional is here too if other functions use it

# ... logger and other functions ...
# At the very top of the problematic file (e.g., pdf_processor.py)
print(f"--- Starting to load {__file__} ---")
import chromadb
print(f"--- chromadb module imported in {__file__}: {chromadb}")
print(f"--- Attributes of chromadb in {__file__}: {dir(chromadb)}") # This will list all attributes
# Check specifically if 'API' is there, though we expect it not to be.
print(f"--- Does chromadb have 'API' attribute in {__file__}? {'API' in dir(chromadb)}")
print(f"--- Does chromadb have 'Client' attribute in {__file__}? {'Client' in dir(chromadb)}")
print(f"--- Does chromadb have 'PersistentClient' attribute in {__file__}? {'PersistentClient' in dir(chromadb)}")


def create_vector_db(documents: List[Dict[str, Any]], db_path: str, collection_name: str) -> chromadb.PersistentClient:
    """
    Creates or updates a ChromaDB vector database with the provided documents.
    Args:
        documents: A list of document chunks (dictionaries with 'content' and 'metadata').
        db_path: The file system path where the ChromaDB should be persisted.
        collection_name: The name of the collection within the database.
    Returns:
        The ChromaDB client instance.
    Raises:
        ValueError: If the OpenAI API key is not configured.
    """
    logger.info(f"Attempting to create/update vector database in directory: '{db_path}' with collection: '{collection_name}'")
    if not aicfg.OPENAI_API_KEY:
        logger.error("OpenAI API key is not available in AIConfig. Cannot create embeddings for vector DB.")
        raise ValueError("OpenAI API key is required for creating embeddings.")

    embeddings_provider = OpenAIEmbeddings(
        model=aicfg.EMBEDDING_MODEL,
        openai_api_key=aicfg.OPENAI_API_KEY
    )

    # Ensure the database directory exists
    os.makedirs(db_path, exist_ok=True)

    try:
        client = chromadb.PersistentClient(path=str(db_path))  # Ensure path is string
        # Use get_or_create_collection to be robust whether collection exists or not
        collection = client.get_or_create_collection(name=str(collection_name))  # Ensure name is string
        logger.info(f"Accessed/Created collection '{collection_name}' in ChromaDB at '{db_path}'.")
    except Exception as e:
        logger.error(f"Failed to initialize ChromaDB client or collection at '{db_path}': {e}", exc_info=True)
        raise  # Re-raise the exception as this is a critical failure

    # Process and add the documents in batches to avoid memory issues
    batch_size = 100  # Adjust based on your system's capabilities
    total_added = 0
    
    try:
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            
            # Prepare data for ChromaDB (ids, documents, metadatas)
            ids = [f"doc_{i}_{chunk['metadata']['chunk_id']}" for chunk in batch]
            texts = [chunk['content'] for chunk in batch]
            metadatas = [chunk['metadata'] for chunk in batch]
            
            # Generate embeddings for the documents
            embeddings = embeddings_provider.embed_documents(texts)
            
            # Add documents to the collection
            collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas
            )
            
            total_added += len(batch)
            logger.debug(f"Added batch {i//batch_size + 1} with {len(batch)} documents. Total added so far: {total_added}")
        
        logger.info(f"Successfully added {total_added} documents to collection '{collection_name}'.")
    except Exception as e:
        logger.error(f"Error adding documents to collection '{collection_name}': {e}", exc_info=True)
        raise  # Re-raise as this is a critical failure
    
    logger.info(f"Vector database creation/update operations completed successfully in '{db_path}' for collection '{collection_name}'.")
    return client  # Return the client for potential further use
def process_all_pdfs_from_input_folder_and_build_db(force_recreate: bool = False) -> Optional[chromadb.Client]:
    """
    Processes all PDF files found in the configured AI_PDF_INPUT_FOLDER,
    extracts text, chunks it, and builds/updates the vector database.
    Args:
        force_recreate: If True, a new versioned database directory will be created,
                        and the global AIConfig.DB_DIRECTORY will be updated.
                        If False, the existing AIConfig.DB_DIRECTORY will be used.
    Returns:
        The ChromaDB client instance if successful, otherwise None.
    """
    pdf_input_folder_path = str(aicfg.PDF_INPUT_FOLDER)
    logger.info(f"Starting batch PDF processing from folder: '{pdf_input_folder_path}'. Force DB recreate: {force_recreate}")

    if not os.path.exists(pdf_input_folder_path):
        logger.error(f"Configured PDF input folder '{pdf_input_folder_path}' does not exist. Cannot process PDFs.")
        return None
    
    pdf_files = [f for f in os.listdir(pdf_input_folder_path) if f.lower().endswith('.pdf')]
    if not pdf_files:
        logger.info(f"No PDF files found in '{pdf_input_folder_path}'. No new data to add to vector DB.")
        return None # Or return an existing client if one is expected
        
    logger.info(f"Found {len(pdf_files)} PDF files to process in '{pdf_input_folder_path}'.")
    all_document_chunks: List[Dict[str, Any]] = []
    
    for pdf_file_name in pdf_files:
        full_pdf_path = os.path.join(pdf_input_folder_path, pdf_file_name)
        # Use filename without extension as the standard name/source
        standard_name_from_file = os.path.splitext(pdf_file_name)[0]
        
        logger.info(f"Processing PDF file: '{pdf_file_name}' (Standard Name: '{standard_name_from_file}')")
        raw_text = extract_text_from_pdf_pypdf2(full_pdf_path)
        if not raw_text:
            logger.warning(f"No text extracted from '{pdf_file_name}', skipping this file.")
            continue
            
        cleaned_text = clean_document_text(raw_text)
        doc_chunks = split_text_into_chunks_with_metadata(cleaned_text, standard_name_from_file)
        all_document_chunks.extend(doc_chunks)
        logger.info(f"Extracted {len(doc_chunks)} chunks from '{pdf_file_name}'.")

    if not all_document_chunks:
        logger.info("No document chunks were extracted from any PDFs in the input folder. Cannot create/update vector database.")
        return None

    logger.info(f"Total document chunks extracted from all PDFs: {len(all_document_chunks)}.")

    current_db_path_for_creation = str(aicfg.DB_DIRECTORY) # Start with current config
    
    if force_recreate:
        logger.info("Force recreate is True. A new database directory will be generated.")
        new_db_path = generate_new_db_directory_path() # This function creates the directory
        update_ai_config_db_directory(new_db_path) # This updates aicfg.DB_DIRECTORY globally
        current_db_path_for_creation = new_db_path # Use the new path for this creation
        logger.info(f"New database will be created in: '{current_db_path_for_creation}'. AIConfig updated.")
    else:
        logger.info(f"Using existing/default DB directory for adding/updating collection: '{current_db_path_for_creation}'.")
        # Ensure this directory exists if not forcing new one
        os.makedirs(current_db_path_for_creation, exist_ok=True)

    try:
        # Pass the determined DB path and collection name to create_vector_db
        client = create_vector_db(
            documents=all_document_chunks,
            db_path=current_db_path_for_creation,
            collection_name=str(aicfg.COLLECTION_NAME)
        )
        logger.info(f"Batch PDF processing and vector database build/update successful in '{current_db_path_for_creation}'.")
        return client
    except Exception as e:
        logger.error(f"Critical error during batch PDF processing and vector database build: {e}", exc_info=True)
        return None