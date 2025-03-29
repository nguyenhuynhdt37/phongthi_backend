import dotenv
import os

dotenv.load_dotenv()


def get_image_directory(path: str) -> str:
    return f"{os.getenv('BASE_URL')}/uploads/images/{path}"
