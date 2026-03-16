# |---------------------------------------------------------|
# |                                                         |
# |                 Give Feedback / Get Help                |
# | https://github.com/getbindu/Bindu/issues/new/choose    |
# |                                                         |
# |---------------------------------------------------------|
#
#  Thank you users! We ❤️ you! - 🌻

"""ai-teaching-agent - An Bindu Agent."""

from ai_teaching_agent.__version__ import __version__
from ai_teaching_agent.main import (
    handler,
    initialize_agent,
    main,
)

__all__ = [
    "__version__",
    "handler",
    "initialize_agent",
    "initialize_all",
    "initialize_mcp_tools",
    "main",
]
