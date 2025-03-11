class ErrorHandler:
    def handle_error(self, error_code, message=None, data=None):
        return {"code": error_code, "message": message or "", "data": data or {}}
