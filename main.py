import os
from check_in import GLaDOS_CheckIn


def handler(event, context):
    checkIn()
    return "Done"


def checkIn():
    COOKIES = os.getenv('COOKIES')
    # BOT_TOKEN = os.getenv('BOT_TOKEN')
    # CHAT_ID = os.getenv('CHAT_ID')
    app_id = os.environ["APP_ID"]
    app_secret = os.environ["APP_SECRET"]
    user_id = os.environ["USER_ID"]
    template_id_s = os.environ["TEMPLATE_ID_S"]
    template_id_e = os.environ["TEMPLATE_ID_E"]

    if COOKIES is None:
        raise EnvironmentError('Environment COOKIES not found!')
    # if BOT_TOKEN is None:
    #     raise EnvironmentError('Environment BOT_TOKEN not found!')
    # if CHAT_ID is None:
    #     raise EnvironmentError('Environment CHAT_ID not found!')
    GLaDOS_CheckIn(COOKIES, app_id,app_secret,user_id,template_id_s,template_id_e).run()


if __name__ == '__main__':
    checkIn()
