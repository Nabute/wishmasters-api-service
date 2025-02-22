from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from core.viewset import AbstractModelViewSet
from core.enums import SystemSettingKey
from core.models import SystemSetting
from games.permissions import CompetitionAccessPolicy
from games.services import get_leaderboard

from games.models import Competition, CompetitionEntry, Score
from games.serializers import (
    CompetitionSerializer, CompetitionEntrySerializer, ScoreSerializer,
    CompetitionEntryResponseSerializer, LeaderboardSerializer
)


class CompetitionViewSet(AbstractModelViewSet):
    """
    ViewSet for managing competitions, including joining, score submissions, and leaderboard.
    """
    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer
    permission_classes = [permissions.IsAuthenticated  | permissions.AllowAny, CompetitionAccessPolicy]

    def perform_create(self, serializer):
        """
        Assigns the authenticated user as the creator of the competition.
        """
        serializer.save(created_by=self.request.user)

    @extend_schema(
        request=CompetitionEntrySerializer,
        responses=CompetitionEntryResponseSerializer
    )
    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        """
        Allows a user to join a competition if it's not full.
        """
        competition = self.get_object()

        entry_fee = request.data.get("entry_fee")

        entry_data = {
            "competition": competition.id,
            "entry_fee": entry_fee
        }

        serializer = CompetitionEntrySerializer(data=entry_data, context={'request': request})

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Successfully joined the competition!"}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def submit_score(self, request, pk=None):
        """
        Allows a player to submit a score for a competition.
        """
        competition = self.get_object()
        entry = CompetitionEntry.objects.filter(competition=competition, player=request.user).first()

        if not entry:
            return Response({'error': 'You must join the competition before submitting a score.'}, status=status.HTTP_400_BAD_REQUEST)

        score_serializer = ScoreSerializer(
            data={'entry': entry.id, 'score': request.data.get('score')},
            context={'request': request}
        )

        if score_serializer.is_valid():
            score_serializer.save()
            return Response({'message': 'Score submitted successfully!'}, status=status.HTTP_201_CREATED)
        
        return Response(score_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def leaderboard(self, request, pk=None):
        competition = self.get_object()

        leaderboard_size = SystemSetting.objects.get(
            key=SystemSettingKey.LEADERBOARD_SIZE.value
        ).current_value

        leaderboard_data = get_leaderboard(competition.id, limit=int(leaderboard_size))

        return Response(LeaderboardSerializer(leaderboard_data, many=True).data, status=status.HTTP_200_OK)
