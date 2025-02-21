import enum


class SystemSettingKey(enum.Enum):
    LEADERBOARD_SIZE = "leaderboard_size"


class AccountStateType(enum.Enum):
    TYPE = "account_state"

    ACTIVE = "account_state_active"
    SUSPENDED = "account_state_suspended"

class CompetitionType(enum.Enum):
    TYPE = "competition_type"

    SINGLE_ATTEMPT = "competition_type_single_attempt"
    MULTIPLE_ATTEMPTS = "competition_type_multiple_attempts"

class RankingMethod(enum.Enum):
    TYPE = "ranking_method"

    HIGHEST_SCORE = "ranking_method_highest_score"
    AVERAGE_SCORE = "ranking_method_average_score"
    CUMULATIVE_SCORE = "ranking_method_cumulative_score"

class TiebreakerRule(enum.Enum):
    TYPE = "tiebreaker_rule"

    FIRST_TO_REACH = "tiebreaker_rule_first_to_reach"
    LATEST_SUBMISSION = "tiebreaker_rule_latest_submission"