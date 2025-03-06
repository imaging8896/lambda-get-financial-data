import traceback
import logging
import sys

from data import get


logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler(sys.stdout)])


def handler(event=None, context=None):
    try:
        data = get(**event)
        return {
            "status": True,
            "result": {
                "data": data,
            },
        }
    except Exception as e:
        return {
            "status": False,
            "result": {
                "exception_type": str(type(e)),
                "exception_message": str(e),
                "traceback" : traceback.format_exc(),
            },
        }        
