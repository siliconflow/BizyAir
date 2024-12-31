class ErrorNo:
    def __init__(self, http_status_code, code, payload, message):
        self.http_status_code = http_status_code
        self.code = code
        self.message = message
        self.data = payload

    def copy(self):
        return ErrorNo(self.http_status_code, self.code, self.data, self.message)


class errnos:
    OK = ErrorNo(200, 20000, None, "Success")
    NO_MODEL_FOUND = ErrorNo(404, 20226, None, "No model found")

    INVALID_TYPE = ErrorNo(400, 400100, None, "Invalid model type")
    INVALID_NAME = ErrorNo(400, 400101, None, "Invalid model name")
    NO_FILE_UPLOAD = ErrorNo(400, 400102, None, "No file to upload")
    EMPTY_UPLOAD_ID = ErrorNo(400, 400103, None, "Upload id is empty")
    INVALID_SHARE_ID = ErrorNo(400, 400104, None, "Invalid share id")
    EMPTY_ABS_PATH = ErrorNo(400, 400111, None, "The upload path cannot be empty")
    NO_ABS_PATH = ErrorNo(400, 400112, None, "The upload path is not an absolute path")
    PATH_NOT_EXISTS = ErrorNo(400, 400113, None, "The upload path does not exist")
    INVALID_CLIENT_ID = ErrorNo(400, 400114, None, "Invalid client id")
    NO_PUBLIC_FLAG = ErrorNo(
        400, 400115, None, 'The parameter "public" is not provided'
    )
    FILE_NOT_EXISTS = ErrorNo(400, 400116, None, "The file does not exist")
    NO_SHARE_ID = ErrorNo(400, 400117, None, 'The parameter "share_id" is not provided')
    INVALID_DESCRIPTION = ErrorNo(400, 400118, None, "Invalid description")
    NOT_A_FILE = ErrorNo(400, 400119, None, "The path is not a file")
    NOT_ALLOWED_EXT_NAME = ErrorNo(400, 400120, None, "Not allowed extension name")
    INVALID_UPLOAD_ID = ErrorNo(400, 400121, None, "Invalid upload id")
    INVALID_VERSIONS = ErrorNo(400, 400122, None, "Invalid versions")
    DUPLICATE_VERSION = ErrorNo(400, 400123, None, "Duplicate version")
    INVALID_VERSION_FIELD = ErrorNo(400, 400124, None, "Invalid version field")
    INVALID_QUERY_MODE = ErrorNo(400, 400125, None, "Invalid query mode")
    INVALID_VERSION_NAME = ErrorNo(400, 400126, None, "Invalid model version name")
    INVALID_MODEL_ID = ErrorNo(400, 400127, None, "Invalid model id")
    INVALID_MODEL_VERSION_ID = ErrorNo(400, 400128, None, "Invalid model version id")
    UNSUPPORT_LIKE_TYPE = ErrorNo(400, 400130, None, "Unsupport like type")
    INVALID_SIGN = ErrorNo(400, 400131, None, "Invalid file sign")
    EMPTY_SHA256SUM = ErrorNo(400, 400132, None, "Empty sha256sum")
    INVALID_OBJECT_KEY = ErrorNo(400, 400133, None, "Invalid object key")
    FAILED_TO_FETCH_WORKFLOW_JSON = ErrorNo(
        400, 400134, None, "Failed to fetch workflow json"
    )
    INVALID_API_KEY = ErrorNo(401, 401000, None, "Invalid API key")
    INVALID_USER = ErrorNo(401, 401001, None, "Invalid user")

    SIGN_FILE = ErrorNo(500, 500101, None, "Failed to sign file")
    UPLOAD = ErrorNo(500, 500102, None, "Failed to upload file")
    COMMIT_FILE = ErrorNo(500, 500103, None, "Failed to commit file")
    COMMIT_BIZY_MODEL = ErrorNo(500, 500105, None, "Failed to commit model")
    EMPTY_FILES = ErrorNo(500, 500107, None, "Empty files to make a model")
    LIST_MODEL_FILE = ErrorNo(500, 500108, None, "Failed to list model file")
    LIST_SHARE_MODEL_FILE = ErrorNo(
        500, 500108, None, "Failed to list share model file"
    )
    INVALID_FILENAME = ErrorNo(500, 500109, None, "Invalid filename")
    DELETE_MODEL = ErrorNo(500, 500110, None, "Failed to delete model")
    GET_USER_INFO = ErrorNo(500, 500111, None, "Failed to get user info")
    LIST_MODEL = ErrorNo(500, 500112, None, "Failed to list model")
    CHANGE_PUBLIC = ErrorNo(500, 500113, None, "Failed to change public")
    UPDATE_SHARE_ID = ErrorNo(500, 500114, None, "Failed to update share id")
    GET_DESCRIPTION = ErrorNo(500, 500115, None, "Failed to get description")
    UPDATE_DESCRIPTION = ErrorNo(500, 500116, None, "Failed to update description")
    DELETE_BIZY_MODEL = ErrorNo(500, 500117, None, "Failed to delete model")
    QUERY_COMMUNITY_MODELS = ErrorNo(
        500, 500118, None, "Failed to query community models"
    )
    QUERY_MODELS = ErrorNo(500, 500119, None, "Failed to query models")
    GET_MODEL_DETAIL = ErrorNo(500, 500120, None, "Failed to get model detail")
    GET_MODEL_VERSION_DETAIL = ErrorNo(
        500, 500121, None, "Failed to get model version detail"
    )
    FORK_MODEL_VERSION = ErrorNo(500, 500122, None, "Failed to fork model version")
    UPDATE_MODEL = ErrorNo(500, 500123, None, "Failed to update model")
    GET_UPLOAD_TOKEN = ErrorNo(500, 500124, None, "Failed to get upload token")
    TOGGLE_USER_LIKE = ErrorNo(500, 500125, None, "Failed to toggle user like")
    GET_DOWNLOAD_URL = ErrorNo(500, 500126, None, "Failed to get download url")
    DOWNLOAD_JSON = ErrorNo(500, 500127, None, "Failed to download json")
    LIST_SHARE_MODEL_FILE_ERR = ErrorNo(
        500, 500128, None, "Failed to list share model file"
    )
    QUERY_OFFICIAL_MODELS = ErrorNo(
        500, 500129, None, "Failed to query official models"
    )
