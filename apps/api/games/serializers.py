from rest_framework import serializers
from django.utils.timezone import now
from django.db.models import Max
from django.contrib.auth import get_user_model
from django.db import transaction
from games.models import Competition, CompetitionEntry, Score
from account.serializers import UserSerializer
from core.serializers import DataLookupSerializer
from core.models import DataLookup
from core.enums import CompetitionType, RankingMethod, TiebreakerRule


class BaseCompetitionSerializer(serializers.ModelSerializer):
    """
    Base Competition serializer containing shared fields and validation logic.
    """
    
    class Meta:
        model = Competition
        fields = [
            'id', 'name', 'min_entry_fee', 'max_entry_fee', 'max_players',
            'max_score_per_player', 'start_time', 'end_time', 'type',
            'ranking_method', 'tiebreaker_rule', 'created_by', 'created_at', 'updated_at'
        ]
    
    def validate(self, attrs):
        """
        Custom validation for Competition model fields.
        """

        min_entry_fee = attrs.get("min_entry_fee", 0)
        max_entry_fee = attrs.get("max_entry_fee", 0)
        max_players = attrs.get("max_players", 0)
        max_score_per_player = attrs.get("max_score_per_player", 0)
        start_time = attrs.get("start_time")
        end_time = attrs.get("end_time")

        # Ensure min_entry_fee and max_entry_fee are positive
        if min_entry_fee < 0:
            raise serializers.ValidationError(
                {"min_entry_fee": "Minimum entry fee must be a positive value."})

        if max_entry_fee < 0:
            raise serializers.ValidationError(
                {"max_entry_fee": "Maximum entry fee must be a positive value."})

        # Ensure max_entry_fee is greater than min_entry_fee (unless max_entry_fee is 0, meaning no limit)
        if max_entry_fee > 0 and max_entry_fee < min_entry_fee:
            raise serializers.ValidationError({
                "max_entry_fee": "Maximum entry fee must be greater than the minimum entry fee."
            })

        # Ensure max_players is a positive integer
        if max_players < 0:
            raise serializers.ValidationError(
                {"max_players": "Maximum number of players must be a positive integer."})

        # Ensure max_score_per_player is a positive integer
        if max_score_per_player < 1:
            raise serializers.ValidationError(
                {"max_score_per_player": "Maximum score per player must be at least 1."})

        # Ensure start_time is defined
        if not start_time:
            raise serializers.ValidationError(
                {"start_time": "Start time is required."})

        # Ensure start_time is before end_time if end_time is provided
        if end_time and start_time >= end_time:
            raise serializers.ValidationError({
                "end_time": "End time must be after the start time."
            })

        return attrs


class CompetitionResponseSerializer(BaseCompetitionSerializer):
    created_by = UserSerializer(read_only=True)
    type = DataLookupSerializer(read_only=True)
    ranking_method = DataLookupSerializer(read_only=True)
    tiebreaker_rule = DataLookupSerializer(read_only=True)

    total_players_joined = serializers.SerializerMethodField()
    current_leader = serializers.SerializerMethodField()
    current_user_rank = serializers.SerializerMethodField()
    can_submit_score = serializers.SerializerMethodField()
    has_joined = serializers.SerializerMethodField()

    class Meta(BaseCompetitionSerializer.Meta):
        fields = BaseCompetitionSerializer.Meta.fields + [
            "total_players_joined",
            "current_leader",
            "current_user_rank",
            "can_submit_score",
            "has_joined"
        ]

    def get_total_players_joined(self, obj):
        """
        Returns the total number of players who have joined the competition.
        """
        return obj.entries.count()

    def get_current_leader(self, obj):
        """
        Returns the player with the highest score.
        """
        top_score_entry = obj.entries.annotate(
            highest_score=Max("scores__score")
        ).order_by("-highest_score").first()

        if top_score_entry and top_score_entry.highest_score is not None:
            return {
                "id": top_score_entry.player.id,
                "name": top_score_entry.player.full_name,
                "score": top_score_entry.highest_score,
            }
        return None
    
    def get_current_user_rank(self, obj):
        """
        Returns the rank of the current authenticated user in the competition.
        - `null` if the user is not authenticated.
        - `null` if the user has not joined the competition.
        - Otherwise, returns the rank (1-based index).
        """
        request = self.context.get("request")
        if not request or not request.user or not request.user.is_authenticated:
            return None

        user = request.user

        # Check if the user has an entry in the competition
        user_entry = obj.entries.filter(player=user).first()
        if not user_entry:
            # User has not joined the competition
            return None 

        # Get the ranking of all players based on their highest score
        ranked_players = (
            obj.entries.annotate(highest_score=Max("scores__score"))
            .filter(highest_score__isnull=False)  # Exclude players with no score
            .order_by("-highest_score")  # Order by highest score descending
        )

        # Create a ranking list with 1-based index
        ranking = {entry.player.id: rank + 1 for rank, entry in enumerate(ranked_players)}

        # Return the user's rank if available
        return ranking.get(user.id)

    def get_can_submit_score(self, obj):
        """
        Determines whether the authenticated user can submit a score.
        """
        request = self.context.get("request")
        if not request or not request.user or not request.user.is_authenticated:
            return False

        user = request.user

        user_entry = obj.entries.filter(player=user).first()
        if not user_entry:
            return False

        has_submitted_score = user_entry.scores.exists()

        if not has_submitted_score:
            return True

        multi_attempt_type = DataLookup.objects.get(value=CompetitionType.MULTIPLE_ATTEMPTS.value)

        if obj.type == multi_attempt_type:
            return True

        return False

    def get_has_joined(self, obj):
        """
        Determines whether the authenticated user has joined the competition.
        """
        request = self.context.get("request")

        if not request or not request.user or not request.user.is_authenticated:
            return False

        user = request.user

        return obj.entries.filter(player=user).exists() 

class CompetitionSerializer(BaseCompetitionSerializer):

    def to_representation(self, instance):
        return CompetitionResponseSerializer(
            instance, context=self.context).to_representation(instance)
    
    def create(self, validated_data):
        request = self.context.get("request", None)

        if request and request.user:
            validated_data["created_by"] = request.user
        
        if "type" not in validated_data:
            validated_data["type"] = DataLookup.objects.filter(
                type=CompetitionType.TYPE.value, is_default=True).first()

        if "ranking_method" not in validated_data:
            validated_data["ranking_method"] = DataLookup.objects.filter(
                type=RankingMethod.TYPE.value, is_default=True).first()

        if "tiebreaker_rule" not in validated_data:
            validated_data["tiebreaker_rule"] = DataLookup.objects.filter(
                type=TiebreakerRule.TYPE.value, is_default=True).first()

        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.description = validated_data.get("description", instance.description)
        instance.min_entry_fee = validated_data.get("min_entry_fee", instance.min_entry_fee)
        instance.max_entry_fee = validated_data.get("max_entry_fee", instance.max_entry_fee)
        instance.max_players = validated_data.get("max_players", instance.max_players)
        instance.max_score_per_player = validated_data.get("max_score_per_player", instance.max_score_per_player)
        instance.start_time = validated_data.get("start_time", instance.start_time)
        instance.end_time = validated_data.get("end_time", instance.end_time)

        # Ensure type, ranking_method, and tiebreaker_rule do not get overridden with None
        instance.type = validated_data.get("type", instance.type)
        instance.ranking_method = validated_data.get("ranking_method", instance.ranking_method)
        instance.tiebreaker_rule = validated_data.get("tiebreaker_rule", instance.tiebreaker_rule)

        instance.save()
        return instance


####################  COMPETITION ENTRY  ####################

class BaseCompetitionEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = CompetitionEntry
        fields = ['id', 'entry_fee', 'competition', 'player', 'created_at', 'updated_at']
        read_only_fields = ['player']

    def validate(self, attrs):
        """
        Common validation logic for all CompetitionEntry serializers.
        """
        entry_fee = attrs.get("entry_fee", 0)
        competition = attrs.get("competition")

        if entry_fee < 0:
            raise serializers.ValidationError({"entry_fee": "Entry fee must be a positive value."})

        if competition:
            if entry_fee < competition.min_entry_fee:
                raise serializers.ValidationError({
                    "entry_fee": "Entry fee must be at least the competition’s minimum entry fee."
                })
            if competition.max_entry_fee > 0 and entry_fee > competition.max_entry_fee:
                raise serializers.ValidationError({
                    "entry_fee": "Entry fee cannot exceed the competition’s maximum entry fee."
                })

            if competition.is_full:
                raise serializers.ValidationError({
                    "competition": "This competition is full and cannot accept more entries."
                })

        return attrs
 

class CompetitionEntryResponseSerializer(BaseCompetitionEntrySerializer):
    competition = serializers.StringRelatedField(read_only=True)
    player = UserSerializer(read_only=True)


class CompetitionEntrySerializer(BaseCompetitionEntrySerializer):
    class Meta:
        model = CompetitionEntry
        fields = ['id', 'entry_fee', 'competition']

    def to_representation(self, instance):
        """
        Ensure response is serialized properly using the response serializer.
        """
        return CompetitionEntryResponseSerializer(instance, context=self.context).data
    
    def check_duplicate_entry(self, competition, player):
        """
        Check if the player is already registered in a SINGLE_ATTEMPT competition.
        """
        if CompetitionEntry.objects.filter(
                competition=competition,
                player=player,
                competition__type__value=CompetitionType.SINGLE_ATTEMPT.value).exists():
            raise serializers.ValidationError({"player": "Player is already registered in this competition."})

    def create(self, validated_data):
        """
        Assign player from request and prevent duplicate competition entries.
        """
        request = self.context.get("request")

        if request and request.user:
            validated_data["player"] = request.user

        competition = validated_data["competition"]
        player = validated_data["player"]

        self.check_duplicate_entry(competition, player)

        return super().create(validated_data)


####################  SCORE  ####################


class BaseScoreSerializer(serializers.ModelSerializer):
    """
    Base serializer containing shared fields and validation logic for Score.
    """

    class Meta:
        model = Score
        fields = ['id', 'entry', 'score', 'created_at', 'updated_at']

    def validate(self, attrs):
        """
        Shared validation logic for Score.
        """
        entry = attrs.get("entry")
        score = attrs.get("score")

        # Ensure the score is a positive integer
        if score < 0:
            raise serializers.ValidationError(
                {"score": "Score must be a positive integer."})

        competition = entry.competition
        player = entry.player

        # Ensure the player submitting the score is the one who registered
        request = self.context.get("request", None)
        if request and request.user != player:
            raise serializers.ValidationError(
                {"player": "You are not allowed to submit a score for this entry."})

        # Ensure scores cannot be submitted after the competition's end_time
        if competition.end_time and now() > competition.end_time:
            raise serializers.ValidationError(
                {"competition": "The competition has ended. Scores cannot be submitted."})

        # Ensure the player hasn’t exceeded the max_score_per_player limit
        if Score.objects.filter(entry__competition=competition, entry__player=player).count() >= competition.max_score_per_player:
            raise serializers.ValidationError(
                {"score": "You have reached the maximum number of score submissions allowed in this competition."}
            )

        return attrs
    

class ScoreResponseSerializer(BaseScoreSerializer):
    entry = serializers.StringRelatedField(read_only=True)


class ScoreSerializer(BaseScoreSerializer):

    def to_representation(self, instance):
        return ScoreResponseSerializer(
            instance, context=self.context
        ).to_representation(instance)

    def create(self, validated_data):
        return super().create(validated_data)

    def update(self, instance, validated_data):
        instance.score = validated_data.get("score", instance.score)
        instance.save()
        return instance


####################  LEADERBOARD  ####################


class LeaderboardSerializer(serializers.Serializer):
    """
    Serializer for representing the leaderboard.
    """
    rank = serializers.IntegerField()
    player_id = serializers.IntegerField()
    player_name = serializers.CharField()
    highest_score = serializers.IntegerField()
    total_entries = serializers.IntegerField()
