import json
from django.conf import settings
from rest_access_policy import AccessPolicy


class AbstractAccessPolicy(AccessPolicy):
    group_prefix = "role:"
    policies = None

    @classmethod
    def load_policies(cls):
        """Load policies from the JSON file if not already loaded."""
        if cls.policies is None:
            policy_file_path = settings.POLICIES_FILE_PATH
            try:
                with open(policy_file_path, 'r') as f:
                    cls.policies = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError) as e:
                raise Exception(f"Error loading policies file: {e}")
        return cls.policies

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.statements = self.load_policies().get(
            self.__class__.__name__, {}).get("statements", [])

    def get_user_group_values(self, user):
        # Return the user's role code if user is authenticated and role exists,
        # else return an empty list
        return (
            [user.role.code]
            if user and user.is_authenticated and user.role
            else []
        )