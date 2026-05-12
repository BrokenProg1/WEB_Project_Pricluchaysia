from flask_login import current_user


def secure_change_to_user():
    # Если каким-то образом категория пользователя не входит в список стандартных, то он становится просто пользователем
    if current_user.role in ['user', 'guide', 'administrator']:
        return
    current_user.role = 'user'