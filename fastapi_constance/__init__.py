from .wrapper import constance_config
from .lifespan import lifespan
from .config import register_config
from .admin import setup_constance_admin

__all__ = ["constance_config", "lifespan", "register_config", "setup_constance_admin"]
__version__ = "0.1.0"
