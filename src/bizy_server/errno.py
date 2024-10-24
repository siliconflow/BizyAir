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
INVALID_SHARE_ID = ErrorNo(400, 400104, None, "Invalid share id")
EMPTY_ABS_FOLDER_ERR = ErrorNo(400, 400111, None, "The upload path cannot be empty.")
NO_ABS_PATH_ERR = ErrorNo(400, 400112, None, "The upload path is not an absolute path.")
PATH_NOT_EXISTS_ERR = ErrorNo(400, 400113, None, "The upload path does not exist.")
INVALID_CLIENT_ID_ERR = ErrorNo(400, 400114, None, "Invalid client id")
NO_PUBLIC_FLAG_ERR = ErrorNo(
    400, 400115, None, 'The parameter "public" is not provided.'
)
FILE_NOT_EXISTS_ERR = ErrorNo(400, 400116, None, "The file does not exist.")
NO_SHARE_ID_ERR = ErrorNo(
    400, 400117, None, 'The parameter "share_id" is not provided.'
)
INVALID_DESCRIPTION = ErrorNo(400, 400118, None, "Invalid description")
INVALID_API_KEY_ERR = ErrorNo(401, 401000, None, "Invalid API key")
INVALID_USER_ERR = ErrorNo(401, 401001, None, "Invalid user")

CHECK_MODEL_EXISTS_ERR = ErrorNo(500, 500100, None, "Failed to check model")
SIGN_FILE_ERR = ErrorNo(500, 500101, None, "Failed to sign file")
UPLOAD_ERR = ErrorNo(500, 500102, None, "Failed to upload file")
COMMIT_FILE_ERR = ErrorNo(500, 500103, None, "Failed to commit file")
MODEL_ALREADY_EXISTS_ERR = ErrorNo(500, 500104, None, "Model already exists")
COMMIT_MODEL_ERR = ErrorNo(500, 500105, None, "Failed to commit model")
INVALID_UPLOAD_ID_ERR = ErrorNo(500, 500106, None, "Invalid upload id")
EMPTY_FILES_ERR = ErrorNo(500, 500107, None, "Empty files to make a model")
LIST_MODEL_FILE_ERR = ErrorNo(500, 500108, None, "Failed to list model file")
LIST_SHARE_MODEL_FILE_ERR = ErrorNo(
    500, 500108, None, "Failed to list share model file"
)
INVALID_FILENAME_ERR = ErrorNo(500, 500109, None, "Invalid filename")
DELETE_MODEL_ERR = ErrorNo(500, 500110, None, "Failed to delete model")
GET_USER_INFO_ERR = ErrorNo(500, 500111, None, "Failed to get user info")
LIST_MODEL_ERR = ErrorNo(500, 500112, None, "Failed to list model")
CHANGE_PUBLIC_ERR = ErrorNo(500, 500113, None, "Failed to change public")
UPDATE_SHATE_ID_ERR = ErrorNo(500, 500114, None, "Failed to update share id")
GET_DESCRIPTION_ERR = ErrorNo(500, 500115, None, "Failed to get description")
UPDATE_DESCRIPTION_ERR = ErrorNo(500, 500116, None, "Failed to update description")
