from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from core.models import DataLookup
from core.abstract import AbstractBaseModel


class Competition(AbstractBaseModel):
    name = models.CharField(
        max_length=255,
        verbose_name=_("name")
    )

    description = models.TextField(
        verbose_name=_("Description about the Competition")
    )
    
    min_entry_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Competition minimum entry fee")
    )

    max_entry_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.0,
        verbose_name=_("Competition maximum entry fee, 0 if not upper limit.")
    )
    
    max_players = models.IntegerField(
        default=1,
        verbose_name=_("Maximum number of participants, 0 for no limit.")
    )

    max_score_per_player = models.IntegerField(
        default=1
    )

    start_time = models.DateTimeField(
        verbose_name=_("Competition start time"),
        auto_now=False, auto_now_add=False
    )

    end_time = models.DateTimeField(
        verbose_name=_("Competition end time"),
        auto_now=False, auto_now_add=False,
        null=True,
        blank=True
    )
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="competitions",
        blank=True
    )

    type = models.ForeignKey(
        DataLookup,
        on_delete=models.RESTRICT,
        blank=True,
        related_name="+",
        limit_choices_to={'type': "competition_type"}
    )

    ranking_method = models.ForeignKey(
        DataLookup,
        on_delete=models.RESTRICT,
        blank=True,
        related_name="+",
        limit_choices_to={'type': "ranking_method"}
    )

    tiebreaker_rule = models.ForeignKey(
        DataLookup,
        on_delete=models.RESTRICT,
        blank=True,
        related_name="+",
        verbose_name=_(
            "Determines how ranking is resolved if two players have the same score"),
        limit_choices_to={'type': "tiebreaker_rule"}
    )

    class Meta:
        verbose_name = _("Competition")
        verbose_name_plural = _("Competitions")
        ordering = ("-created_at",)
        db_table = "competition"
        constraints = [
            models.UniqueConstraint(
                fields=["name"],
                condition=models.Q(name__isnull=False) & models.Q(deleted_at__isnull=True),
                name="competition_name_idx"
            )
        ]
        indexes = [
            models.Index(
                fields=["created_at"],
                name="competition_created_at_idx"
            ),
            models.Index(
                fields=["updated_at"],
                name="competition_updated_at_idx"
            ),
            models.Index(
                fields=["deleted_at"],
                name="competition_deleted_at_idx"
            )
        ]

    def __str__(self):
        return self.name
    
    @property
    def is_full(self):
        """
        Checks if the competition has reached the maximum allowed number of players.
        Returns True if the competition is full, False otherwise.
        """
        if self.max_players == 0:
            return False
        return self.entries.count() >= self.max_players


class CompetitionEntry(AbstractBaseModel):
    entry_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Competition entry fee")
    )

    competition = models.ForeignKey(
        Competition,
        on_delete=models.CASCADE,
        related_name="entries"
    )

    player = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="entries"
    )

    class Meta:
        verbose_name = _("Competition Entry")
        verbose_name_plural = _("Competition Entries")
        ordering = ("-created_at",)
        db_table = "competition_entry"
        constraints = [
            models.UniqueConstraint(
                fields=['competition', 'player'],
                name='unique_competition_entry')
        ]

    def __str__(self):
        return f"{self.player} in {self.competition}"


class Score(AbstractBaseModel):
    entry = models.ForeignKey(
        CompetitionEntry,
        on_delete=models.CASCADE,
        related_name="scores"
    )

    score = models.IntegerField(
        verbose_name=_("Submitted Score")
    )

    class Meta:
        verbose_name = _("Score")
        verbose_name_plural = _("Scores")
        ordering = ['-score']
        db_table = "score"

    def __str__(self):
        return f"{self.entry.player} - {self.score}"
