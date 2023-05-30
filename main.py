import os
from check_in import GLaDOS_CheckIn


def handler(event, context):
    checkIn()
    return "Done"


def checkIn():
    COOKIES = os.getenv('COOKIES')
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    CHAT_ID = os.getenv('CHAT_ID')
    if COOKIES is None:
        raise EnvironmentError('Environment COOKIES not found!')
    if BOT_TOKEN is None:
        raise EnvironmentError('Environment BOT_TOKEN not found!')
    if CHAT_ID is None:
        raise EnvironmentError('Environment CHAT_ID not found!')
    GLaDOS_CheckIn(COOKIES, BOT_TOKEN, CHAT_ID).run()


if __name__ == '__main__':
    checkIn()
