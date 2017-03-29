import sys
import traceback

BAD_REQUEST_CODE = 400
UNAUTHORIZED_CODE = 403
NOT_FOUND_CODE = 404
SERVER_ERROR = 500


class InvalidAPIRequest(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code:
            self.status_code = status_code
        self.payload = payload if isinstance(payload, dict) or isinstance(payload, str) else {}

    def to_dict(self):
        if isinstance(self.payload, str):
            self.payload = dict(payload=self.payload, message=self.message)
        elif isinstance(self.payload, dict):
            self.payload['message'] = self.message
        return self.payload


def get_traceback():
    return traceback.format_exc(10)


