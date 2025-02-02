import traceback

from data import get


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
