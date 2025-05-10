from django.db import models

class StandardAnalysis(models.Model):
    standard_name = models.CharField(max_length=255)
    upload_date = models.DateTimeField(auto_now_add=True)
    pdf_file = models.FileField(upload_to='pdfs/')
    
    # Analysis results
    executive_summary = models.TextField(null=True, blank=True)
    clarity_improvements = models.TextField(null=True, blank=True)
    modern_adaptations = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return self.standard_name

class Feedback(models.Model):
    standard_analysis = models.ForeignKey(StandardAnalysis, on_delete=models.CASCADE, related_name='feedbacks')
    feedback_text = models.TextField()
    submitted_date = models.DateTimeField(auto_now_add=True)
    recommended_refinements = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return f"Feedback for {self.standard_analysis.standard_name}"