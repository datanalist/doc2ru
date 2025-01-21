import os

from dotenv import load_dotenv

load_dotenv("../.env")

api_key = os.getenv("BOT_TOKEN")


if __name__ == "__main__":
    print()