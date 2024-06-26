# app/models/user.py
from datetime import datetime

from mongoengine import Document, StringField, URLField, EmailField, DateTimeField


class User(Document):
    google_id = StringField(required=True, primary_key=True)
    email = EmailField(required=True, unique=True)
    name = StringField(required=True, max_length=50)
    avatar_url = URLField(required=True)

    created_at = DateTimeField(default=datetime.utcnow)

    meta = {'collection': 'users'}

    @classmethod
    def create_user(cls, google_id, email, name, avatar_url):
        """
        Create a new user with the given information.
        :param google_id: Google ID of the user.
        :param email: Email address of the user.
        :param name: Name of the user.
        :param avatar_url: Photo URL of the user.
        """
        try:
            user = cls(
                google_id=google_id,
                email=email,
                name=name,
                avatar_url=avatar_url
            )
            user.save()
            return user
        except Exception as e:
            print(e)
            return None

    @classmethod
    def get_user_by_email(cls, email):
        """
        Retrieve a user by their email address.
        :param email: Email address of the user.
        :return: User object if found, None otherwise.
        """
        return cls.objects(email=email).first()