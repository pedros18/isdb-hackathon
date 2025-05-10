from django.urls import path
from . import views

urlpatterns = [
    path('analyze-standard', views.analyze_standard, name='analyze-standard'),
    path('submit-feedback', views.submit_feedback, name='submit-feedback'),
]