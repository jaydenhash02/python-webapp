import pytest
import random
from src.auth import auth_login_v2, auth_register_v2, auth_logout_v1
from src.channel import channel_invite_v2, channel_details_v2, channel_messages_v2, channel_join_v2, channel_addowner_v1, channel_removeowner_v1, channel_leave_v1
from src.channels import channels_list_v2, channels_listall_v2, channels_create_v2
from src.message import message_send_v2
from src.other import clear_v1
from src.error import InputError, AccessError
from src import config
from src.fixture import channel_fixture
import time


#test if input error is raised with invalid channel id
#uses invalid channel id 
def test_invalid_channel_id(channel_fixture):
    token = channel_fixture[0]
    u_id_two = channel_fixture[3]
    c_id = channel_fixture[6]

    invalid_c_id = random.randint(0, 10)
    while invalid_c_id == c_id:
        invalid_c_id = random.randint(0, 10)
    
    with pytest.raises(InputError):
        channel_invite_v2(token, invalid_c_id, u_id_two)
    with pytest.raises(InputError):
        channel_details_v2(token, invalid_c_id)
    with pytest.raises(InputError):
        channel_messages_v2(token, invalid_c_id, 0)
    with pytest.raises(InputError):
        channel_join_v2(token, invalid_c_id)
    with pytest.raises(InputError):
        channel_addowner_v1(token, invalid_c_id, u_id_two)
    with pytest.raises(InputError):
        channel_removeowner_v1(token, invalid_c_id, u_id_two)
    with pytest.raises(InputError):
        channel_leave_v1(token, invalid_c_id)

#testing if access error if auth_user is not part of the channel
def test_unauthorised_token(channel_fixture):
    token = channel_fixture[0]
    token_two = channel_fixture[2]
    u_id_two = channel_fixture[3]
    token_three = channel_fixture[4]
    u_id_three = channel_fixture[5]
    c_id = channel_fixture[6]
    c_id_two = channels_create_v2(token, 'My Second Channel', False)['channel_id']

    with pytest.raises(AccessError):
        channel_invite_v2(token_two, c_id, u_id_three)
    with pytest.raises(AccessError):
        channel_details_v2(token_two, c_id)
    with pytest.raises(AccessError):
        channel_messages_v2(token_two, c_id, 0)
    with pytest.raises(AccessError):
        channel_join_v2(token_two, c_id_two)
    with pytest.raises(AccessError):
        channel_addowner_v1(token_two, c_id, u_id_two)
    channel_join_v2(token_three, c_id)
    channel_addowner_v1(token, c_id, u_id_three)
    with pytest.raises(AccessError):
        channel_removeowner_v1(token_two, c_id, u_id_three)
    with pytest.raises(AccessError):
        channel_leave_v1(token_two, c_id)

#testing if access error is raised with invalid token
def test_invalid_token(channel_fixture):
    token = channel_fixture[0]
    token_two = channel_fixture[2]
    u_id_two = channel_fixture[3]
    u_id_three = channel_fixture[5]
    c_id = channel_fixture[6]
    c_id_two = channels_create_v2(token, 'My Second Channel', False)['channel_id']
    channel_join_v2(token_two, c_id)
    channel_addowner_v1(token, c_id, u_id_two)
    auth_logout_v1(token) #token is now invalid

    with pytest.raises(AccessError):
        channel_invite_v2(token, c_id, u_id_two)
    with pytest.raises(AccessError):
        channel_details_v2(token, c_id)
    with pytest.raises(AccessError):
        channel_messages_v2(token, c_id, 0)
    with pytest.raises(AccessError):
        channel_join_v2(token, c_id_two)
    with pytest.raises(AccessError):
        channel_addowner_v1(token, c_id, u_id_three)
    with pytest.raises(AccessError):
        channel_removeowner_v1(token, c_id, u_id_two)
    with pytest.raises(AccessError):
        channel_leave_v1(token, c_id)
 

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

    with pytest.raises(InputError):
        channel_invite_v2(token, c_id, invalid_u_id)

#test if user is correctly added to channel
def test_channel_invite(channel_fixture):
    token = channel_fixture[0]
    token_two = channel_fixture[2]
    u_id_two = channel_fixture[3]
    c_id = channel_fixture[6]

    channel_invite_v2(token, c_id, u_id_two)
    assert channels_list_v2(token_two) == {
        'channels': [
            {
                'channel_id': c_id,
                'name': 'My Channel',
            }
        ],
    }

#test if user is correctly added to multiple channels
def test_multiple_channel_invite(channel_fixture):
    token = channel_fixture[0]
    u_id_two = channel_fixture[3]
    c_id = channel_fixture[6]

    c_id_two = channels_create_v2(token, 'My Second Channel', True)['channel_id']
    channel_invite_v2(token, c_id, u_id_two)
    channel_invite_v2(token, c_id_two, u_id_two)
    assert channels_list_v2(token) == {
        'channels': [
            {
                'channel_id': c_id,
                'name': 'My Channel',
            },
            {
                'channel_id': c_id_two,
                'name': 'My Second Channel',
            }
        ],
    }

#test if channel detail correctly lists channels
def test_channel_details(channel_fixture):
    token = channel_fixture[0]
    u_id = channel_fixture[1]
    c_id = channel_fixture[6]

    assert channel_details_v2(token, c_id) == {
        'name': 'My Channel',
        'is_public': True,
        'owner_members': [
            {
                'u_id': u_id,
                'email': 'henrylei@gmail.com',
                'name_first': 'henry',
                'name_last': 'lei',
                'handle_str': 'henrylei',
                'profile_img_url': f'http://localhost:{config.port}/static/default.jpg'
            }
        ],
        'all_members': [
            {
                'u_id': u_id,
                'email': 'henrylei@gmail.com',
                'name_first': 'henry',
                'name_last': 'lei',
                'handle_str': 'henrylei',
                'profile_img_url': f'http://localhost:{config.port}/static/default.jpg'

            }
        ],
    }

#test if channel details lists out multiple members of a channel
def test_multiple_users_channel_details(channel_fixture):
    token = channel_fixture[0]
    u_id = channel_fixture[1]
    token_two = channel_fixture[2]
    u_id_two = channel_fixture[3]
    c_id = channel_fixture[6]

    channel_invite_v2(token, c_id, u_id_two)
    assert channel_details_v2(token, c_id) == {
        'name': 'My Channel',
        'is_public': True,
        'owner_members': [
            {
                'u_id': u_id,
                'email': 'henrylei@gmail.com',
                'name_first': 'henry',
                'name_last': 'lei',
                'handle_str': 'henrylei',
                'profile_img_url': f'http://localhost:{config.port}/static/default.jpg'
            }
        ],
        'all_members': [
            {
                'u_id': u_id,
                'email': 'henrylei@gmail.com',
                'name_first': 'henry',
                'name_last': 'lei',
                'handle_str': 'henrylei',
                'profile_img_url': f'http://localhost:{config.port}/static/default.jpg'
            },
            {
                'u_id': u_id_two,
                'email': 'second@gmail.com',
                'name_first': 'random',
                'name_last': 'person',
                'handle_str': 'randomperson',
                'profile_img_url': f'http://localhost:{config.port}/static/default.jpg'
            }
        ],
    }

    assert channel_details_v2(token, c_id) == channel_details_v2(token_two, c_id)

#test starting index is outside range of messages
#index starting value is 3 however no messages have been sent
def test_channel_messages_invalid_start(channel_fixture):
    token = channel_fixture[0]
    c_id = channel_fixture[6]

    with pytest.raises(InputError):
        channel_messages_v2(token, c_id, 3)


#test channel messages is successful
def test_channel_messages(channel_fixture):
    token = channel_fixture[0]
    u_id = channel_fixture[1]
    c_id = channel_fixture[6]

    m_id = message_send_v2(token, c_id, 'hello')['message_id']
    timestamp = int(time.time())
    assert channel_messages_v2(token, c_id, 0) == {
        'messages': [
            {
                'message_id': m_id,
                'u_id': u_id,
                'message': 'hello',
                'time_created': timestamp,
                'reacts': [],
                'is_pinned': False
            }
        ],
        'start': 0,
        'end': -1,
    }

#testing if normal user attempts to join private channel
def test_join_priv_channel(channel_fixture):
    token = channel_fixture[0]
    token_two = channel_fixture[2]



    c_id_two = channels_create_v2(token, 'My Second Channel', False)['channel_id']
    with pytest.raises(AccessError):
        channel_join_v2(token_two, c_id_two)

#test is normal user successfully joins a public channel
def test_join_channel(channel_fixture):
    token_two = channel_fixture[2]
    c_id = channel_fixture[6]

    channel_join_v2(token_two, c_id)
    assert channels_list_v2(token_two) == {
        'channels': [
        	{
        		'channel_id': c_id,
        		'name': 'My Channel',
        	}
        ],
    }

#testing if global owner successfully attempts to join private channel
def test_join_priv_channel_global_owner(channel_fixture):
    token = channel_fixture[0]
    token_two = channel_fixture[2]
    c_id = channel_fixture[6]


    c_id_two = channels_create_v2(token_two, 'My Second Channel', False)['channel_id']
    channel_join_v2(token, c_id_two)
    assert channels_list_v2(token) == {
        'channels': [
        	{
        		'channel_id': c_id,
        		'name': 'My Channel',
        	},
            {
        		'channel_id': c_id_two,
        		'name': 'My Second Channel',
        	}
        ],
    }

#raises input error when removing the only user/not an owner or adding user who is already an owner
def test_ownership_channel(channel_fixture):
    token = channel_fixture[0]
    u_id = channel_fixture[1]
    u_id_two = channel_fixture[3]
    c_id = channel_fixture[6]


    with pytest.raises(InputError):
        channel_removeowner_v1(token, c_id, u_id_two)
    with pytest.raises(InputError):
        channel_removeowner_v1(token, c_id, u_id)
    with pytest.raises(InputError):
        channel_addowner_v1(token, c_id, u_id)

def test_add_remove_leave(channel_fixture):
    token = channel_fixture[0]
    token_two = channel_fixture[2]
    u_id = channel_fixture[1]
    u_id_two = channel_fixture[3]
    c_id = channel_fixture[6]

    channel_addowner_v1(token, c_id, u_id_two)
    assert channel_details_v2(token, c_id) == {
        'name': 'My Channel',
        'is_public': True,
        'owner_members': [
            {
                'u_id': u_id,
                'email': 'henrylei@gmail.com',
                'name_first': 'henry',
                'name_last': 'lei',
                'handle_str': 'henrylei',
                'profile_img_url': f'http://localhost:{config.port}/static/default.jpg'
            },
            {
                'u_id': u_id_two,
                'email': 'second@gmail.com',
                'name_first': 'random',
                'name_last': 'person',
                'handle_str': 'randomperson',
                'profile_img_url': f'http://localhost:{config.port}/static/default.jpg'
            }
        ],
        'all_members': [
            {
                'u_id': u_id,
                'email': 'henrylei@gmail.com',
                'name_first': 'henry',
                'name_last': 'lei',
                'handle_str': 'henrylei',
                'profile_img_url': f'http://localhost:{config.port}/static/default.jpg'
            },
            {
                'u_id': u_id_two,
                'email': 'second@gmail.com',
                'name_first': 'random',
                'name_last': 'person',
                'handle_str': 'randomperson',
                'profile_img_url': f'http://localhost:{config.port}/static/default.jpg'
            }
        ],
    }
    channel_removeowner_v1(token, c_id, u_id_two)
    assert channel_details_v2(token, c_id) == {
        'name': 'My Channel',
        'is_public': True,
        'owner_members': [
            {
                'u_id': u_id,
                'email': 'henrylei@gmail.com',
                'name_first': 'henry',
                'name_last': 'lei',
                'handle_str': 'henrylei',
                'profile_img_url': f'http://localhost:{config.port}/static/default.jpg'
            }
        ],
        'all_members': [
            {
                'u_id': u_id,
                'email': 'henrylei@gmail.com',
                'name_first': 'henry',
                'name_last': 'lei',
                'handle_str': 'henrylei',
                'profile_img_url': f'http://localhost:{config.port}/static/default.jpg'
            },
        ],
    }
    channel_addowner_v1(token, c_id, u_id_two)
    assert channel_details_v2(token, c_id) == {
        'name': 'My Channel',
        'is_public': True,
        'owner_members': [
            {
                'u_id': u_id,
                'email': 'henrylei@gmail.com',
                'name_first': 'henry',
                'name_last': 'lei',
                'handle_str': 'henrylei',
                'profile_img_url': f'http://localhost:{config.port}/static/default.jpg'
            },
            {
                'u_id': u_id_two,
                'email': 'second@gmail.com',
                'name_first': 'random',
                'name_last': 'person',
                'handle_str': 'randomperson',
                'profile_img_url': f'http://localhost:{config.port}/static/default.jpg'
            }
        ],
        'all_members': [
            {
                'u_id': u_id,
                'email': 'henrylei@gmail.com',
                'name_first': 'henry',
                'name_last': 'lei',
                'handle_str': 'henrylei',
                'profile_img_url': f'http://localhost:{config.port}/static/default.jpg'
            },
            {
                'u_id': u_id_two,
                'email': 'second@gmail.com',
                'name_first': 'random',
                'name_last': 'person',
                'handle_str': 'randomperson',
                'profile_img_url': f'http://localhost:{config.port}/static/default.jpg'
            }
        ],
    }
    channel_leave_v1(token_two, c_id)
    assert channel_details_v2(token, c_id) == {
        'name': 'My Channel',
        'is_public': True,
        'owner_members': [
            {
                'u_id': u_id,
                'email': 'henrylei@gmail.com',
                'name_first': 'henry',
                'name_last': 'lei',
                'handle_str': 'henrylei',
                'profile_img_url': f'http://localhost:{config.port}/static/default.jpg'
            }
        ],
        'all_members': [
            {
                'u_id': u_id,
                'email': 'henrylei@gmail.com',
                'name_first': 'henry',
                'name_last': 'lei',
                'handle_str': 'henrylei',
                'profile_img_url': f'http://localhost:{config.port}/static/default.jpg'
            },
        ],
    }

def test_member_cannot_remove_owner(channel_fixture):
    token_two = channel_fixture[2]
    u_id = channel_fixture[1]
    c_id = channel_fixture[6]
    channel_join_v2(token_two, c_id)
    with pytest.raises(AccessError):
        channel_removeowner_v1(token_two, c_id, u_id)
        

def test_nonmember_cannot_remove_owner(channel_fixture):
    token_two = channel_fixture[2]
    u_id = channel_fixture[1]
    c_id = channel_fixture[6]
    with pytest.raises(AccessError):
        channel_removeowner_v1(token_two, c_id, u_id)

def test_global_owner_can_remove_owner(channel_fixture):
    token = channel_fixture[0]
    token_two = channel_fixture[2]
    token_three = channel_fixture[4]
    u_id_two = channel_fixture[3]
    u_id_three = channel_fixture[5]
    c_id_two = channels_create_v2(token_two, "jimmyw", True)['channel_id']
    channel_join_v2(token_three, c_id_two)
    channel_addowner_v1(token, c_id_two, u_id_three)
    channel_removeowner_v1(token, c_id_two, u_id_three)
    assert channel_details_v2(token_two, c_id_two) == {
        'name': 'jimmyw',
        'is_public': True,
        'owner_members': [
            {
                'u_id': u_id_two,
                'email': 'second@gmail.com',
                'name_first': 'random',
                'name_last': 'person',
                'handle_str': 'randomperson',
                'profile_img_url': f'http://localhost:{config.port}/static/default.jpg'
            }
        ],
        'all_members': [
            {
                'u_id': u_id_two,
                'email': 'second@gmail.com',
                'name_first': 'random',
                'name_last': 'person',
                'handle_str': 'randomperson',
                'profile_img_url': f'http://localhost:{config.port}/static/default.jpg'
            }
        ],
    }

def test_owner_can_remove_owner(channel_fixture):
    token = channel_fixture[0]
    token_two = channel_fixture[2]
    u_id = channel_fixture[1]
    u_id_two = channel_fixture[3]
    c_id = channel_fixture[6]
    channel_join_v2(token_two, c_id)
    channel_addowner_v1(token, c_id, u_id_two)
    channel_removeowner_v1(token, c_id, u_id)
    assert channel_details_v2(token_two, c_id) == {
        'name': 'My Channel',
        'is_public': True,
        'owner_members': [
            {
                'u_id': u_id_two,
                'email': 'second@gmail.com',
                'name_first': 'random',
                'name_last': 'person',
                'handle_str': 'randomperson',
                'profile_img_url': f'http://localhost:{config.port}/static/default.jpg'
            }
        ],
        'all_members': [
            {
                'u_id': u_id_two,
                'email': 'second@gmail.com',
                'name_first': 'random',
                'name_last': 'person',
                'handle_str': 'randomperson',
                'profile_img_url': f'http://localhost:{config.port}/static/default.jpg'
            }
        ],
    }