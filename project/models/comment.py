import uuid
from datetime import datetime


class Comment:
    def __init__(self, author_id: uuid, text: str):
        self.author_id: uuid = author_id
        self.text: str = text
        self.create_data: datetime = datetime.now()
        self.update_data: datetime = self.create_data
        self.like_count: int = 0

    def edit_comment(self, new_text: str):
        self.text = new_text
        self.update_data = datetime.now()

    def like(self):
        self.like_count += 1

    def dislike(self):
        self.like_count -= 1

    def __repr__(self) -> str:
        return f"<Comment by {self.author_id}>"
