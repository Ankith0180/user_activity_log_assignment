from rest_framework import serializers
from .models import UserActivityLog

class UserActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserActivityLog
        fields = '__all__'
        read_only_fields = ['user', 'timestamp']
