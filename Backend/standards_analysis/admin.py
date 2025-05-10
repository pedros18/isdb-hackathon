from django.contrib import admin
from .models import StandardAnalysis, Feedback

@admin.register(StandardAnalysis)
class StandardAnalysisAdmin(admin.ModelAdmin):
    list_display = ('standard_name', 'upload_date')
    search_fields = ('standard_name',)

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('standard_analysis', 'submitted_date')
    search_fields = ('feedback_text', 'standard_analysis__standard_name')