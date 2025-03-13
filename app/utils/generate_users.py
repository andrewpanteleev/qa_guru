from faker import Faker

from app.database.users import create_user
from app.models.User import User


def generate_users(num_users):
    fake = Faker()

    for i in range(1, num_users + 1):
        user = User(
            email=fake.email(),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            avatar=fake.image_url()
        )


        create_user(user)