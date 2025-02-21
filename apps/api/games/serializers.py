from rest_framework import serializers
from django.utils.timezone import now
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

    def validate(self, attrs):
        entry_fee = attrs.get("entry_fee", 0)
        competition = attrs.get("competition")

        # Ensure entry fee is positive
        if entry_fee < 0:
            raise serializers.ValidationError({"entry_fee": "Entry fee must be a positive value."})

        # Ensure the competition allows this entry fee
        if competition:
            if entry_fee < competition.min_entry_fee:
                raise serializers.ValidationError({
                    "entry_fee": "Entry fee must be at least the competition’s minimum entry fee."
                })
            if competition.max_entry_fee > 0 and entry_fee > competition.max_entry_fee:
                raise serializers.ValidationError({
                    "entry_fee": "Entry fee cannot exceed the competition’s maximum entry fee."
                })

        return attrs
    

class CompetitionEntryResponseSerializer(BaseCompetitionEntrySerializer):
    competition = serializers.StringRelatedField(read_only=True)
    player = UserSerializer(read_only=True)


class CompetitionEntrySerializer(BaseCompetitionEntrySerializer):

    def to_representation(self, instance):
        return CompetitionEntryResponseSerializer(
            instance, context=self.context
        ).to_representation(instance)
    
    def validate(self, attrs):
        """
        Validate competition entry before saving.
        """
        competition = attrs.get("competition")

        if competition.is_full:
            raise serializers.ValidationError(
                {"competition": "This competition has reached the maximum number of players and cannot accept more entries."}
            )

        return super().validate(attrs)

    def create(self, validated_data):
        """
        Create a new CompetitionEntry instance while ensuring constraints.
        """
        request = self.context.get("request", None)

        # Assign player from request if available
        if request and request.user:
            validated_data["player"] = request.user

        # Ensure the player is not already registered in the competition
        competition = validated_data["competition"]
        player = validated_data["player"]

        if CompetitionEntry.objects.filter(competition=competition, player=player).exists():
            raise serializers.ValidationError(
                {"player": "Player is already registered in this competition."}
            )

        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Update an existing CompetitionEntry instance while ensuring values are properly managed.
        """
        instance.entry_fee = validated_data.get("entry_fee", instance.entry_fee)

        instance.save()
        return instance


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
        if competition.end_time and now().time() > competition.end_time:
            raise serializers.ValidationError(
                {"competition": "The competition has ended. Scores cannot be submitted."})

        # Ensure the player hasn’t exceeded the max_score_per_player limit
        if competition.scores.filter(entry__player=player).count() >= competition.max_score_per_player:
            raise serializers.ValidationError(
                {"score": "You have reached the maximum number of score submissions allowed in this competition."})

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
