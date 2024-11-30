import uuid


class User:
    def __init__(self, name: str):
        self.id: uuid = uuid.uuid4()
        self.name: str = name
        self.comments_count: int = 0
        self.rate: int = 0
        self.is_banned: bool = False

    def edit_name(self, new_name: str):
        self.name = new_name

    def increment_rate(self):
        self.rate += 1

    def ban_user(self):
        self.is_banned = True

    def unban_user(self):
        self.is_banned = False

    def __repr__(self) -> str:
        return f"<User {self.name}>"
