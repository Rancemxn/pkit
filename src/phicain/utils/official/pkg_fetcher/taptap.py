import json
import random
import urllib3
import typing

from uuid import uuid4, UUID
from time import time
from hashlib import md5
from string import ascii_lowercase, digits
from typing import Dict, Any

import requests

from loguru import logger

urllib3.disable_warnings()


def get_download_info(
    appid: int = 165287, apkid: typing.Optional[int] = None
) -> Dict[str, Any]:
    UID: UUID = uuid4()
    API: str = "https://api.taptapdada.com"
    USER_AGENT: str = "okhttp/3.12.1"
    VN_CODE: str = "281001004"
    X_UA: str = (
        f"V=1&PN=TapTap&VN_CODE={VN_CODE}&LOC=CN&LANG=zh_CN&CH=default&UID={UID}"
    )

    try:
        apkid_result: Dict[str, Any] = requests.get(
            f"{API}/app/v2/detail-by-id/{appid}",
            params={"X-UA": X_UA},
            headers={"User-Agent": USER_AGENT},
            verify=False,
        ).json()
    except json.decoder.JSONDecodeError:
        raise Exception("Request TapTap API too frequently")
    except requests.exceptions.RequestException:
        raise

    apkid_int: int = (
        apkid_result["data"]["download"]["apk_id"] if apkid is None else apkid
    )

    nonce: str = "".join(random.sample(ascii_lowercase + digits, 5))
    t: int = int(time())
    sign: str = md5(
        f"X-UA={X_UA}&end_point=d1&id={apkid_int}&node={UID}&nonce={nonce}&time={t}PeCkE6Fu0B10Vm9BKfPfANwCUAn5POcs".encode()
    ).hexdigest()

    post_data: Dict[str, Any] = {
        "sign": sign,
        "node": UID,
        "time": t,
        "id": apkid_int,
        "nonce": nonce,
        "end_point": "d1",
    }

    post_headers: Dict[str, str] = {
        "User-Agent": USER_AGENT,
    }

    try:
        response: requests.Response = requests.post(
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
