from models.user import User


def select_top_users_by_rate(users: list[User], top_size: int) -> list[User]:
    sorted_users = sorted(users, key=lambda x: x.rate, reverse=True)
    return sorted_users[:top_size]
