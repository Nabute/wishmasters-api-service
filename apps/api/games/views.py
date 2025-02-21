from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from core.viewset import AbstractModelViewSet
from core.enums import SystemSettingKey
from core.models import SystemSetting

from games.models import Competition, CompetitionEntry, Score
from games.serializers import (
    CompetitionSerializer, CompetitionEntrySerializer, ScoreSerializer
)


class CompetitionViewSet(AbstractModelViewSet):
    """
    ViewSet for managing competitions, including joining, score submissions, and leaderboard.
    """
    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """
        Assigns the authenticated user as the creator of the competition.
        """
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        """
        Allows a user to join a competition if it's not full.
        """
        competition = self.get_object()

        entry_serializer = CompetitionEntrySerializer(
            data={'competition': competition.id, 'player': request.user.id, 'entry_fee': 0},
            context={'request': request}
        )

        if entry_serializer.is_valid():
            entry_serializer.save()
            return Response({'message': 'Successfully joined the competition!'}, status=status.HTTP_201_CREATED)
        
        return Response(entry_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
        """
        Retrieves the top LEADERBOARD_SIZE scores for a competition.
        """
        competition = self.get_object()
        leaderboard_response_count = SystemSetting.objects.get(
            key=SystemSettingKey.LEADERBOARD_SIZE.value
        ).current_value
        top_scores = Score.objects.filter(
            entry__competition=competition).order_by(
                '-score')[:int(leaderboard_response_count)]
        return Response(ScoreSerializer(top_scores, many=True).data, status=status.HTTP_200_OK)
