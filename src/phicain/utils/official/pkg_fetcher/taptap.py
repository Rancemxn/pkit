# Reference: https://github.com/qaqFei/phispler/blob/main/src/tool-getPgrUrl.py


import json
import random

import urllib3
import typing
from uuid import uuid4
from time import time
from hashlib import md5
from string import ascii_lowercase, digits
from loguru import logger

import requests

urllib3.disable_warnings()


def get_download_info(appid: int = 165287, apkid: typing.Optional[int] = None):
    UID = uuid4()
    API = "https://api.taptapdada.com"
    USER_AGENT = "okhttp/3.12.1"
    VN_CODE = "281001004"
    X_UA = f"V=1&PN=TapTap&VN_CODE={VN_CODE}&LOC=CN&LANG=zh_CN&CH=default&UID={UID}"

    try:
        apkid_result = requests.get(
            f"{API}/app/v2/detail-by-id/{appid}",
            params={"X-UA": X_UA},
            headers={"User-Agent": USER_AGENT},
            verify=False,
        ).json()
    except json.decoder.JSONDecodeError:
        raise Exception("Request TapTap API too frequently")
    except requests.exceptions.RequestException:
        raise

    apkid = apkid_result["data"]["download"]["apk_id"] if apkid is None else apkid

    nonce = "".join(random.sample(ascii_lowercase + digits, 5))
    t = int(time())
    sign = md5(
        f"X-UA={X_UA}&end_point=d1&id={apkid}&node={UID}&nonce={nonce}&time={t}PeCkE6Fu0B10Vm9BKfPfANwCUAn5POcs".encode()
    ).hexdigest()

    post_data = {
        "sign": sign,
        "node": UID,
        "time": t,
        "id": apkid,
        "nonce": nonce,
        "end_point": "d1",
    }

    post_headers = {
        "User-Agent": USER_AGENT,
    }

    try:
        response = requests.post(
            f"{API}/apk/v1/detail",
            params={"X-UA": X_UA},
            data=post_data,
            headers=post_headers,
            verify=False,
        )
        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException:
        logger.error("Request TapTap API apk detail Error")
        raise
    except json.decoder.JSONDecodeError:
        raise
