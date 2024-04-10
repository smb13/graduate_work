from faker import Faker

fake = Faker()


def generate_password(length: int = 12) -> str:
    return fake.password(length=length, special_chars=True, digits=True, upper_case=True, lower_case=True)
