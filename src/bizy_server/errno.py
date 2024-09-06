class ErrorNo:
    def __init__(self, http_status_code, code, payload, message):
        self.http_status_code = http_status_code
        self.code = code
        self.message = message
        self.data = payload


CODE_OK = 20000
CODE_NO_MODEL_FOUND = 20226

INVALID_TYPE = ErrorNo(400, 400100, None, "Invalid type")
INVALID_NAME = ErrorNo(400, 400101, None, "Invalid name")
NO_FILE_UPLOAD_ERR = ErrorNo(400, 400102, None, "No file to upload")
EMPTY_UPLOAD_ID_ERR = ErrorNo(400, 400103, None, "Upload id is Empty")
EMPTY_ABS_FOLDER_ERR = ErrorNo(400, 400111, None, "The upload path cannot be empty.")
NO_ABS_PATH_ERR = ErrorNo(400, 400112, None, "The upload path is not an absolute path.")
PATH_NOT_EXISTS_ERR = ErrorNo(400, 400113, None, "The upload path does not exist.")
FILE_NOT_EXISTS_ERR = ErrorNo(400, 400114, None, "The file does not exist.")
INVALID_CLIENT_ID_ERR = ErrorNo(400, 400114, None, "Invalid client id")
INVALID_API_KEY_ERR = ErrorNo(401, 401000, None, "Invalid API key")

FILE_UPLOAD_SIZE_LIMIT_ERR = ErrorNo(
    413,
    413000,
    None,
    'File size exceeds the allowed limit. Please use the "--max-upload-size" to specify the upload file size limit, default is 100MB.',
)

CHECK_MODEL_EXISTS_ERR = ErrorNo(500, 500100, None, "failed to check model")
SIGN_FILE_ERR = ErrorNo(500, 500101, None, "failed to sign file")
UPLOAD_ERR = ErrorNo(500, 500102, None, "failed to upload file")
COMMIT_FILE_ERR = ErrorNo(500, 500103, None, "failed to commit file")
MODEL_ALREADY_EXISTS_ERR = ErrorNo(500, 500104, None, "model already exists")
COMMIT_MODEL_ERR = ErrorNo(500, 500105, None, "failed to commit model")
INVALID_UPLOAD_ID_ERR = ErrorNo(500, 500106, None, "invalid upload id")
EMPTY_FILES_ERR = ErrorNo(500, 500107, None, "empty files to make a model")
LIST_MODEL_FILE_ERR = ErrorNo(500, 500108, None, "failed to list model file")
INVALID_FILENAME_ERR = ErrorNo(500, 500109, None, "invalid filename")
DELETE_MODEL_ERR = ErrorNo(500, 500110, None, "failed to delete model")

