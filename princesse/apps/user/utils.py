from user.models import User


def get_output_data(data):
    data.pop('password', None)
    data['token'] = User.get_token_user(data['username'])
    return data