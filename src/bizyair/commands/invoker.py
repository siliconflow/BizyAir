from .processors.prompt_processor import PromptProcessor, SearchServiceRouter
from .servers.prompt_server import PromptServer

prompt_server = PromptServer(router=SearchServiceRouter(), processor=PromptProcessor())
