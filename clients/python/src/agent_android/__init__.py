__version__ = "0.1.1"

from .client import AgentAndroidClient
from .repl import AriaReplSession

__all__ = ["__version__", "main", "AgentAndroidClient", "AriaReplSession"]


def main() -> int:
    from .cli import main as cli_main

    return cli_main()
