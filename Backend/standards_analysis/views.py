import logging
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from .models import StandardAnalysis, Feedback
from .serializers import (
    StandardAnalysisSerializer, StandardAnalysisCreateSerializer, StandardTextProcessInputSerializer,
    FeedbackSerializer, FeedbackInputSerializer, SearchInputSerializer, AdminActionSerializer
)
from .services.ai_orchestration import AIOperationsOrchestrator, StandardDocument, load_sample_standard_document_data
from .services.visualization_generator import generate_shariah_compliance_chart_image
from .services.pdf_processor import (
    extract_text_from_pdf_pypdf2, clean_document_text,
    process_all_pdfs_from_input_folder_and_build_db
)
from .services.ai_config import update_ai_config_db_directory # For admin task

# For tasks (Celery or Django Background Tasks)
# from .tasks import process_standard_analysis_task # Example if using Celery

logger = logging.getLogger('standards_analysis.views')

# Get the AI Orchestrator instance (singleton-like)
ai_orchestrator = AIOperationsOrchestrator.get_instance()


class InitializeVectorDBView(APIView):
    """
    Admin endpoint to process all PDFs from the configured input folder
    and build/rebuild the vector database.
    WARNING: This can be a long-running task. Consider background processing.
    """
    def post(self, request, *args, **kwargs):
        serializer = AdminActionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        force_recreate = serializer.validated_data.get('force_recreate', False)
        logger.info(f"Admin request to initialize vector DB. Force recreate: {force_recreate}")

        try:
            # This is a synchronous call, might timeout for many PDFs
            client = process_all_pdfs_from_input_folder_and_build_db(force_recreate=force_recreate)
            if client:
                # If DB path changed, re-initialize orchestrator to pick up new path for its VectorDBManager
                from .services.ai_config import aicfg # get current path
                if force_recreate: # Path would have changed
                    global ai_orchestrator
                    ai_orchestrator = AIOperationsOrchestrator.reinitialize_instance()
                    logger.info("AI Orchestrator re-initialized due to DB recreation.")
                
                return Response({
                    "message": "Vector DB initialization process completed.",
                    "db_path": str(aicfg.DB_DIRECTORY), # Show current DB path
                    "collection_name": str(aicfg.COLLECTION_NAME)
                }, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Failed to initialize vector DB or no PDFs found."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"Error initializing vector DB: {e}", exc_info=True)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProcessStandardPDFView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        create_serializer = StandardAnalysisCreateSerializer(data=request.data)
        if not create_serializer.is_valid():
            logger.warning(f"ProcessStandardPDFView validation error: {create_serializer.errors}")
            return Response(create_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Save the StandardAnalysis instance first to get an ID and save the file
        analysis_instance = create_serializer.save(status='PENDING')
        logger.info(f"Created StandardAnalysis instance {analysis_instance.id} for PDF: {analysis_instance.pdf_file.name}")

        try:
            analysis_instance.status = 'PROCESSING'
            analysis_instance.save()

            pdf_path = analysis_instance.pdf_file.path
            raw_text = extract_text_from_pdf_pypdf2(pdf_path)
            if not raw_text:
                analysis_instance.status = 'FAILED'
                analysis_instance.error_message = "Could not extract text from PDF."
                analysis_instance.save()
                return Response({"error": "Could not extract text from PDF."}, status=status.HTTP_400_BAD_REQUEST)
            
            cleaned_text = clean_document_text(raw_text)
            doc_to_process = StandardDocument(name=analysis_instance.standard_name, content=cleaned_text)
            
            # Synchronous call (consider Celery for long AI processing)
            ai_results_dict = ai_orchestrator.process_uploaded_standard(doc_to_process)
            
            analysis_instance.ai_processing_result_json = ai_results_dict
            # Populate specific fields from the AI JSON if desired for easier access
            analysis_instance.executive_summary = ai_results_dict.get("report", {}).get("executive_summary", "")
            # ... populate other fields like clarity_improvements, modern_adaptations from ai_results_dict ...
            
            analysis_instance.status = 'COMPLETED'
            analysis_instance.save()
            
            # Return the full analysis instance data
            full_serializer = StandardAnalysisSerializer(analysis_instance, context={'request': request})
            return Response(full_serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error processing PDF for StandardAnalysis {analysis_instance.id}: {e}", exc_info=True)
            analysis_instance.status = 'FAILED'
            analysis_instance.error_message = str(e)
            analysis_instance.save()
            return Response({"error": f"Failed to process PDF: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ProcessStandardTextView(APIView):
     def post(self, request, *args, **kwargs):
        input_serializer = StandardTextProcessInputSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response(input_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = input_serializer.validated_data
        standard_name = data['standard_name']
        standard_content = data['standard_content']
        
        # Create a StandardAnalysis record (without a PDF file for text input)
        analysis_instance = StandardAnalysis.objects.create(
            standard_name=standard_name,
            status='PROCESSING'
        )
        logger.info(f"Created StandardAnalysis instance {analysis_instance.id} for text input: {standard_name}")

        try:
            doc_to_process = StandardDocument(name=standard_name, content=standard_content)
            ai_results_dict = ai_orchestrator.process_uploaded_standard(doc_to_process)
            
            analysis_instance.ai_processing_result_json = ai_results_dict
            analysis_instance.executive_summary = ai_results_dict.get("report", {}).get("executive_summary", "")
            # ... populate other fields ...
            analysis_instance.status = 'COMPLETED'
            analysis_instance.save()

            full_serializer = StandardAnalysisSerializer(analysis_instance, context={'request': request})
            return Response(full_serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error processing text for StandardAnalysis {analysis_instance.id}: {e}", exc_info=True)
            analysis_instance.status = 'FAILED'
            analysis_instance.error_message = str(e)
            analysis_instance.save()
            return Response({"error": f"Failed to process text: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class StandardAnalysisDetailView(generics.RetrieveAPIView):
    queryset = StandardAnalysis.objects.all()
    serializer_class = StandardAnalysisSerializer
    lookup_field = 'id'

class RunDemoAIView(APIView):
    def post(self, request, *args, **kwargs):
        logger.info("Running AI Demo...")
        try:
            sample_doc = load_sample_standard_document_data() # From ai_orchestration
            
            # Create a dummy StandardAnalysis record for the demo if you want to show it in list
            # Or just return the AI output without saving to DB for demo
            ai_results_dict = ai_orchestrator.process_uploaded_standard(sample_doc)
            
            # To make it like other processing endpoints, create a temporary instance (not saved to DB usually for demo)
            # or return a structure that matches ProcessingResult from FastAPI
            demo_result_payload = {
                "id": None, "standard_name": sample_doc.name, "upload_date": None,
                "pdf_file": None, "pdf_file_url": None, "status": "DEMO_COMPLETED", "error_message": None,
                "executive_summary": ai_results_dict.get("report", {}).get("executive_summary", ""),
                "clarity_improvements": ai_results_dict.get("enhancement", {}).get("clarity_improvements", ""),
                "modern_adaptations": ai_results_dict.get("enhancement", {}).get("modern_adaptations", ""),
                "ai_processing_result_json": ai_results_dict,
                "analyzer_chart_data_json": None
            }
            return Response(demo_result_payload, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error running AI demo: {e}", exc_info=True)
            return Response({"error": f"Demo failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VisualizeShariahComplianceView(APIView):
    def get(self, request, analysis_id, *args, **kwargs):
        analysis_instance = get_object_or_404(StandardAnalysis, id=analysis_id)
        if not analysis_instance.ai_processing_result_json:
            return Response({"error": "AI processing result not found for this analysis."}, status=status.HTTP_404_NOT_FOUND)

        shariah_assessment_data = analysis_instance.ai_processing_result_json.get("shariah_assessment")
        if not shariah_assessment_data:
            return Response({"error": "Shariah assessment data not found in AI results."}, status=status.HTTP_404_NOT_FOUND)

        try:
            image_bytes = generate_shariah_compliance_chart_image(
                shariah_assessment_data,
                analysis_instance.standard_name
            )
            if not image_bytes:
                return Response({"error": "Could not generate Shariah compliance chart. Data might be insufficient."}, status=status.HTTP_404_NOT_FOUND)
            
            return HttpResponse(image_bytes, content_type="image/png")
        except Exception as e:
            logger.error(f"Error generating Shariah compliance chart for analysis {analysis_id}: {e}", exc_info=True)
            return Response({"error": f"Failed to generate chart: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SearchVectorDBView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = SearchInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        query = serializer.validated_data['query']
        top_k = serializer.validated_data['top_k']
        logger.info(f"Searching vector DB for: '{query}', top_k={top_k}")
        try:
            search_results = ai_orchestrator.search_vector_database(query, top_k)
            return Response(search_results, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error during vector DB search: {e}", exc_info=True)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SubmitFeedbackView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = FeedbackInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        analysis_id = data['standard_analysis_id']
        feedback_text = data['feedback_text']
        
        analysis_instance = get_object_or_404(StandardAnalysis, id=analysis_id)
        if not analysis_instance.ai_processing_result_json:
            return Response({"error": "Cannot submit feedback. Original AI analysis result not found."}, status=status.HTTP_404_NOT_FOUND)

        # Extract enhancement proposals text from the stored AI result
        enhancement_proposals_text = analysis_instance.ai_processing_result_json.get("enhancement", {}).get("enhancement_proposals")

        try:
            ai_feedback_results = ai_orchestrator.process_feedback_for_standard(
                feedback_text=feedback_text,
                standard_name=analysis_instance.standard_name,
                enhancement_proposals_text=enhancement_proposals_text
            )
            
            feedback_instance = Feedback.objects.create(
                standard_analysis=analysis_instance,
                feedback_text=feedback_text,
                ai_feedback_analysis_json=ai_feedback_results
            )
            
            feedback_serializer = FeedbackSerializer(feedback_instance)
            return Response(feedback_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error processing feedback for analysis {analysis_id}: {e}", exc_info=True)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# --- Views for analyzer.py (Simpler, non-AI version) ---
# If you want to expose the simpler analyzer.py functionality:
from .analyzer import analyze_standard_document as simple_analyze_pdf, generate_feedback_response as simple_feedback_response

class SimpleAnalyzePDFView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        # This view would use functions from analyzer.py
        # It needs pdf_file and standard_name similar to ProcessStandardPDFView
        # For simplicity, I'm omitting the full implementation, but it would:
        # 1. Get standard_name and pdf_file from request.
        # 2. Save PDF and create a StandardAnalysis record.
        # 3. Call `simple_analyze_pdf(pdf_path)`.
        # 4. Populate StandardAnalysis fields like `executive_summary`, `clarity_improvements`,
        #    `modern_adaptations`, and `analyzer_chart_data_json` from the result.
        # 5. Return serialized StandardAnalysis.
        # Note: analyzer.py uses pytesseract which requires Tesseract OCR installed.
        return Response({"message": "Simple PDF analysis endpoint (using analyzer.py) - placeholder."}, status=status.HTTP_501_NOT_IMPLEMENTED)