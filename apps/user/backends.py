from django.contrib.auth.backends import ModelBackend


class AuthBackend(ModelBackend):
    def user_can_authenticate(self, user) -> bool:
        return not user.is_deleted
