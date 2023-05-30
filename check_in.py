import traceback
from typing import Optional

import json
import requests
import telegram


class GLaDOS_CheckIn:
    _HOST = "glados.network"
    _ORIGIN_URL = f"https://{_HOST}"
    _UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
    _BUDGET_DATA_PATH = "budget.json"

    def __init__(self, cookies: str, bot_token: str, chat_id: str):
        self._cookies: str = cookies
        self._bot_token: str = bot_token
        self._chat_id: str = chat_id

    def _send_msg(self, msg: str):
        bot = telegram.Bot(token=self._bot_token)
        bot.send_message(self._chat_id, msg)

    def _report_success(self, msg: str, left_days: int, plan: str, used_gb: float, total_gb: int):
        self._send_msg(
            '--------------------\n'
            'GLaDOS CheckIn\n'
            'Msg: ' + msg + '\n' +
            'Plan: ' + plan + ' Plan\n' +
            'Left days: ' + str(left_days) + '\n' +
            'Usage: ' + '%.3f' % used_gb + 'GB\n' +
            'Total: ' + str(total_gb) + 'GB\n' +
            '--------------------'
        )

    def _report_cookies_expired(self):
        self._send_msg(
            '--------------------\n'
            'GLaDOS CheckIn\n'
            'Msg: Your cookies are expired!\n'
            '--------------------'
        )

    def _report_checkin_error(self, msg: str):
        self._send_msg(
            '--------------------\n'
            'GLaDOS CheckIn\n'
            'Msg: Check in error!\n'
            'Error:\n' + msg + '\n' +
            '--------------------'
        )

    def _api_traffic(self):
        traffic_url = f"{self._ORIGIN_URL}/api/user/traffic"
        referer_url = f"{self._ORIGIN_URL}/console"

        with requests.get(
                traffic_url,
                headers={'cookie': self._cookies,
                         'referer': referer_url,
                         'origin': self._ORIGIN_URL,
                         'user-agent': self._UA,
                         'content-type': 'application/json;charset=UTF-8'}
        ) as r:
            return r.json()

    def _api_check_in(self) -> dict:
        check_in_url = f"{self._ORIGIN_URL}/api/user/checkin"
        referer_url = f"{self._ORIGIN_URL}/console/checkin"

        payload = {'token': 'glados.network'}

        with requests.post(
                check_in_url,
                headers={'cookie': self._cookies,
                         'referer': referer_url,
                         'origin': self._ORIGIN_URL,
                         'user-agent': self._UA,
                         'content-type': 'application/json;charset=UTF-8'},
                data=json.dumps(payload)
        ) as r:
            return r.json()

    def _api_status(self) -> dict:
        status_url = f"{self._ORIGIN_URL}/api/user/status"
        referer_url = f"{self._ORIGIN_URL}/console/checkin"

        with requests.get(
                status_url,
                headers={'cookie': self._cookies,
                         'referer': referer_url,
                         'origin': self._ORIGIN_URL,
                         'user-agent': self._UA}
        ) as r:
            return r.json()

    def _get_budget(self, vip_level: Optional[int]) -> dict:
        with open(self._BUDGET_DATA_PATH, 'r') as f:
            budget_info = json.load(f)
            user_budgets = [i for i in budget_info if
                            (vip_level is not None and 'vip' in i and i['vip'] == vip_level) or (vip_level is None and 'vip' not in i)]
            if len(user_budgets) > 0:
                return user_budgets[0]
            else:
                raise EnvironmentError(
                    f'Budget info not found for this user! VIP: {vip_level}')

    def _check_in(self):
        check_in_response = self._api_check_in()
        check_in_msg = check_in_response['message']

        if check_in_msg == '\u6ca1\u6709\u6743\u9650':
            self._report_cookies_expired()
            return

        status_response = self._api_status()
        left_days = int(status_response['data']['leftDays'].split('.')[0])
        vip_level = status_response['data']['vip']

        traffic_response = self._api_traffic()
        used_gb = traffic_response["data"]["today"] / 1024 / 1024 / 1024

        user_budget = self._get_budget(vip_level)
        total_gb = user_budget['budget']
        plan = user_budget['level']

        self._report_success(check_in_msg, left_days, plan, used_gb, total_gb)

    def run(self):
        try:
            self._check_in()
        except BaseException:
            self._report_checkin_error(traceback.format_exc())
