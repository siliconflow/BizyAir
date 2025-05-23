class ErrorNo:
    def __init__(self, http_status_code, code, payload, messages):
        self.http_status_code = http_status_code
        self.code = code
        self.messages = messages  # 现在是一个字典，key是语言代码
        self.data = payload

    def copy(self):
        return ErrorNo(self.http_status_code, self.code, self.data, self.messages)

    def get_message(self, lang="en"):
        return self.messages.get(lang, self.messages.get("en", "Unknown error"))


class errnos:
    OK = ErrorNo(200, 20000, None, {"en": "Success", "zh": "成功"})
    NO_MODEL_FOUND = ErrorNo(
        404, 20226, None, {"en": "No model found", "zh": "未找到模型"}
    )
    INTERNAL_ERROR = ErrorNo(
        500, 50000, None, {"en": "Internal Error", "zh": "内部错误"}
    )

    INVALID_TYPE = ErrorNo(
        400, 400100, None, {"en": "Invalid model type", "zh": "无效的模型类型"}
    )
    INVALID_NAME = ErrorNo(
        400, 400101, None, {"en": "Invalid model name", "zh": "无效的模型名称"}
    )
    NO_FILE_UPLOAD = ErrorNo(
        400, 400102, None, {"en": "No file to upload", "zh": "没有要上传的文件"}
    )
    EMPTY_UPLOAD_ID = ErrorNo(
        400, 400103, None, {"en": "Upload id is empty", "zh": "上传ID为空"}
    )
    INVALID_SHARE_ID = ErrorNo(
        400, 400104, None, {"en": "Invalid share id", "zh": "无效的分享ID"}
    )
    EMPTY_ABS_PATH = ErrorNo(
        400,
        400111,
        None,
        {"en": "The upload path cannot be empty", "zh": "上传路径不能为空"},
    )
    NO_ABS_PATH = ErrorNo(
        400,
        400112,
        None,
        {"en": "The upload path is not an absolute path", "zh": "上传路径不是绝对路径"},
    )
    PATH_NOT_EXISTS = ErrorNo(
        400,
        400113,
        None,
        {"en": "The upload path does not exist", "zh": "上传路径不存在"},
    )
    INVALID_CLIENT_ID = ErrorNo(
        400, 400114, None, {"en": "Invalid client id", "zh": "无效的客户端ID"}
    )
    NO_PUBLIC_FLAG = ErrorNo(
        400,
        400115,
        None,
        {"en": 'The parameter "public" is not provided', "zh": "未提供public参数"},
    )
    FILE_NOT_EXISTS = ErrorNo(
        400, 400116, None, {"en": "The file does not exist", "zh": "文件不存在"}
    )
    NO_SHARE_ID = ErrorNo(
        400,
        400117,
        None,
        {"en": 'The parameter "share_id" is not provided', "zh": "未提供share_id参数"},
    )
    INVALID_DESCRIPTION = ErrorNo(
        400, 400118, None, {"en": "Invalid description", "zh": "无效的描述"}
    )
    NOT_A_FILE = ErrorNo(
        400, 400119, None, {"en": "The path is not a file", "zh": "路径不是文件"}
    )
    NOT_ALLOWED_EXT_NAME = ErrorNo(
        400,
        400120,
        None,
        {"en": "Not allowed extension name", "zh": "不允许的文件扩展名"},
    )
    INVALID_UPLOAD_ID = ErrorNo(
        400, 400121, None, {"en": "Invalid upload id", "zh": "无效的上传ID"}
    )
    INVALID_VERSIONS = ErrorNo(
        400, 400122, None, {"en": "Invalid versions", "zh": "无效的版本信息"}
    )
    DUPLICATE_VERSION = ErrorNo(
        400, 400123, None, {"en": "Duplicate version", "zh": "重复的版本"}
    )
    INVALID_VERSION_FIELD = ErrorNo(
        400, 400124, None, {"en": "Invalid version field", "zh": "无效的版本字段"}
    )
    INVALID_QUERY_MODE = ErrorNo(
        400, 400125, None, {"en": "Invalid query mode", "zh": "无效的查询模式"}
    )
    INVALID_VERSION_NAME = ErrorNo(
        400,
        400126,
        None,
        {"en": "Invalid model version name", "zh": "无效的模型版本名称"},
    )
    INVALID_MODEL_ID = ErrorNo(
        400, 400127, None, {"en": "Invalid model id", "zh": "无效的模型ID"}
    )
    INVALID_MODEL_VERSION_ID = ErrorNo(
        400, 400128, None, {"en": "Invalid model version id", "zh": "无效的模型版本ID"}
    )
    UNSUPPORT_LIKE_TYPE = ErrorNo(
        400, 400130, None, {"en": "Unsupport like type", "zh": "不支持的点赞类型"}
    )
    INVALID_SIGN = ErrorNo(
        400, 400131, None, {"en": "Invalid file sign", "zh": "无效的文件签名"}
    )
    EMPTY_SHA256SUM = ErrorNo(
        400, 400132, None, {"en": "Empty sha256sum", "zh": "空的sha256sum"}
    )
    INVALID_OBJECT_KEY = ErrorNo(
        400, 400133, None, {"en": "Invalid object key", "zh": "无效的对象键"}
    )
    FAILED_TO_FETCH_WORKFLOW_JSON = ErrorNo(
        400,
        400134,
        None,
        {"en": "Failed to fetch workflow json", "zh": "获取工作流JSON失败"},
    )
    INVALID_DATASET_NAME = ErrorNo(
        400, 400135, None, {"en": "Invalid dataset name", "zh": "无效的数据集名称"}
    )
    INVALID_DATASET_VERSION = ErrorNo(
        400, 400136, None, {"en": "Invalid dataset version", "zh": "无效的数据集版本"}
    )
    INVALID_DATASET_ID = ErrorNo(
        400, 400137, None, {"en": "Invalid dataset id", "zh": "无效的数据集ID"}
    )
    INVALID_DATASET_VERSION_ID = ErrorNo(
        400,
        400138,
        None,
        {"en": "Invalid dataset version id", "zh": "无效的数据集版本ID"},
    )
    INVALID_SHARE_BIZ_ID = ErrorNo(
        400, 400139, None, {"en": "Invalid share biz id", "zh": "无效的分享业务ID"}
    )
    INVALID_SHARE_TYPE = ErrorNo(
        400, 400140, None, {"en": "Invalid share type", "zh": "无效的分享类型"}
    )
    INVALID_SHARE_CODE = ErrorNo(
        400, 400141, None, {"en": "Invalid share code", "zh": "无效的分享代码"}
    )
    INVALID_NOTIF_ID = ErrorNo(
        400, 400142, None, {"en": "Invalid notification id", "zh": "无效的通知ID"}
    )
    INVALID_PRODUCT_ID = ErrorNo(
        400, 400143, None, {"en": "Invalid product id", "zh": "无效的产品ID"}
    )
    INVALID_ORDER_NO = ErrorNo(
        400, 400144, None, {"en": "Invalid order number", "zh": "无效的订单号"}
    )

    INVALID_PAY_PLATFORM = ErrorNo(
        400, 400145, None, {"en": "Invalid pay platform", "zh": "无效的支付平台"}
    )

    INVALID_YEAR_PARAM = ErrorNo(
        400, 400146, None, {"en": "Year parameter is required", "zh": "缺少年份参数"}
    )

    INVALID_MONTH_PARAM = ErrorNo(
        400, 400147, None, {"en": "Month parameter is required", "zh": "缺少月份参数"}
    )

    INVALID_DAY_PARAM = ErrorNo(
        400, 400148, None, {"en": "Day parameter is required", "zh": "缺少日期参数"}
    )

    MISSING_PROMPT = ErrorNo(
        400, 400149, None, {"en": "Missing parameter prompt", "zh": "缺少参数prompt"}
    )

    # 具体错误动态填
    INVALID_PROMPT = ErrorNo(
        400, 400150, None, {"en": "Invalid prompt", "zh": "工作流错误"}
    )

    INVALID_API_KEY = ErrorNo(
        401, 401000, None, {"en": "Invalid API key", "zh": "无效的API密钥"}
    )
    INVALID_USER = ErrorNo(
        401, 401001, None, {"en": "Invalid user", "zh": "无效的用户"}
    )

    SIGN_FILE = ErrorNo(
        500, 500101, None, {"en": "Failed to sign file", "zh": "文件签名失败"}
    )
    UPLOAD = ErrorNo(
        500, 500102, None, {"en": "Failed to upload file", "zh": "文件上传失败"}
    )
    COMMIT_FILE = ErrorNo(
        500, 500103, None, {"en": "Failed to commit file", "zh": "文件提交失败"}
    )
    COMMIT_BIZY_MODEL = ErrorNo(
        500, 500105, None, {"en": "Failed to commit model", "zh": "模型提交失败"}
    )
    EMPTY_FILES = ErrorNo(
        500,
        500107,
        None,
        {"en": "Empty files to make a model", "zh": "创建模型的文件为空"},
    )
    LIST_MODEL_FILE = ErrorNo(
        500, 500108, None, {"en": "Failed to list model file", "zh": "列出模型文件失败"}
    )
    LIST_SHARE_MODEL_FILE = ErrorNo(
        500,
        500108,
        None,
        {"en": "Failed to list share model file", "zh": "列出分享模型文件失败"},
    )
    INVALID_FILENAME = ErrorNo(
        500, 500109, None, {"en": "Invalid filename", "zh": "无效的文件名"}
    )
    DELETE_MODEL = ErrorNo(
        500, 500110, None, {"en": "Failed to delete model", "zh": "删除模型失败"}
    )
    GET_USER_INFO = ErrorNo(
        500, 500111, None, {"en": "Failed to get user info", "zh": "获取用户信息失败"}
    )
    LIST_MODEL = ErrorNo(
        500, 500112, None, {"en": "Failed to list model", "zh": "列出模型失败"}
    )
    CHANGE_PUBLIC = ErrorNo(
        500, 500113, None, {"en": "Failed to change public", "zh": "更改公开状态失败"}
    )
    UPDATE_SHARE_ID = ErrorNo(
        500, 500114, None, {"en": "Failed to update share id", "zh": "更新分享ID失败"}
    )
    GET_DESCRIPTION = ErrorNo(
        500, 500115, None, {"en": "Failed to get description", "zh": "获取描述失败"}
    )
    UPDATE_DESCRIPTION = ErrorNo(
        500, 500116, None, {"en": "Failed to update description", "zh": "更新描述失败"}
    )
    DELETE_BIZY_MODEL = ErrorNo(
        500, 500117, None, {"en": "Failed to delete model", "zh": "删除模型失败"}
    )
    QUERY_COMMUNITY_MODELS = ErrorNo(
        500,
        500118,
        None,
        {"en": "Failed to query community models", "zh": "查询社区模型失败"},
    )
    QUERY_MODELS = ErrorNo(
        500, 500119, None, {"en": "Failed to query models", "zh": "查询模型失败"}
    )
    GET_MODEL_DETAIL = ErrorNo(
        500,
        500120,
        None,
        {"en": "Failed to get model detail", "zh": "获取模型详情失败"},
    )
    GET_MODEL_VERSION_DETAIL = ErrorNo(
        500,
        500121,
        None,
        {"en": "Failed to get model version detail", "zh": "获取模型版本详情失败"},
    )
    FORK_MODEL_VERSION = ErrorNo(
        500,
        500122,
        None,
        {"en": "Failed to fork model version", "zh": "分支模型版本失败"},
    )
    UPDATE_MODEL = ErrorNo(
        500, 500123, None, {"en": "Failed to update model", "zh": "更新模型失败"}
    )
    GET_UPLOAD_TOKEN = ErrorNo(
        500,
        500124,
        None,
        {"en": "Failed to get upload token", "zh": "获取上传令牌失败"},
    )
    TOGGLE_USER_LIKE = ErrorNo(
        500,
        500125,
        None,
        {"en": "Failed to toggle user like", "zh": "切换用户点赞状态失败"},
    )
    GET_DOWNLOAD_URL = ErrorNo(
        500, 500126, None, {"en": "Failed to get download url", "zh": "获取下载URL失败"}
    )
    DOWNLOAD_JSON = ErrorNo(
        500, 500127, None, {"en": "Failed to download json", "zh": "下载JSON失败"}
    )
    LIST_SHARE_MODEL_FILE_ERR = ErrorNo(
        500,
        500128,
        None,
        {"en": "Failed to list share model file", "zh": "列出分享模型文件失败"},
    )
    QUERY_OFFICIAL_MODELS = ErrorNo(
        500,
        500129,
        None,
        {"en": "Failed to query official models", "zh": "查询官方模型失败"},
    )
    UNFORK_MODEL_VERSION = ErrorNo(
        500,
        500130,
        None,
        {"en": "Failed to unfork model version", "zh": "取消分支模型版本失败"},
    )

    COMMIT_DATASET = ErrorNo(
        500, 500130, None, {"en": "Failed to commit dataset", "zh": "提交数据集失败"}
    )
    UPDATE_DATASET = ErrorNo(
        500, 500131, None, {"en": "Failed to update dataset", "zh": "更新数据集失败"}
    )
    GET_DATASET_VERSION_DETAIL = ErrorNo(
        500,
        500132,
        None,
        {"en": "Failed to get dataset version detail", "zh": "获取数据集版本详情失败"},
    )
    DELETE_DATASET = ErrorNo(
        500, 500133, None, {"en": "Failed to delete dataset", "zh": "删除数据集失败"}
    )
    QUERY_DATASETS = ErrorNo(
        500, 500134, None, {"en": "Failed to query datasets", "zh": "查询数据集失败"}
    )
    GET_DATASET_DETAIL = ErrorNo(
        500,
        500135,
        None,
        {"en": "Failed to get dataset detail", "zh": "获取数据集详情失败"},
    )
    CREATE_SHARE = ErrorNo(
        500, 500136, None, {"en": "Failed to create share", "zh": "创建分享失败"}
    )
    GET_SHARE_DETAIL = ErrorNo(
        500,
        500137,
        None,
        {"en": "Failed to get share detail", "zh": "获取分享详情失败"},
    )

    GET_DATA_DICT = ErrorNo(
        500, 500138, None, {"en": "Failed to get data dict", "zh": "获取数据字典失败"}
    )

    GET_NOTIF_UNREAD_COUNT = ErrorNo(
        500,
        500139,
        None,
        {
            "en": "Failed to get notification unread counts",
            "zh": "获取未读通知数量失败",
        },
    )
    QUERY_NOTIF = ErrorNo(
        500, 500140, None, {"en": "Failed to query notifications", "zh": "查询通知失败"}
    )
    READ_NOTIF = ErrorNo(
        500,
        500141,
        None,
        {"en": "Failed to mark notifications as read", "zh": "标记通知为已读失败"},
    )
    READ_ALL_NOTIF = ErrorNo(
        500,
        500142,
        None,
        {
            "en": "Failed to mark all notifications as read",
            "zh": "标记所有通知为已读失败",
        },
    )
    GET_WALLET_INFO = ErrorNo(
        500,
        500143,
        None,
        {"en": "Failed to get user wallet info", "zh": "获取用户钱包信息失败"},
    )
    QUERY_COINS = ErrorNo(
        500,
        500144,
        None,
        {"en": "Failed to query user coin records", "zh": "查询用户金币记录失败"},
    )
    GET_USER_METADATA = ErrorNo(
        500,
        500145,
        None,
        {"en": "Failed to get user metadata", "zh": "获取用户元数据失败"},
    )
    UPDATE_USER_INFO = ErrorNo(
        500,
        500146,
        None,
        {"en": "Failed to update user info", "zh": "更新用户信息失败"},
    )
    USER_REAL_NAME = ErrorNo(
        500, 500147, None, {"en": "Failed to verify real name", "zh": "实名认证失败"}
    )
    COPY_PROFILE_FAILED = ErrorNo(
        500, 500148, None, {"en": "Failed to copy profile", "zh": "复制配置文件失败"}
    )
    CREATE_PROFILE_FAILED = ErrorNo(
        500, 500149, None, {"en": "Failed to create profile", "zh": "创建配置文件失败"}
    )
    WRITE_PROFILE_FAILED = ErrorNo(
        500, 500150, None, {"en": "Failed to write profile", "zh": "写入配置文件失败"}
    )
    READ_PROFILE_FAILED = ErrorNo(
        500, 500151, None, {"en": "Failed to read profile", "zh": "读取配置文件失败"}
    )
    BUY_PRODUCT = ErrorNo(
        500, 500148, None, {"en": "Failed to buy product", "zh": "购买商品失败"}
    )
    PAY_STATUS = ErrorNo(
        500,
        500149,
        None,
        {"en": "Failed to check payment status", "zh": "检查支付状态失败"},
    )
    PAY_CANCEL = ErrorNo(
        500, 500150, None, {"en": "Failed to cancel payment", "zh": "取消支付失败"}
    )
    LIST_PRODUCTS = ErrorNo(
        500, 500151, None, {"en": "Failed to list products", "zh": "列出商品失败"}
    )
    LIST_PAY_ORDER = ErrorNo(
        500, 500152, None, {"en": "Failed to list pay orders", "zh": "列出支付订单失败"}
    )
    GET_YEAR_COST = ErrorNo(
        500, 500153, None, {"en": "Failed to get year cost", "zh": "获取年度费用失败"}
    )
    GET_MONTH_COST = ErrorNo(
        500, 500154, None, {"en": "Failed to get month cost", "zh": "获取月度费用失败"}
    )
    GET_DAY_COST = ErrorNo(
        500, 500155, None, {"en": "Failed to get day cost", "zh": "获取日费用失败"}
    )

    GET_RECENT_COST = ErrorNo(
        500, 500157, None, {"en": "Failed to get recent cost", "zh": "获取最近消费失败"}
    )

    MODEL_API_ERROR = ErrorNo(
        500, 500158, None, {"en": "Failed to call model API", "zh": "调用模型API失败"}
    )

    MODEL_API_TIMEOUT = ErrorNo(
        500, 500159, None, {"en": "Model API request timeout", "zh": "模型API请求超时"}
    )

    STREAMING_CONNECTION_ERROR = ErrorNo(
        500,
        500160,
        None,
        {"en": "Streaming connection closed unexpectedly", "zh": "流式连接异常关闭"},
    )
