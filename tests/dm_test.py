import pytest
import random
import time
from src import config
from src.auth import auth_login_v2, auth_register_v2, auth_logout_v1
from src.message import message_remove_v1
from src.dm import dm_details_v1, dm_list_v1, dm_create_v1, dm_remove_v1, dm_invite_v1, dm_leave_v1, dm_messages_v1, message_senddm_v1, message_sendlaterdm_v1
from src.other import clear_v1
from src.error import InputError, AccessError
from src.fixture import dm_fixture, message_fixture

#creates a new dm and checks that the output matches
def test_dm_create(dm_fixture):
    token = dm_fixture[0]
    u_id_three = dm_fixture[5]
    assert dm_create_v1(token, [u_id_three]) == {'dm_id': dm_list_v1(token)['dms'][1]['dm_id'], 'dm_name': ['henrylei', 'randomperson0']}

#test if input error is raised with invalid dm id
def test_invalid_dm_id(dm_fixture):
    token = dm_fixture[0]
    u_id_two = dm_fixture[3]
    dm_id = dm_fixture[6]

    invalid_dm_id = random.randint(0, 10)
    while invalid_dm_id == dm_id:
        invalid_dm_id = random.randint(0, 10)
    
    with pytest.raises(InputError):
        dm_invite_v1(token, invalid_dm_id, u_id_two)
    with pytest.raises(InputError):
        dm_details_v1(token, invalid_dm_id)
    with pytest.raises(InputError):
        dm_remove_v1(token, invalid_dm_id)
    with pytest.raises(InputError):
        dm_leave_v1(token, invalid_dm_id)
    with pytest.raises(InputError):
        dm_messages_v1(token, invalid_dm_id, 0)

#test if input error is raised if u_id does not refer to a valid user
def test_invalid_user_id(dm_fixture):
    token = dm_fixture[0]
    u_id = dm_fixture[1]
    u_id_two = dm_fixture[3]
    u_id_three = dm_fixture[5]
    dm_id = dm_fixture[6]

    invalid_u_id = random.randint(0, 10)
    while invalid_u_id == u_id or invalid_u_id == u_id_two or invalid_u_id == u_id_three:
        invalid_u_id = random.randint(0, 10)

    with pytest.raises(InputError):
        dm_create_v1(token, [invalid_u_id])
    with pytest.raises(InputError):
        dm_invite_v1(token, dm_id, invalid_u_id)

# raise access error when the Authorised user is not a member of this DM with dm_id
def test_not_member_of_dm(dm_fixture):
    token_three = dm_fixture[4]
    u_id_two = dm_fixture[3]
    dm_id = dm_fixture[6]
    
    with pytest.raises(AccessError):
        dm_invite_v1(token_three, dm_id, u_id_two)
    with pytest.raises(AccessError):
        dm_details_v1(token_three, dm_id)
    with pytest.raises(AccessError):
        dm_leave_v1(token_three, dm_id)
    with pytest.raises(AccessError):
        dm_messages_v1(token_three, dm_id, 0)
    with pytest.raises(AccessError):
        message_senddm_v1(token_three, dm_id, 'hello')


#raise access error if invalid token
def test_invalid_token(dm_fixture):
    token = dm_fixture[0]
    u_id_two = dm_fixture[3]
    dm_id = dm_fixture[6]

    auth_logout_v1(token)
    invalid_token = token
    
    with pytest.raises(AccessError):
        dm_invite_v1(invalid_token, dm_id, u_id_two)
    with pytest.raises(AccessError):
        dm_details_v1(invalid_token, dm_id)
    with pytest.raises(AccessError):
        dm_leave_v1(invalid_token, dm_id)
    with pytest.raises(AccessError):
        dm_messages_v1(invalid_token, dm_id, 0)
    with pytest.raises(AccessError):
        message_senddm_v1(invalid_token, dm_id, 'hello')

#test if dm details correctly lists members
def test_dm_details(dm_fixture):
    token = dm_fixture[0]
    u_id = dm_fixture[1]
    u_id_two = dm_fixture[3]
    dm_id = dm_fixture[6]

    assert dm_details_v1(token, dm_id) == {
        'name': ['henrylei', 'randomperson'],
        'members': [
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
        ]
    } 

#test if a single dm is correctly listed
def test_single_dm_list(dm_fixture):
    token = dm_fixture[0]
    dm_id = dm_fixture[6]

    assert dm_list_v1(token) == {
        'dms': [
            {
                'dm_id': dm_id,
                'name': ['henrylei', 'randomperson'],
            }
        ]
    } 

#test if multiple dms are correctly listed
def test_mutiple_dms_list(dm_fixture):
    token = dm_fixture[0]
    u_id_three = dm_fixture[5]
    dm_id = dm_fixture[6]
    dm_id_two = dm_create_v1(token, [u_id_three])['dm_id']

    assert dm_list_v1(token) == {
        'dms': [
        	{
        		'dm_id': dm_id,
        		'name': ['henrylei', 'randomperson'],
        	},
            {
        		'dm_id': dm_id_two,
        		'name': ['henrylei', 'randomperson0'],
        	}
        ]
    }

#test if dm ids are not equal
def test_dm_ids_not_equal(dm_fixture): 
    token = dm_fixture[0]
    token_two = dm_fixture[2]
    u_id_three = dm_fixture[5]
    dm_id = dm_fixture[6]
    dm_id_two = dm_create_v1(token_two, [u_id_three])['dm_id']
    dm_id_three = dm_create_v1(token, [u_id_three])['dm_id']

    assert dm_id != dm_id_two
    assert dm_id != dm_id_three
    assert dm_id_two != dm_id_three

#raise error when user is not original dm creator
def test_check_unauthorised_remove(dm_fixture):
    token_two = dm_fixture[2]
    dm_id = dm_fixture[6]

    with pytest.raises(AccessError):
        dm_remove_v1(token_two, dm_id)

#test if user is correctly invited to dm
def test_dm_invite(dm_fixture): 
    token = dm_fixture[0]
    token_three = dm_fixture[4]
    u_id_three = dm_fixture[5]
    dm_id = dm_fixture[6]
    dm_invite_v1(token, dm_id, u_id_three)

    assert dm_list_v1(token_three) == {
        'dms': [
            {
                'dm_id': dm_id,
                'name': ['henrylei', 'randomperson'],
            }
        ]
    }   

#check if user successfully left dm
def test_dm_leave(dm_fixture): 
    token = dm_fixture[0]
    dm_id = dm_fixture[6]
    dm_leave_v1(token, dm_id)

    assert dm_list_v1(token) == {
        'dms': []
    }

#test starting index is outside range of messages
#index starting value is 3 however no messages have been sent
def test_dm_messages_invalid_start(dm_fixture):
    token = dm_fixture[0]
    dm_id = dm_fixture[6]

    with pytest.raises(InputError):
        dm_messages_v1(token, dm_id, 3)

#raises input error if message is over 1000 characters
def test_dm_message_too_long(dm_fixture):
    token = dm_fixture[0]
    dm_id = dm_fixture[6]
    with pytest.raises(InputError):
        message_senddm_v1(token, dm_id, "A while back I needed to count the amount of letters that a piece of text in an email template had (to avoid passing any character limits). Unfortunately, I could not think of a quick way to do so on my macbook and I therefore turned to the Internet. There were a couple of tools out there, but none of them met my standards and since I am a web designer I thought: why not do it myself and help others along the way? And... here is the result, hope it helA while back I needed to count the amount of letters that a piece of text in an email template had (to avoid passing any character limits). Unfortunately, I could not think of a quick way to do so on my macbook and I therefore turned to the Internet.There were a couple of tools out there, but none of them met my standards and since I am a web designer I thought: why not do it myself and help others along the way? A while back I needed to count the amount of letters that a piece of text in an email template had (to avoid passing any charact")   

#sends a dm message and tests that it is listed properly
def test_dm_messages(dm_fixture): 
    token = dm_fixture[0]
    u_id = dm_fixture[1]
    dm_id = dm_fixture[6]
    timestamp = int(time.time())
    message_id = message_senddm_v1(token, dm_id, 'hello')['message_id']

    assert dm_messages_v1(token, dm_id, 0) == {
        'messages': [
            {
                'message_id': message_id,
                'u_id': u_id,
                'message': 'hello',
                'time_created': timestamp,
                'reacts': [],
                'is_pinned': False
            }
        ],
        'start': 0,
        'end': -1
    }

#test if dm is sent 5 secs before raises InputError
def test_dm_send_later_error(dm_fixture):
    token = dm_fixture[0]
    dm_id = dm_fixture[6]

    future_timestamp = int(time.time()) - 5 
    with pytest.raises(InputError):
        message_sendlaterdm_v1(token, dm_id, 'hello', future_timestamp)

#test if message is sent 5 secs later then deletes msg
def test_message_send_later(dm_fixture):
    token = dm_fixture[0]
    dm_id = dm_fixture[6]
    u_id = dm_fixture[1]

    future_timestamp = int(time.time()) + 5
    m_id = message_sendlaterdm_v1(token, dm_id, 'hello', future_timestamp)['message_id']
    assert dm_messages_v1(token, dm_id, 0) == {
        'messages': [
            {
                'message_id': m_id,
                'u_id': u_id,
                'message': 'hello',
                'time_created': future_timestamp,
                'reacts': [],
                'is_pinned': False 
            }
        ],
        'start': 0,
        'end': -1,
    }
    message_remove_v1(token, m_id)
