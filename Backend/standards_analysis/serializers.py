from rest_framework import serializers
from .models import StandardAnalysis, Feedback

class StandardAnalysisSerializer(serializers.ModelSerializer):
    pdf_file_url = serializers.SerializerMethodField()

    class Meta:
        model = StandardAnalysis
        fields = [
            'id', 'standard_name', 'upload_date', 'pdf_file', 'pdf_file_url',
            'status', 'error_message',
            'executive_summary', 'clarity_improvements', 'modern_adaptations', # populated from AI
            'ai_processing_result_json', # Full AI output
            'analyzer_chart_data_json' # If using analyzer.py's chart data
        ]
        read_only_fields = ('id', 'upload_date', 'status', 'error_message', 'pdf_file_url',
                            'executive_summary', 'clarity_improvements', 'modern_adaptations',
                            'ai_processing_result_json', 'analyzer_chart_data_json')

    def get_pdf_file_url(self, obj):
        request = self.context.get('request')
        if obj.pdf_file and request:
            return request.build_absolute_uri(obj.pdf_file.url)
        return None

class StandardAnalysisCreateSerializer(serializers.ModelSerializer):
    # Used for creating via PDF upload
    class Meta:
        model = StandardAnalysis
        fields = ['standard_name', 'pdf_file'] # Only these are needed for creation

class StandardTextProcessInputSerializer(serializers.Serializer):
    standard_name = serializers.CharField(max_length=255)
    standard_content = serializers.CharField()

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'
        read_only_fields = ('id', 'submitted_date', 'ai_feedback_analysis_json')

class FeedbackInputSerializer(serializers.Serializer):
    standard_analysis_id = serializers.IntegerField()
    feedback_text = serializers.CharField()

class SearchInputSerializer(serializers.Serializer):
    query = serializers.CharField()
    top_k = serializers.IntegerField(default=5, min_value=1, max_value=20)

class AdminActionSerializer(serializers.Serializer): # For admin actions like DB init
    force_recreate = serializers.BooleanField(default=False)