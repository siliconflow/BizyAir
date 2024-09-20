from .processors.prompt_processor import (
    PromptProcessor,
    PromptSseProcessor,
    SearchServiceRouter,
)
from .servers.prompt_server import PromptServer, PromptSseServer

prompt_server = PromptServer(router=SearchServiceRouter(), processor=PromptProcessor())

prompt_sse_server = PromptSseServer(
    router=SearchServiceRouter(), processor=PromptSseProcessor()
)
