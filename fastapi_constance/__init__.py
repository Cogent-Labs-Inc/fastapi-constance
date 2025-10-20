from .wrapper import ConstanceConfigWrapper
from .lifespan import lifespan
from .config import register_config

constance_config = ConstanceConfigWrapper()

__all__ = ["constance_config", "lifespan", "register_config"]
__version__ = "0.1.0"
