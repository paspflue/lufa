from lufa.repository.user_repository import User, UserRepository


class TestUserRepository:
    def test_get_user(self, user_repository: UserRepository):
        new_user: User = {"distinguished_name": "new_user_dn", "username": "new_user", "data": {"more": "data"}}

        assert user_repository.get_user(new_user["distinguished_name"]) is None
        user_repository.save_user(**new_user)

        get_user = user_repository.get_user(new_user["distinguished_name"])

        # for postgres typeof(get_user) == RealDictRow
        assert get_user is not None
        assert dict(get_user) == dict(new_user)
