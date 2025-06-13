from rest_framework import generics, permissions, filters, status
from .models import UserActivityLog
from .serializers import UserActivityLogSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.cache import cache
from django_filters.rest_framework import DjangoFilterBackend

class UserActivityLogCreateView(generics.CreateAPIView):
    serializer_class = UserActivityLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        cache.delete(f"user_logs_{self.request.user.id}")

class UserActivityLogListView(generics.ListAPIView):
    serializer_class = UserActivityLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    filterset_fields = ['action', 'timestamp']

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        cache_key = f"user_logs_{user_id}"
        data = cache.get(cache_key)
        if data:
            return data
        queryset = UserActivityLog.objects.filter(user_id=user_id)
        cache.set(cache_key, queryset, timeout=60)
        return queryset

class UserActivityStatusUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        try:
            log = UserActivityLog.objects.get(pk=pk, user=request.user)
        except UserActivityLog.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get('status')
        if new_status not in dict(UserActivityLog.STATUS_CHOICES):
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
        log.status = new_status
        log.save()
        return Response(UserActivityLogSerializer(log).data)
