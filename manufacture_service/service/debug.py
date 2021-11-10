from dotenv import load_dotenv
from app import create_app


if __name__ == '__main__':
    load_dotenv()
    app = create_app()

# TODO Переделать (файл запуска локального сервера для дебага)
