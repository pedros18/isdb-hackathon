from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import StandardAnalysis, Feedback
from .serializers import StandardAnalysisSerializer, FeedbackSerializer
from .analyzer import analyze_standard_document, generate_feedback_response
import os

@api_view(['POST'])
def analyze_standard(request):
    if 'file' not in request.FILES:
        return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    pdf_file = request.FILES['file']
    
    # Save the file temporarily
    analysis = StandardAnalysis(
        standard_name="Analyzing...",
        pdf_file=pdf_file
    )
    analysis.save()
    
    # Process the PDF
    try:
        # Get the full path to the saved file
        pdf_path = analysis.pdf_file.path
        
        # Analyze the document
        results = analyze_standard_document(pdf_path)
        
        # Update the analysis object with results
        analysis.standard_name = results['standard_name']
        analysis.executive_summary = results['report']['executive_summary']
        analysis.clarity_improvements = results['enhancement']['clarity_improvements']
        analysis.modern_adaptations = results['enhancement']['modern_adaptations']
        analysis.save()
        
        # Return the results
        return Response(results)
    
    except Exception as e:
        # Delete the analysis object if there's an error
        analysis.delete()
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def submit_feedback(request):
    if not request.data:
        return Response({'error': 'No data provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        standard_name = request.data.get('standard_name', '')
        feedback_text = request.data.get('feedback', '')
        
        # Get or create analysis object
        analysis = StandardAnalysis.objects.filter(standard_name=standard_name).first()
        if not analysis:
            return Response({'error': 'Standard not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Generate response to feedback
        recommended_refinements = generate_feedback_response(feedback_text)
        
        # Create feedback object
        feedback = Feedback(
            standard_analysis=analysis,
            feedback_text=feedback_text,
            recommended_refinements=recommended_refinements
        )
        feedback.save()
        
        # Return the results
        return Response({
            'recommended_refinements': recommended_refinements
        })
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)