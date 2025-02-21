from django.contrib import admin
from games.models import Competition, CompetitionEntry, Score
from core.admin import BaseModelAdmin


@admin.register(Competition)
class CompetitionAdmin(BaseModelAdmin):
    """
    Admin configuration for the Competition model.
    """
    list_display = ("name", "type", "max_players", "start_time", "end_time", "is_full", "created_by")
    list_filter = ("type", "ranking_method", "tiebreaker_rule", "start_time")
    search_fields = ("name", "description", "created_by__email")
    ordering = ("-created_at",)
    readonly_fields = ("is_full",)

    fieldsets = (
        ("Basic Info", {
            "fields": ("name", "description", "type", "ranking_method", "tiebreaker_rule", "created_by")
        }),
        ("Rules & Limits", {
            "fields": ("min_entry_fee", "max_entry_fee", "max_players", "max_score_per_player")
        }),
        ("Time Settings", {
            "fields": ("start_time", "end_time")
        }),
        ("Status", {
            "fields": ("is_full",)
        }),
    )


@admin.register(CompetitionEntry)
class CompetitionEntryAdmin(BaseModelAdmin):
    """
    Admin configuration for the CompetitionEntry model.
    """
    list_display = ("competition", "player", "entry_fee", "created_at")
    list_filter = ("competition", "player")
    search_fields = ("competition__name", "player__email")
    ordering = ("-created_at",)

    fieldsets = (
        ("Competition Entry Details", {
            "fields": ("competition", "player", "entry_fee")
        }),
    )


@admin.register(Score)
class ScoreAdmin(BaseModelAdmin):
    """
    Admin configuration for the Score model.
    """
    list_display = ("entry", "score", "created_at")
    list_filter = ("entry__competition", "score")
    search_fields = ("entry__competition__name", "entry__player__email")
    ordering = ("-score", "-created_at")

    fieldsets = (
        ("Score Details", {
            "fields": ("entry", "score")
        }),
    )
