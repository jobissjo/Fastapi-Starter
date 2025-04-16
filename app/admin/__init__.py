from sqladmin import Admin
from app.core.db_config import engine
from app.admin.models import EmailSettingAdmin, UserAdmin,ProfileAdmin


def setup_admin(app):
    admin = Admin(app, engine)
    admin.add_view(UserAdmin)
    admin.add_view(ProfileAdmin)
    admin.add_view(EmailSettingAdmin)