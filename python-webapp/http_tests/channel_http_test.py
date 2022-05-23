import pytest
import requests
import json
from src import config
from src.other import clear_v1
import random
import time
from src.http_fixture import channel_fixture

#test if input error is raised with invalid channel id
#uses invalid channel id 
def test_invalid_channel_id(channel_fixture):
    token = channel_fixture[0]
    u_id_two = channel_fixture[3]
    c_id = channel_fixture[6]

    invalid_c_id = random.randint(0, 10)
    while invalid_c_id == c_id:
        invalid_c_id = random.randint(0, 10)
    
    assert requests.post(config.url + "channel/invite/v2", json={"token": token,"channel_id": invalid_c_id, "u_id": u_id_two}).status_code == 400
    assert requests.get(config.url + "channel/details/v2", params={"token": token,"channel_id": invalid_c_id}).status_code == 400
    assert requests.get(config.url + "channel/messages/v2", params={"token": token,"channel_id": invalid_c_id, "start": 0}).status_code == 400
    assert requests.post(config.url + "channel/join/v2", json={"token": token,"channel_id": invalid_c_id}).status_code == 400
    assert requests.post(config.url + "channel/addowner/v1", json={"token": token,"channel_id": invalid_c_id, "u_id": u_id_two}).status_code == 400
    assert requests.post(config.url + "channel/removeowner/v1", json={"token": token,"channel_id": invalid_c_id, "u_id": u_id_two}).status_code == 400
    assert requests.post(config.url + "channel/leave/v1", json={"token": token,"channel_id": invalid_c_id}).status_code == 400

#testing if access error is raised with invalid token
#uses unauthorised token as token_two is not part any channels
def test_unauthorised_token(channel_fixture):
    token = channel_fixture[0]
    token_two = channel_fixture[2]
    u_id_two = channel_fixture[3]
    token_three = channel_fixture[4]
    u_id_three = channel_fixture[5]
    c_id = channel_fixture[6]
    c_id_two = requests.post(config.url + "channels/create/v2", json={"token": token, "name": "My Second Channel", "is_public": False}).json()["channel_id"]
    
    assert requests.post(config.url + "channel/invite/v2", json={"token": token_two,"channel_id": c_id, "u_id": u_id_three}).status_code == 403
    assert requests.get(config.url + "channel/details/v2", params={"token": token_two,"channel_id": c_id}).status_code == 403
    assert requests.get(config.url + "channel/messages/v2", params={"token": token_two,"channel_id": c_id, "start": 0}).status_code == 403
    assert requests.post(config.url + "channel/join/v2", json={"token": token_two,"channel_id": c_id_two}).status_code == 403
    assert requests.post(config.url + "channel/addowner/v1", json={"token": token_two,"channel_id": c_id, "u_id": u_id_two}).status_code == 403

    requests.post(config.url + "channel/join/v2", json={"token": token_three,"channel_id": c_id})
    requests.post(config.url + "channel/addowner/v1", json={"token": token,"channel_id": c_id, "u_id": u_id_three})

    assert requests.post(config.url + "channel/removeowner/v1", json={"token": token_two,"channel_id": c_id, "u_id": u_id_three}).status_code == 403
    assert requests.post(config.url + "channel/leave/v1", json={"token": token_two,"channel_id": c_id}).status_code == 403

#testing if access error is raised with invalid token
def test_invalid_token(channel_fixture):
    token = channel_fixture[0]
    token_two = channel_fixture[2]
    u_id_two = channel_fixture[3]
    u_id_three = channel_fixture[5]
    c_id = channel_fixture[6]
    c_id_two = requests.post(config.url + "channels/create/v2", json={"token": token, "name": "My Second Channel", "is_public": False}).json()["channel_id"]
    requests.post(config.url + "channel/join/v2", json={"token": token_two,"channel_id": c_id})
    requests.post(config.url + "channel/addowner/v1", json={"token": token,"channel_id": c_id, "u_id": u_id_two})
    requests.post(config.url + "auth/logout/v1", json={"token": token}) #token is now invalid

    assert requests.post(config.url + "channel/invite/v2", json={"token": token,"channel_id": c_id, "u_id": u_id_two}).status_code == 403
    assert requests.get(config.url + "channel/details/v2", params={"token": token,"channel_id": c_id}).status_code == 403
    assert requests.get(config.url + "channel/messages/v2", params={"token": token,"channel_id": c_id, "start": 0}).status_code == 403
    assert requests.post(config.url + "channel/join/v2", json={"token": token,"channel_id": c_id_two}).status_code == 403
    assert requests.post(config.url + "channel/addowner/v1", json={"token": token,"channel_id": c_id, "u_id": u_id_three}).status_code == 403
    assert requests.post(config.url + "channel/removeowner/v1", json={"token": token,"channel_id": c_id, "u_id": u_id_two}).status_code == 403
    assert requests.post(config.url + "channel/leave/v1", json={"token": token,"channel_id": c_id}).status_code == 403

#test if input error is raised with invalid user id
#uses invalid user id
def test_invalid_user_id(channel_fixture):
    token = channel_fixture[0]
    u_id = channel_fixture[1]
    u_id_two = channel_fixture[3]
    u_id_three = channel_fixture[5] 
    c_id = channel_fixture[6]

    invalid_u_id = random.randint(0, 10)
    while invalid_u_id == u_id or invalid_u_id == u_id_two or invalid_u_id == u_id_three:
        invalid_u_id = random.randint(0, 10)

    assert requests.post(config.url + "channel/invite/v2", json={"token": token,"channel_id": c_id, "u_id": invalid_u_id}).status_code == 400

#test if user is correctly added to channel
def test_channel_invite(channel_fixture):
    token = channel_fixture[0]
    token_two = channel_fixture[2]
    u_id_two = channel_fixture[3]
    c_id = channel_fixture[6]

    requests.post(config.url + "channel/invite/v2", json={"token": token,"channel_id": c_id, "u_id": u_id_two})
    data = {
        "channels": [
            {
                "channel_id": c_id,
                "name": "My Channel",
            }
        ]
    }
    info = requests.get(config.url + "channels/list/v2", params={"token": token_two})
    assert json.loads(info.text) == data

#test if user is correctly added to multiple channels
def test_multiple_channel_invite(channel_fixture):
    token = channel_fixture[0]
    u_id_two = channel_fixture[3]
    c_id = channel_fixture[6]

    c_id_two = requests.post(config.url + "channels/create/v2", json={"token": token,"name": "My Second Channel", "is_public": True}).json()["channel_id"]

    requests.post(config.url + "channel/invite/v2", json={"token": token,"channel_id": c_id, "u_id": u_id_two})
    requests.post(config.url + "channel/invite/v2", json={"token": token,"channel_id": c_id_two, "u_id": u_id_two})
    data = {
        "channels": [
            {
                "channel_id": c_id,
                "name": "My Channel",
            },
            {
                "channel_id": c_id_two,
                "name": "My Second Channel",
            }
        ]
    }

    info = requests.get(config.url + "channels/list/v2", params={"token": token})
    assert json.loads(info.text) == data

#test if channel detail correctly lists channels
def test_channel_details(channel_fixture):
    token = channel_fixture[0]
    u_id = channel_fixture[1]
    c_id = channel_fixture[6]

    data = {
        "name": "My Channel",
        "is_public": True,
        "owner_members": [
            {
                "u_id": u_id,
                "email": "henrylei@gmail.com",
                "name_first": "henry",
                "name_last": "lei",
                "handle_str": "henrylei",
                'profile_img_url': f'http://localhost:{config.port}/static/default.jpg'
            }
        ],
        "all_members": [
            {
                "u_id": u_id,
                "email": "henrylei@gmail.com",
                "name_first": "henry",
                "name_last": "lei",
                "handle_str": "henrylei",
                'profile_img_url': f'http://localhost:{config.port}/static/default.jpg'
            }
        ]
    }

    info = requests.get(config.url + "channel/details/v2", params={"token": token, "channel_id": c_id})
    assert json.loads(info.text) == data

#test if channel details lists out multiple members of a channel
def test_multiple_users_channel_details(channel_fixture):
    token = channel_fixture[0]
    u_id = channel_fixture[1]
    token_two = channel_fixture[2]
    u_id_two = channel_fixture[3]
    c_id = channel_fixture[6]

    requests.post(config.url + "channel/invite/v2", json={"token": token,"channel_id": c_id, "u_id": u_id_two})
    data = {
        "name": "My Channel",
        "is_public": True,
        "owner_members": [
            {
                "u_id": u_id,
                "email": "henrylei@gmail.com",
                "name_first": "henry",
                "name_last": "lei",
                "handle_str": "henrylei",
                'profile_img_url': f'http://localhost:{config.port}/static/default.jpg'
            }
        ],
        "all_members": [
            {
                "u_id": u_id,
                "email": "henrylei@gmail.com",
                "name_first": "henry",
                "name_last": "lei",
                "handle_str": "henrylei",
                'profile_img_url': f'http://localhost:{config.port}/static/default.jpg'
            },
            {
                "u_id": u_id_two,
                "email": "second@gmail.com",
                "name_first": "random",
                "name_last": "person",
                "handle_str": "randomperson",
                'profile_img_url': f'http://localhost:{config.port}/static/default.jpg'
            }
        ]
    }

    info = requests.get(config.url + "channel/details/v2", params={"token": token, "channel_id": c_id})
    assert json.loads(info.text) == data

    info2 = requests.get(config.url + "channel/details/v2", params={"token": token_two, "channel_id": c_id})
    assert json.loads(info.text) == json.loads(info2.text)

#test starting index is outside range of messages
#index starting value is 3 however no messages have been sent
def test_channel_messages_invalid_start(channel_fixture):
    token = channel_fixture[0]
    c_id = channel_fixture[6]

    assert requests.get(config.url + "channel/messages/v2", params={"token": token,"channel_id": c_id, "start": 3}).status_code == 400

#test channel messages is successful
def test_channel_messages(channel_fixture):
    token = channel_fixture[0]
    u_id = channel_fixture[1]
    c_id = channel_fixture[6]

    m_id = requests.post(config.url + "message/send/v2", json={"token": token,"channel_id": c_id, "message": "hello"}).json()["message_id"]

    timestamp = int(time.time())
    data = {
        "messages": [
            {
                "message_id": m_id,
                "u_id": u_id,
                "message": "hello",
                "time_created": timestamp,
                "reacts": [],
                "is_pinned": False
            }
        ],
        "start": 0,
        "end": -1,
    }

    info = requests.get(config.url + "channel/messages/v2", params={"token": token, "channel_id": c_id, "start": 0})
    assert json.loads(info.text) == data

#testing if normal user attempts to join private channel
def test_join_priv_channel(channel_fixture):
    token = channel_fixture[0]
    token_two = channel_fixture[2]

    c_id_two = requests.post(config.url + "channels/create/v2", json={"token": token, "name": "My Second Channel", "is_public": False}).json()["channel_id"]
    assert requests.post(config.url + "channel/join/v2", json={"token": token_two,"channel_id": c_id_two}).status_code == 403

#test is normal user successfully joins a public channel
def test_join_channel(channel_fixture):
    token_two = channel_fixture[2]
    c_id = channel_fixture[6]

    requests.post(config.url + "channel/join/v2", json={"token": token_two,"channel_id": c_id})
    data = {
        "channels": [
        	{
        		"channel_id": c_id,
        		"name": "My Channel",
        	}
        ]
    }

    info = requests.get(config.url + "channels/list/v2", params={"token": token_two})
    assert json.loads(info.text) == data

#testing if global owner successfully attempts to join private channel
def test_join_priv_channel_global_owner(channel_fixture):
    token = channel_fixture[0]
    token_two = channel_fixture[2]
    c_id = channel_fixture[6]

    c_id_two = requests.post(config.url + "channels/create/v2", json={"token": token_two, "name": "My Second Channel", "is_public": False}).json()["channel_id"]
    requests.post(config.url + "channel/join/v2", json={"token": token, "channel_id": c_id_two})

    data = {
        "channels": [
        	{
        		"channel_id": c_id,
        		"name": "My Channel",
        	},
            {
        		"channel_id": c_id_two,
        		"name": "My Second Channel",
        	}
        ]
    }

    info = requests.get(config.url + "channels/list/v2", params={"token": token})
    assert json.loads(info.text) == data

#raises input error when removing the only user/not an owner or adding user who is already an owner
def test_ownership_channel(channel_fixture):
    token = channel_fixture[0]
    token_two = channel_fixture[2]
    u_id = channel_fixture[1]
    u_id_two = channel_fixture[3]
    c_id = channel_fixture[6]

    assert requests.post(config.url + "channel/removeowner/v1", json={"token": token_two,"channel_id": c_id, "u_id": u_id_two}).status_code == 403
    assert requests.post(config.url + "channel/removeowner/v1", json={"token": token,"channel_id": c_id, "u_id": u_id}).status_code == 400
    assert requests.post(config.url + "channel/addowner/v1", json={"token": token,"channel_id": c_id, "u_id": u_id}).status_code == 400

#test if add remove and leave correctly work
def test_add_remove_leave(channel_fixture):
    token = channel_fixture[0]
    token_two = channel_fixture[2]
    u_id = channel_fixture[1]
    u_id_two = channel_fixture[3]
    c_id = channel_fixture[6]

    requests.post(config.url + "channel/addowner/v1", json={"token": token,"channel_id": c_id, "u_id": u_id_two})
    data = {
        "name": "My Channel",
        "is_public": True,
        "owner_members": [
            {
                "u_id": u_id,
                "email": "henrylei@gmail.com",
                "name_first": "henry",
                "name_last": "lei",
                "handle_str": "henrylei",
                'profile_img_url': f'http://localhost:{config.port}/static/default.jpg'
            },
            {
                "u_id": u_id_two,
                "email": "second@gmail.com",
                "name_first": "random",
                "name_last": "person",
                "handle_str": "randomperson",
                'profile_img_url': f'http://localhost:{config.port}/static/default.jpg'
            }
        ],
        "all_members": [
            {
                "u_id": u_id,
                "email": "henrylei@gmail.com",
                "name_first": "henry",
                "name_last": "lei",
                "handle_str": "henrylei",
                'profile_img_url': f'http://localhost:{config.port}/static/default.jpg'
            },
            {
                "u_id": u_id_two,
                "email": "second@gmail.com",
                "name_first": "random",
                "name_last": "person",
                "handle_str": "randomperson",
                'profile_img_url': f'http://localhost:{config.port}/static/default.jpg'
            }
            
        ]
    }

    info = requests.get(config.url + "channel/details/v2", params={"token": token, "channel_id": c_id})
    assert json.loads(info.text) == data

    requests.post(config.url + "channel/removeowner/v1", json={"token": token,"channel_id": c_id, "u_id": u_id_two})
    data = {
        "name": "My Channel",
        "is_public": True,
        "owner_members": [
            {
                "u_id": u_id,
                "email": "henrylei@gmail.com",
                "name_first": "henry",
                "name_last": "lei",
                "handle_str": "henrylei",
                'profile_img_url': f'http://localhost:{config.port}/static/default.jpg'
            }
        ],
        "all_members": [
            {
                "u_id": u_id,
                "email": "henrylei@gmail.com",
                "name_first": "henry",
                "name_last": "lei",
                "handle_str": "henrylei",
                'profile_img_url': f'http://localhost:{config.port}/static/default.jpg'
            },
        ],
    }

    info = requests.get(config.url + "channel/details/v2", params={"token": token, "channel_id": c_id})
    assert json.loads(info.text) == data

    requests.post(config.url + "channel/addowner/v1", json={"token": token,"channel_id": c_id, "u_id": u_id_two})
    data = {
        "name": "My Channel",
        "is_public": True,
        "owner_members": [
            {
                "u_id": u_id,
                "email": "henrylei@gmail.com",
                "name_first": "henry",
                "name_last": "lei",
                "handle_str": "henrylei",
                'profile_img_url': f'http://localhost:{config.port}/static/default.jpg'
            },
            {
                "u_id": u_id_two,
                "email": "second@gmail.com",
                "name_first": "random",
                "name_last": "person",
                "handle_str": "randomperson",
                'profile_img_url': f'http://localhost:{config.port}/static/default.jpg'
            }
        ],
        "all_members": [
            {
                "u_id": u_id,
                "email": "henrylei@gmail.com",
                "name_first": "henry",
                "name_last": "lei",
                "handle_str": "henrylei",
                'profile_img_url': f'http://localhost:{config.port}/static/default.jpg'
            },
            {
                "u_id": u_id_two,
                "email": "second@gmail.com",
                "name_first": "random",
                "name_last": "person",
                "handle_str": "randomperson",
                'profile_img_url': f'http://localhost:{config.port}/static/default.jpg'
            }
        ]
    }

    info = requests.get(config.url + "channel/details/v2", params={"token": token, "channel_id": c_id})
    assert json.loads(info.text) == data

    requests.post(config.url + "channel/leave/v1", json={"token": token_two,"channel_id": c_id})
    data = {
        "name": "My Channel",
        "is_public": True,
        "owner_members": [
            {
                "u_id": u_id,
                "email": "henrylei@gmail.com",
                "name_first": "henry",
                "name_last": "lei",
                "handle_str": "henrylei",
                'profile_img_url': f'http://localhost:{config.port}/static/default.jpg'
            }
        ],
        "all_members": [
            {
                "u_id": u_id,
                "email": "henrylei@gmail.com",
                "name_first": "henry",
                "name_last": "lei",
                "handle_str": "henrylei",
                'profile_img_url': f'http://localhost:{config.port}/static/default.jpg'
            },
        ]
    }

    info = requests.get(config.url + "channel/details/v2", params={"token": token, "channel_id": c_id})
    print(info.json())
    assert json.loads(info.text) == data #THIS ONE