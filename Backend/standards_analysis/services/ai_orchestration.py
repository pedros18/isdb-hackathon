# KARIMDATA/Backend/standards_analysis/services/ai_orchestration.py

import os
import re
import json
import time
import uuid
import logging
from typing import List, Dict, Any, Optional

import chromadb
from langchain_openai import OpenAIEmbeddings # Ensure this is the correct import for your LangChain version

# Imports from within the 'services' package (or app if structured differently)
from .ai_config import aicfg, update_ai_config_db_directory # Import the Django-aware config
from .pdf_processor import DocumentProcessorUtils # Assuming DocumentProcessorUtils for splitting
                                                 # extract_text_from_pdf_pypdf2, clean_document_text are not directly used by orchestrator
                                                 # but by views or the bulk pdf_processor itself.

from .ai_agents import ( # All agent classes should be defined in ai_agents.py
    StandardDocument,    # The simple class to hold standard data
    DocumentReviewAgent, # Stub using original ReviewAgent
    StandardAnalysisAgent,
    EnhancementAgentNew,
    ShariahComplianceAgent,
    ValidationAgentNew,
    ReportGenerationAgent,
    VisualizationAgent,  # Agent that generates specs
    FeedbackAgent
)

# Get a logger instance for this module
logger = logging.getLogger('standards_analysis.ai_system.orchestration')

class VectorDBManager:
    """
    Manages interactions with the ChromaDB vector database for the AI system.
    """
    def __init__(self):
        self.logger = logging.getLogger('standards_analysis.ai_system.vectordb')
        if not aicfg.OPENAI_API_KEY:
            self.logger.error("OpenAI API Key not found in AIConfig for VectorDBManager.")
            raise ValueError("OpenAI API Key not configured for VectorDBManager.")

        # Uses the current DB_DIRECTORY from ai_config, which might have been
        # updated by a bulk DB creation process (e.g., admin command).
        self.db_directory = str(aicfg.DB_DIRECTORY) # Ensure it's a string path
        self.collection_name = str(aicfg.COLLECTION_NAME)
        
        os.makedirs(self.db_directory, exist_ok=True)
        try:
            self.client = chromadb.PersistentClient(path=self.db_directory)
            self.embeddings_provider = OpenAIEmbeddings(
                model=aicfg.EMBEDDING_MODEL,
                openai_api_key=aicfg.OPENAI_API_KEY
            )
            self.collection = self.client.get_or_create_collection(name=self.collection_name)
            self.logger.info(f"VectorDBManager: Connected/created collection '{self.collection_name}' at '{self.db_directory}'")
        except Exception as e:
            self.logger.error(f"VectorDBManager: Error during initialization with DB path '{self.db_directory}' and collection '{self.collection_name}': {e}", exc_info=True)
            raise
    
    def add_document_chunks(self, standard_name: str, chunks: List[Dict[str, Any]]) -> List[str]:
        if not chunks:
            self.logger.warning(f"No chunks provided for document '{standard_name}'. Skipping add to vector DB.")
            return []

        chunk_texts = [chunk["content"] for chunk in chunks]
        chunk_metadata = [chunk["metadata"] for chunk in chunks]
        # Generate unique IDs for these chunks to avoid collisions if re-adding or updating.
        chunk_ids = [str(uuid.uuid4()) for _ in range(len(chunks))]
        
        try:
            embeddings_list = self.embeddings_provider.embed_documents(chunk_texts)
        except Exception as e:
            self.logger.error(f"Error generating embeddings for '{standard_name}': {e}", exc_info=True)
            return [] # Return empty list on failure
            
        try:
            self.collection.add(
                embeddings=embeddings_list,
                documents=chunk_texts,
                metadatas=chunk_metadata,
                ids=chunk_ids
            )
            self.logger.info(f"Added {len(chunks)} chunks from '{standard_name}' to vector database collection '{self.collection_name}'.")
            return chunk_ids
        except Exception as e:
            self.logger.error(f"Error adding chunks for '{standard_name}' to collection '{self.collection_name}': {e}", exc_info=True)
            return []

    def add_standard_document_to_db(self, standard_doc: StandardDocument) -> List[str]:
        self.logger.info(f"Preparing to add standard document '{standard_doc.name}' to vector DB.")
        # Uses DocumentProcessorUtils (from pdf_processor.py) for splitting logic
        doc_chunks = DocumentProcessorUtils.split_text_into_chunks(standard_doc.content, standard_doc.name)
        return self.add_document_chunks(standard_doc.name, doc_chunks)
    
    def search_documents_in_db(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        self.logger.info(f"Searching vector DB for query: '{query[:50]}...' with top_k={top_k}")
        try:
            query_embedding = self.embeddings_provider.embed_query(query)
        except Exception as e:
            self.logger.error(f"Error generating query embedding for search: {e}", exc_info=True)
            return []

        try:
            results = self.collection.query(query_embeddings=[query_embedding], n_results=top_k)
        except Exception as e:
            self.logger.error(f"Error querying collection '{self.collection_name}': {e}", exc_info=True)
            return []
        
        if not results or not results.get("documents") or not results["documents"][0]:
            self.logger.info(f"No documents found in vector DB for the query: '{query[:50]}...'.")
            return []

        documents = results["documents"][0]
        # Handle cases where metadata or distances might be missing or not in the expected structure
        metadatas_list = results.get("metadatas", [[]])[0] if results.get("metadatas") else []
        distances_list = results.get("distances", [[]])[0] if results.get("distances") else []
        
        result_list = []
        for i in range(len(documents)):
            metadata = metadatas_list[i] if i < len(metadatas_list) else {}
            distance = distances_list[i] if i < len(distances_list) else None
            relevance_score = (1 - distance) if distance is not None else 0.0 # Assuming cosine similarity (0-1 range)
            
            result_list.append({
                "content": documents[i],
                "metadata": metadata,
                "distance": distance,
                "relevance_score": relevance_score 
            })
        self.logger.info(f"Found {len(result_list)} results in vector DB for query: '{query[:50]}...'.")
        return result_list


class AIOperationsOrchestrator:
    """
    Orchestrates the AI multi-agent system for processing AAOIFI standards.
    Uses a singleton-like pattern for Django integration.
    """
    _instance: Optional['AIOperationsOrchestrator'] = None

    @classmethod
    def get_instance(cls) -> 'AIOperationsOrchestrator':
        if cls._instance is None:
            logger.info("Creating AIOperationsOrchestrator instance for the first time.")
            cls._instance = cls()
        return cls._instance
    
    @classmethod
    def reinitialize_instance(cls) -> 'AIOperationsOrchestrator':
        """Re-initializes the global system instance. Useful after DB path changes."""
        logger.info("Re-initializing AIOperationsOrchestrator instance.")
        cls._instance = cls() # This will call __init__ again
        logger.info("AIOperationsOrchestrator re-initialized successfully.")
        return cls._instance

    def __init__(self):
        # This check prevents issues if __init__ is complex and accidentally called multiple times
        # outside the get_instance/reinitialize_instance flow, though with those class methods,
        # direct instantiation `AIOperationsOrchestrator()` should be avoided by users of the class.
        if hasattr(self, '_initialized_orchestrator') and self._initialized_orchestrator:
            logger.warning("AIOperationsOrchestrator __init__ called again on an already initialized instance. This might be a reinitialization.")
            # Depending on resource intensity, you might want to clean up old resources here.
        
        self.logger = logging.getLogger('standards_analysis.ai_system.orchestrator_main')
        self.logger.info("Initializing AIOperationsOrchestrator instance...")
        
        if not aicfg.OPENAI_API_KEY:
            self.logger.critical("OpenAI API Key is NOT configured in aicfg. AI Operations will fail.")
            # raise ValueError("OpenAI API Key is required for AI Orchestrator.") # Or handle gracefully

        # Initialize AI Agents
        try:
            self.review_agent = DocumentReviewAgent()
            self.analysis_agent = StandardAnalysisAgent()
            self.enhancement_agent = EnhancementAgentNew() 
            self.shariah_agent = ShariahComplianceAgent()
            self.validation_agent = ValidationAgentNew() 
            self.report_agent = ReportGenerationAgent()
            self.visualization_spec_agent = VisualizationAgent() # Agent that defines specs
            self.feedback_agent = FeedbackAgent()
            self.logger.info("All AI agents initialized.")
        except Exception as e:
            self.logger.critical(f"Failed to initialize one or more AI agents: {e}", exc_info=True)
            raise # Re-raise to prevent system from starting in a broken state

        # Initialize VectorDBManager
        try:
            self.vector_db_manager = VectorDBManager() # This will use aicfg.DB_DIRECTORY
            self.logger.info("VectorDBManager initialized.")
        except Exception as e:
            self.logger.critical(f"Failed to initialize VectorDBManager: {e}", exc_info=True)
            raise

        os.makedirs(aicfg.OUTPUT_DIR, exist_ok=True)
        self._initialized_orchestrator = True # Mark as initialized
        self.logger.info("AIOperationsOrchestrator initialization complete.")
    
    def process_uploaded_standard(self, standard_doc: StandardDocument) -> Dict[str, Any]:
        self.logger.info(f"Orchestrator: Beginning AI processing of standard: '{standard_doc.name}'")
        
        start_time_total = time.time()
        
        # Add document to vector DB. This is useful if agents need to search for context.
        # If agents are purely sequential and only operate on the passed text, this could be optional
        # or done selectively. For a comprehensive system, adding it is good practice.
        try:
            self.vector_db_manager.add_standard_document_to_db(standard_doc)
        except Exception as e:
            self.logger.error(f"Failed to add standard '{standard_doc.name}' to vector DB during processing: {e}", exc_info=True)
            # Decide if this is a critical failure or if processing can continue without it.
            # For now, we'll log and continue.

        # Execute the AI agent pipeline
        try:
            review_result = self.review_agent.execute(standard_doc)
            analysis_result = self.analysis_agent.execute(review_result)
            enhancement_result = self.enhancement_agent.execute(review_result, analysis_result)
            shariah_result = self.shariah_agent.execute(enhancement_result, review_result)
            validation_result = self.validation_agent.execute(enhancement_result, shariah_result)
            report_result = self.report_agent.execute(
                review_result, analysis_result, enhancement_result, 
                shariah_result, validation_result
            )
            # Visualization agent generates SPECS, not the image itself.
            visualization_specs_result = self.visualization_spec_agent.execute(
                enhancement_result, shariah_result, validation_result
            )
        except Exception as e:
            self.logger.error(f"Error during AI agent pipeline for standard '{standard_doc.name}': {e}", exc_info=True)
            # Return a partial result or raise an error to be handled by the view
            raise RuntimeError(f"AI agent pipeline failed for '{standard_doc.name}': {str(e)}") from e

        
        full_ai_output = {
            "standard_name": standard_doc.name, 
            "review": review_result, 
            "analysis": analysis_result,
            "enhancement": enhancement_result, 
            "shariah_assessment": shariah_result,
            "validation": validation_result, 
            "report": report_result, 
            "visualizations_specs": visualization_specs_result # Specs from the agent
        }
        
        self._save_ai_output_to_file(full_ai_output, suffix="ai_processing_output")
        
        end_time_total = time.time()
        self.logger.info(f"Orchestrator: Completed AI processing of standard: '{standard_doc.name}'. Total time: {end_time_total - start_time_total:.2f}s")
        return full_ai_output # This rich JSON is intended to be stored in the Django model
    
    def process_feedback_for_standard(
        self, 
        feedback_text: str, 
        standard_name: str, 
        enhancement_proposals_text: Optional[str] = None # Typically from stored AI result
        ) -> Dict[str, Any]:

        self.logger.info(f"Orchestrator: Processing stakeholder feedback for standard: '{standard_name}'")
        start_time_feedback = time.time()
        
        if enhancement_proposals_text is None:
            self.logger.warning(f"No enhancement proposals text provided for '{standard_name}' during feedback processing. Feedback agent might not perform optimally.")
            enhancement_proposals_text = "Enhancement proposals context not available for this feedback."

        try:
            feedback_analysis_result = self.feedback_agent.execute(
                feedback_text, 
                enhancement_proposals_text, 
                standard_name
            )
        except Exception as e:
            self.logger.error(f"Error during feedback agent execution for standard '{standard_name}': {e}", exc_info=True)
            raise RuntimeError(f"Feedback agent failed for '{standard_name}': {str(e)}") from e
            
        self._save_ai_output_to_file(feedback_analysis_result, suffix="feedback_analysis_output")
        
        end_time_feedback = time.time()
        self.logger.info(f"Orchestrator: Completed feedback processing for standard: '{standard_name}'. Time: {end_time_feedback - start_time_feedback:.2f}s")
        return feedback_analysis_result # This rich JSON is for the Feedback model
    
    def _save_ai_output_to_file(self, results_data: Dict[str, Any], suffix: str = "results") -> None:
        """Saves the provided dictionary of results to a JSON file."""
        standard_name = results_data.get("standard_name", "unknown_standard")
        # Sanitize standard_name for use in filename
        sanitized_name = re.sub(r'[^\w\-_\.]', '_', str(standard_name))
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        
        # Ensure OUTPUT_DIR from config exists
        os.makedirs(aicfg.OUTPUT_DIR, exist_ok=True)
        output_filename = f"{sanitized_name}_{suffix}_{timestamp}.json"
        output_path = os.path.join(aicfg.OUTPUT_DIR, output_filename)
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results_data, f, indent=2, ensure_ascii=False)
            self.logger.info(f"AI output successfully saved to: {output_path}")
        except Exception as e:
            self.logger.error(f"Failed to save AI output to {output_path}: {e}", exc_info=True)

    def search_vector_database(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Wraps the VectorDBManager's search method."""
        if not hasattr(self, 'vector_db_manager') or self.vector_db_manager is None:
            self.logger.error("VectorDBManager is not initialized. Cannot perform search.")
            return [] # Or raise an error
        return self.vector_db_manager.search_documents_in_db(query, top_k)

def load_sample_standard_document_data() -> StandardDocument:
    """
    Loads a predefined sample AAOIFI standard document for demonstration purposes.
    (Content copied from MAI.py)
    """
    sample_content = """
    AAOIFI Shariah Standard No. X: Murabahah to the Purchase Orderer

    1. Scope of the Standard
    This standard covers Murabahah to the Purchase Orderer transactions as practiced by Islamic financial institutions, including the conditions, procedures, rules, and modern applications. It does not cover simple Murabahah transactions that do not involve a prior promise to purchase.

    2. Definition of Murabahah to the Purchase Orderer
    Murabahah to the Purchase Orderer is a transaction where an Islamic financial institution (IFI) purchases an asset based on a promise from a customer to buy the asset from the institution on Murabahah terms (cost plus profit) after the institution has purchased it.

    3. Shariah Requirements for Murabahah to the Purchase Orderer
    3.1 The IFI must acquire ownership of the asset before selling it to the customer.
    3.2 The IFI must bear the risks of ownership during the period between purchasing the asset and selling it to the customer.
    3.3 The cost price and markup must be clearly disclosed to the customer.
    3.4 The customer's promise to purchase is morally binding but not legally enforceable as a sale contract.
    3.5 The Murabahah sale contract can only be executed after the IFI has acquired ownership of the asset.

    4. Procedures for Murabahah to the Purchase Orderer
    4.1 The customer identifies the asset they wish to purchase and requests the IFI to purchase it.
    4.2 The IFI and customer enter into a promise agreement, where the customer promises to purchase the asset after the IFI acquires it.
    4.3 The IFI purchases the asset from the supplier.
    4.4 The IFI informs the customer that it has acquired the asset and offers to sell it on Murabahah terms.
    4.5 The customer accepts the offer, and a Murabahah sale contract is executed.
    4.6 The customer pays the agreed price, either in installments or as a lump sum.

    5. Modern Applications and Issues
    5.1 Appointment of the customer as agent: The IFI may appoint the customer as its agent to purchase the asset on its behalf, provided that the customer acts in a genuine agency capacity.
    5.2 Third-party guarantees: Independent third parties may provide guarantees to protect against negligence or misconduct.
    5.3 Late payment: The IFI may require the customer to donate to charity in case of late payment, but may not benefit from these amounts.
    5.4 Rebate for early settlement: The IFI may voluntarily give a rebate for early settlement, but this cannot be stipulated in the contract.

    6. Shariah Rulings on Specific Murabahah Issues
    6.1 It is not permissible to roll over a Murabahah financing by extending the payment period in exchange for an increase in the amount owed.
    6.2 Currency exchange (sarf) must be completed before the Murabahah transaction when purchasing assets in a different currency.
    6.3 Conventional insurance on Murabahah assets should be avoided in favor of Takaful (Islamic insurance) when available.

    7. Documentation Requirements
    7.1 Promise document: Detailing the customer's promise to purchase the asset.
    7.2 Agency agreement (if applicable): Appointing the customer as agent for purchasing the asset.
    7.3 Murabahah sale contract: Documenting the actual sale transaction.
    7.4 Security documents: Including collateral, guarantees, or pledges to secure the payment.
    """
    logger.debug("Loading sample standard document data for demo.")
    return StandardDocument(name="Sample Murabahah Standard X (Django Demo)", content=sample_content)