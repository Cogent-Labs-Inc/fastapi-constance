try:
    import sqladmin
except ImportError:
    raise ImportError(
        "sqladmin[full] is required for SQLAdmin integration. "
        "Install it via `pip install fastapi-constance[admin]`"
    )

from sqladmin import Admin, ModelView
from .models import ConstanceConfig

def setup_admin(app, engine):
    if app is None or engine is None:
        raise RuntimeError("FastAPI app and engine must be provided for SQLAdmin")
    admin = Admin(app, engine)
    admin.add_view(ModelView(ConstanceConfig, engine))
    return admin
