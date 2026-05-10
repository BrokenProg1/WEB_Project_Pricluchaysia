from flask_login import current_user


def secure_change_to_user(user):
    if current_user.role in ['user', 'guide', 'administrator']:
        return
    current_user.role = 'user'