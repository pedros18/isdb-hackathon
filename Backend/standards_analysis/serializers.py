from rest_framework import serializers
from .models import StandardAnalysis, Feedback

class StandardAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = StandardAnalysis
        fields = '__all__'

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'