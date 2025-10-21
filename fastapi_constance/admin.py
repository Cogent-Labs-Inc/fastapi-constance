from sqladmin import Admin, ModelView
from .models import ConstanceConfig


def setup_constance_admin(app, engine):
    """
    Setup SQLAdmin for managing Constance configurations.
    Automatically registers the ConstanceConfig model in the admin interface.
    """

    if app is None or engine is None:
        raise RuntimeError("FastAPI app and SQLAlchemy engine must be provided for SQLAdmin setup.")

    admin = Admin(app, engine)
    admin.add_view(ModelView(ConstanceConfig, engine))
    print("✅ fastapi-constance admin panel registered at /admin")
    return admin
