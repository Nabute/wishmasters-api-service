from django.db.models import Max, Count
from games.models import Score


def get_leaderboard(competition_id: int, limit: int = 10):
    """
    Fetches the leaderboard for a given competition.
    """
    leaderboard_entries = (
        Score.objects.filter(entry__competition_id=competition_id)
        .values("entry__player_id", "entry__player__full_name")
        .annotate(
            highest_score=Max("score"),
            total_entries=Count("id")
        )
        .order_by("-highest_score")[:limit]
    )

    return [
        {
            "rank": index + 1,
            "player_id": entry["entry__player_id"],
            "player_name": entry["entry__player__full_name"],
            "highest_score": entry["highest_score"],
            "total_entries": entry["total_entries"],
        }
        for index, entry in enumerate(leaderboard_entries)
    ]
