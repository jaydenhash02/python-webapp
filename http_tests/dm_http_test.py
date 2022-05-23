import json
import requests
import urllib
import pytest
from src import config
import random
import time
from src.auth import auth_login_v2, auth_register_v2, auth_logout_v1
from src.message import message_remove_v1
from src.dm import dm_details_v1, dm_list_v1, dm_create_v1, dm_remove_v1, dm_invite_v1, dm_leave_v1, dm_messages_v1, message_senddm_v1
from src.other import clear_v1
from src.error import InputError, AccessError
from src.http_fixture import dm_fixture

#creates a new dm and checks that the output matches
def test_dm_create(dm_fixture): 
    token = dm_fixture[0]
    u_id_three = dm_fixture[5]
    resp = requests.post(config.url + 'dm/create/v1', json={
        'token': token,
        'u_ids': [u_id_three]
    })
    dm_id2 = requests.get(config.url + 'dm/list/v1', params={'token': token}).json()['dms'][1]['dm_id']
    assert json.loads(resp.text) == {'dm_id': dm_id2, 'dm_name': ['henrylei', 'randomperson0']}

#test if a single dm is correctly listed
def test_single_dm_list(dm_fixture): 
    token = dm_fixture[0]
    dm_id = dm_fixture[6]
    resp = requests.get(config.url + 'dm/list/v1', params={
        'token': token
    })
    assert json.loads(resp.text) == {
        'dms': [
            {
                'dm_id': dm_id, 
                'name': ['henrylei', 'randomperson']
            }
        ]
    }

#test if multiple dms are correctly listed
def test_mutiple_dms_list(dm_fixture):
    token = dm_fixture[0]
    u_id_three = dm_fixture[5]
    dm_id = dm_fixture[6]

    dm_id_two = requests.post(config.url + 'dm/create/v1', json={'token': token, 'u_ids': [u_id_three]}).json()['dm_id']
    resp = requests.get(config.url + 'dm/list/v1', params={
        'token': token
    })

    assert json.loads(resp.text) == {
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
#test if dm details correctly lists members
def test_dm_details_v1(dm_fixture):
    token = dm_fixture[0]
    u_id = dm_fixture[1]
    u_id_two = dm_fixture[3]
    dm_id = dm_fixture[6]
    resp = requests.get(config.url + 'dm/details/v1', params={
        'token': token,
        'dm_id': dm_id
    })
    assert json.loads(resp.text) == {
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

#test if input error is raised with invalid dm id
def test_invalid_dm_id(dm_fixture):
    token = dm_fixture[0]
    u_id_two = dm_fixture[3]
    dm_id = dm_fixture[6]

    invalid_dm_id = random.randint(0, 10)
    while invalid_dm_id == dm_id:
        invalid_dm_id = random.randint(0, 10)

    assert requests.post(config.url + "dm/invite/v1", json={"token": token, "dm_id": invalid_dm_id, "u_id": u_id_two}).status_code == 400
    assert requests.get(config.url + "dm/details/v1", params={"token": token, "dm_id": invalid_dm_id}).status_code == 400
    assert requests.delete(config.url + "dm/remove/v1", json={"token": token, "dm_id": invalid_dm_id}).status_code == 400
    assert requests.post(config.url + "dm/leave/v1", json={"token": token, "dm_id": invalid_dm_id}).status_code == 400
    assert requests.get(config.url + "dm/messages/v1", params={"token": token, "dm_id": invalid_dm_id, "start": u_id_two}).status_code == 400

#test if input error is raised if u_id does not refer to a valid user
def test_invalid_user(dm_fixture):
    token = dm_fixture[0]
    u_id = dm_fixture[1]
    u_id_two = dm_fixture[3]
    u_id_three = dm_fixture[5]
    dm_id = dm_fixture[6]

    invalid_u_id = random.randint(0, 10)
    while invalid_u_id == u_id or invalid_u_id == u_id_two or invalid_u_id == u_id_three:
        invalid_u_id = random.randint(0, 10)

    assert requests.post(config.url + "dm/create/v1", json={"token": token, "u_ids": [invalid_u_id]}).status_code == 400
    assert requests.post(config.url + "dm/invite/v1", json={"token": token, "dm_id": dm_id, "u_id": invalid_u_id}).status_code == 400

# raise access error when the Authorised user is not a member of this DM with dm_id
def test_not_member(dm_fixture):
    token_three = dm_fixture[4]
    u_id_two = dm_fixture[3]
    dm_id = dm_fixture[6]

    assert requests.post(config.url + "dm/invite/v1", json={"token": token_three, "dm_id": dm_id, "u_id": u_id_two}).status_code == 403
    assert requests.get(config.url + "dm/details/v1", params={"token": token_three, "dm_id": dm_id}).status_code == 403
    assert requests.post(config.url + "dm/leave/v1", json={"token": token_three, "dm_id": dm_id}).status_code == 403
    assert requests.get(config.url + "dm/messages/v1", params={"token": token_three, "dm_id": dm_id, "start": 0}).status_code == 403
    assert requests.post(config.url + "message/senddm/v1", json={"token": token_three, "dm_id": dm_id, "message": 'hello'}).status_code == 403

#raise access error if invalid token
def test_invalid_token(dm_fixture):
    token = dm_fixture[0]
    u_id_two = dm_fixture[3]
    dm_id = dm_fixture[6]
    
    requests.post(config.url + "auth/logout/v1", json={"token": token})
    
    assert requests.post(config.url + "dm/invite/v1", json={"token": token, "dm_id": dm_id, "u_id": u_id_two}).status_code == 403
    assert requests.get(config.url + "dm/details/v1", params={"token": token, "dm_id": dm_id}).status_code == 403
    assert requests.post(config.url + "dm/leave/v1", json={"token": token, "dm_id": dm_id}).status_code == 403
    assert requests.get(config.url + "dm/messages/v1", params={"token": token, "dm_id": dm_id, "start": 0}).status_code == 403
    assert requests.post(config.url + "message/senddm/v1", json={"token": token, "dm_id": dm_id, "message": 'hello'}).status_code == 403

#raise access error when user is not original dm creator
def test_check_unauthorised_remove(dm_fixture):
    token_two = dm_fixture[2]
    dm_id = dm_fixture[6]
    assert requests.delete(config.url + "dm/remove/v1", json={"token": token_two, "dm_id": dm_id}).status_code == 403

#test if user is correctly invited to dm
def test_dm_invite_v1(dm_fixture): 
    token = dm_fixture[0]
    token_three = dm_fixture[4]
    u_id_three = dm_fixture[5]
    dm_id = dm_fixture[6]

    requests.post(config.url + "dm/invite/v1", json={"token": token, "dm_id": dm_id, "u_id": u_id_three})

    resp = requests.get(config.url + 'dm/list/v1', params={
        'token': token_three
    })
    assert json.loads(resp.text) == {
        'dms': [
            {
                'dm_id': dm_id, 
                'name': ['henrylei', 'randomperson']
            }
        ]
    }

#check if user successfully left dm
def test_dm_leave_v1(dm_fixture): 
    token = dm_fixture[0]
    dm_id = dm_fixture[6]

    requests.post(config.url + "dm/leave/v1", json={"token": token, "dm_id": dm_id})


    resp = requests.get(config.url + 'dm/list/v1', params={
        'token': token
    })
    assert json.loads(resp.text) == {
        'dms': []
    }

#test starting index is outside range of messages
#index starting value is 3 however no messages have been sent
def test_dm_messages_invalid_start(dm_fixture):
    token = dm_fixture[0]
    dm_id = dm_fixture[6]
    assert requests.get(config.url + "dm/messages/v1", params={"token": token, "dm_id": dm_id, "start": 3}).status_code == 400

#raises input error if message is over 1000 characters
def test_dm_message_too_long(dm_fixture):
    token = dm_fixture[0]
    dm_id = dm_fixture[6]
    assert requests.post(config.url + "message/senddm/v1", json={"token": token, "dm_id": dm_id, "message": "A while back I needed to count the amount of letters that a piece of text in an email template had (to avoid passing any character limits). Unfortunately, I could not think of a quick way to do so on my macbook and I therefore turned to the Internet. There were a couple of tools out there, but none of them met my standards and since I am a web designer I thought: why not do it myself and help others along the way? And... here is the result, hope it helA while back I needed to count the amount of letters that a piece of text in an email template had (to avoid passing any character limits). Unfortunately, I could not think of a quick way to do so on my macbook and I therefore turned to the Internet.There were a couple of tools out there, but none of them met my standards and since I am a web designer I thought: why not do it myself and help others along the way? A while back I needed to count the amount of letters that a piece of text in an email template had (to avoid passing any charact"}).status_code == 400

#sends a dm message and tests that it is listed properly
def test_dm_messages_v1(dm_fixture): 
    token = dm_fixture[0]
    u_id = dm_fixture[1]
    dm_id = dm_fixture[6]
    timestamp = int(time.time())
    message_id = requests.post(config.url + "message/senddm/v1", json={"token": token, "dm_id": dm_id, "message": 'hello'}).json()['message_id']

    resp = requests.get(config.url + 'dm/messages/v1', params={
        'token': token,
        'dm_id': dm_id,
        'start': 0
    })
    assert json.loads(resp.text) == {
        'messages': [
            {
                'is_pinned': False,
                'message_id': message_id,
                'u_id': u_id,
                'message': 'hello',
                'reacts': [],
                'time_created': timestamp
            }
        ],
        'start': 0,
        'end': -1
    }



