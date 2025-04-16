from sqladmin import ModelView
from app.models import User, Profile, EmailSetting

class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.first_name, User.last_name, User.email, User.is_superuser]

class ProfileAdmin(ModelView, model=Profile):
    column_list = [Profile.id, Profile.bio, Profile.profile_picture_url, Profile.user]

class EmailSettingAdmin(ModelView, model=EmailSetting):
    column_list = [EmailSetting.id, EmailSetting.email, EmailSetting.password, EmailSetting.email_type, EmailSetting.port, EmailSetting.is_active, EmailSetting.user, EmailSetting.is_admin_mail]

