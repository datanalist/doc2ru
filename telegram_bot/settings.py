# from environs import Env
from dataclasses import dataclass

@dataclass
class Bots:
    bot_token: str

@dataclass
class Settings:
    bots: Bots

def get_settings(api_token: str):

    return Settings(
        bots=Bots(
            bot_token=api_token
        )
    )

# settings = get_settings('telegram_bot/env')