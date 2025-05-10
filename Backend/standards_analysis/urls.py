from django.urls import path
from . import views

urlpatterns = [
    # Admin/Setup Endpoints
    path('admin/initialize-vector-db/', views.InitializeVectorDBView.as_view(), name='admin_init_db'),

    # AI System Endpoints
    path('process-pdf/', views.ProcessStandardPDFView.as_view(), name='process_pdf'),
    path('process-text/', views.ProcessStandardTextView.as_view(), name='process_text'),
    path('details/<int:id>/', views.StandardAnalysisDetailView.as_view(), name='analysis_detail'),
    path('run-demo/', views.RunDemoAIView.as_view(), name='run_demo_ai'),
    path('visualize/shariah-compliance/<int:analysis_id>/', views.VisualizeShariahComplianceView.as_view(), name='visualize_shariah'),
    path('search-db/', views.SearchVectorDBView.as_view(), name='search_vector_db'),
    path('submit-feedback/', views.SubmitFeedbackView.as_view(), name='submit_feedback'),

    # Endpoints for simpler analyzer.py (if implemented)
    # path('simple-analyze-pdf/', views.SimpleAnalyzePDFView.as_view(), name='simple_analyze_pdf'),
]