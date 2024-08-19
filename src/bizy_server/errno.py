class ErrorNo:
    def __init__(self, http_status_code, code, payload, message):
        self.http_status_code = http_status_code
        self.code = code
        self.message = message
        self.data = payload

CODE_OK = 20000
INVAILD_TYPE = ErrorNo(400, 400100, None, "type is invalid")
INVAILD_NAME = ErrorNo(400, 400101, None, "name is invalid")
CHECK_MODEL_EXISTS_ERR = ErrorNo(500, 500100, None, "failed to check model")
