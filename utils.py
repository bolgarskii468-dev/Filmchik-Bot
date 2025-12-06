import os

ADMINS_DIR = "admins"

def is_admin(user_id: int) -> bool:
    return os.path.exists(f"{ADMINS_DIR}/{user_id}.txt")
