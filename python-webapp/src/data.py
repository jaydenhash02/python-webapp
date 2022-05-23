from json import loads, dumps

data = {
    'users': [
    ],
    'channels': [
    ],
    'messages': [
    ],
    'dms': [
    ],
    'deleted_users': [
    ],
    'notifications': [
    ],
    'user_analytics': [
    ],
    'server_analytics': {
        'channels': [],
        'dms': [],
        'messages': [],
    }
}

user_template = {
    'auth_user_id': 1,
    'email': 'cs1531@cse.unsw.edu.au',
    'password': '12345qwerty',
    'name_first': 'Hayden',
    'name_last': 'Jacobs',
    'handle_str': 'haydenjacobs',
    'permission_id': 1,
    'session_id': [1],
    'profile_img_url': 'default.jpg',
    'reset_code': 1,
}

channel_template = {
    'channel_id': 1,
    'name': 'channel1',
    'owners_id': [1],
    'members_id': [2],
    'messages': [],
    'is_active': False, 
    'time_finish': None,
    'standup_messages': '',
    'private': True,
}

message_template = {
    'message_id': 1,
    'user_id': 1,
    'channel_id': 1,
    'dm_id': None,
    'message': 'Hello world',
    'time_created': 1582426789,
    'reacts': [],
    'is_pinned': False
}

dms_template = {
    'dm_id': 1,
    'name': 'dm1',
    'owners_id': [1],
    'members_id': [2],
    'messages': [],
    'private': True,
}

notification_template = {
    'channel_id': 1,
    'dm_id': 1,
    'user_id': [],
    'message': 'hello'
}

user_analytics_template = {
    'user_id': 1,
    'channels': [],
    'dms': [],
    'messages': [],
}

server_analytics_template = {
    'channels': [],
    'dms': [],
    'messages': [],
}

SECRET = 'ilovecompsciitissuperfun'

def load_data():
    global data
    try:
        with open('data.json', 'r') as file:
            data = loads(file.read())
    except:
        with open('data.json', 'w+') as file:
            file.write(dumps(data))

def get_data():
    global data
    return data

def save():
    data = get_data()
    with open('data.json', 'w+') as file:
        file.write(dumps(data))
