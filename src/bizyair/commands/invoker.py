from .processors.prompt_processor import (
    PromptAsyncProcessor,
    PromptPreRunProcessor,
    PromptProcessor,
    SearchServiceRouter,
)
from .servers.prompt_server import PromptAsyncServer, PromptServer

prompt_server = PromptServer(router=SearchServiceRouter(), processor=PromptProcessor())
prompt_async_server = PromptAsyncServer(
    router=SearchServiceRouter(),
    pre_run_processor=PromptPreRunProcessor(),
    request_processor=PromptAsyncProcessor(),
)
