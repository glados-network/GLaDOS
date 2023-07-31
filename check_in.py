import traceback
from typing import Optional
from datetime import date, datetime
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage, WeChatTemplate

import json
import requests
import random
# import telegram

class GLaDOS_CheckIn:
    _HOST = "glados.rocks"
    _ORIGIN_URL = f"https://{_HOST}"
    _UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
    _BUDGET_DATA_PATH = "budget.json"

    def __init__(self, cookies: str,  app_id,app_secret,user_id,template_id_s,template_id_e):
        self._cookies: str = cookies
        self._app_id = app_id
        self._app_secret = app_secret
        self._user_id = user_id
        self._template_id_s = template_id_s
        self._template_id_e = template_id_e

    # def _send_msg(self, msg: str):
    #     bot = telegram.Bot(token=self._bot_token)
    #     bot.send_message(self._chat_id, msg)

    # 字体随机颜色
    def _get_random_color(self):
        return "#%06x" % random.randint(0, 0xFFFFFF)
    def _send_to_mp(self,msg:str):
        tday = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        client = WeChatClient(self._app_id, self._app_secret)
        wm = WeChatMessage(client)
        data = {
            "date": {"value": format(tday), "color": self._get_random_color()},
            "re": {"value": msg, "color": self._get_random_color()},
        }
        res = wm.send_template(self._user_id, self._template_id_e, data)


    def _report_success(self, msg: str, left_days: int, plan: str, used_gb: float, total_gb: int):
        tday = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = {
            "date": {"value": tday, "color": self._get_random_color()},
            "msg": {"value": msg, "color": self._get_random_color()},
            "plan": {"value": plan, "color": self._get_random_color()},
            "ldays": {"value": left_days, "color": self._get_random_color()},
            "usege": {"value": '%.3f' % used_gb, "color": self._get_random_color()},
            "total": {"value": total_gb, "color": self._get_random_color()},
        }

        client = WeChatClient(self._app_id, self._app_secret)
        wm = WeChatMessage(client)
        res = wm.send_template(self._user_id, self._template_id_s, data)

    def _report_cookies_expired(self):
        self._send_to_mp("Your cookies are expired!")

    def _report_token_error(self):
        self._send_to_mp("oops, token error")

    def _report_checkin_error(self, msg: str):
        self._send_to_mp(msg)

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
        referer_url = f"{self._ORIGIN_URL}/console"

        payload = {'token': 'glados.one'}

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

        # 没有权限
        if check_in_msg == '\u6ca1\u6709\u6743\u9650':
            self._report_cookies_expired()
            return

        if "token error" in check_in_msg:
            self._report_token_error()
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
