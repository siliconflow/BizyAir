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
    INVALID_DATASET_NAME = ErrorNo(400, 400135, None, "Invalid dataset name")
    INVALID_DATASET_VERSION = ErrorNo(400, 400136, None, "Invalid dataset version")
    INVALID_DATASET_ID = ErrorNo(400, 400137, None, "Invalid dataset id")
    INVALID_DATASET_VERSION_ID = ErrorNo(
        400, 400138, None, "Invalid dataset version id"
    )
    INVALID_SHARE_BIZ_ID = ErrorNo(400, 400139, None, "Invalid share biz id")
    INVALID_SHARE_TYPE = ErrorNo(400, 400140, None, "Invalid share type")
    INVALID_SHARE_CODE = ErrorNo(400, 400141, None, "Invalid share code")
    INVALID_NOTIF_ID = ErrorNo(400, 400142, None, "Invalid notification id")

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
    UNFORK_MODEL_VERSION = ErrorNo(500, 500130, None, "Failed to unfork model version")

    COMMIT_DATASET = ErrorNo(500, 500130, None, "Failed to commit dataset")
    UPDATE_DATASET = ErrorNo(500, 500131, None, "Failed to update dataset")
    GET_DATASET_VERSION_DETAIL = ErrorNo(
        500, 500132, None, "Failed to get dataset version detail"
    )
    DELETE_DATASET = ErrorNo(500, 500133, None, "Failed to delete dataset")
    QUERY_DATASETS = ErrorNo(500, 500134, None, "Failed to query datasets")
    GET_DATASET_DETAIL = ErrorNo(500, 500135, None, "Failed to get dataset detail")
    CREATE_SHARE = ErrorNo(500, 500136, None, "Failed to create share")
    GET_SHARE_DETAIL = ErrorNo(500, 500137, None, "Failed to get share detail")

    GET_DATA_DICT = ErrorNo(500, 500138, None, "Failed to get data dict")

    GET_NOTIF_UNREAD_COUNT = ErrorNo(
        500, 500139, None, "Failed to get notification unread counts"
    )
    QUERY_NOTIF = ErrorNo(500, 500140, None, "Failed to query notifications")
    READ_NOTIF = ErrorNo(500, 500141, None, "Failed to mark notifications as read")
    READ_ALL_NOTIF = ErrorNo(
        500, 500142, None, "Failed to mark all notifications as read"
    )
    GET_WALLET_INFO = ErrorNo(500, 500143, None, "Failed to get user wallet info")
    QUERY_COINS = ErrorNo(500, 500144, None, "Failed to query user coin records")
    GET_USER_METADATA = ErrorNo(500, 500145, None, "Failed to get user metadata")
    UPDATE_USER_INFO = ErrorNo(500, 500146, None, "Failed to update user info") 
    USER_REAL_NAME = ErrorNo(500, 500147, None, "Failed to verify real name")