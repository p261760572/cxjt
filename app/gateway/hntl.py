# coding=utf-8
import json

import requests

from app import logger


def tms_quick_debug(data):
    logger.info(json.dumps(data, ensure_ascii=False))
    params = {
        'inst_id': '00000096',
        'mchnt_cd': data.get('mchnt_cd'),
        'term_id': data.get('term_id'),
        'device_no': data.get('device_no'),
        'device_type': data.get('device_type')
    }

    logger.debug(json.dumps(params, ensure_ascii=False))

    r = requests.post('http://188.80.65.14:18001/gateway/tms/quick-debug', json=params)
    r.raise_for_status()
    return r.json()
