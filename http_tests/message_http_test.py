import pytest
import requests
import json
import time, sched
from src import config
from src.auth import auth_login_v2, auth_register_v2
from src.channel import channel_invite_v2, channel_details_v2, channel_messages_v2, channel_join_v2
from src.channels import channels_list_v2, channels_listall_v2, channels_create_v2
from src.message import message_send_v2,message_edit_v2,message_remove_v1,message_share_v1
from src.dm import dm_create_v1, dm_messages_v1, message_senddm_v1
from src.other import clear_v1
from src.error import InputError, AccessError
from src.http_fixture import message_fixture

#testing unauthorised user
def test_invalid_messager(message_fixture):
    token_two = message_fixture[2]
    c_id = message_fixture[1]

    assert requests.post(config.url + 'message/send/v2', json={'token': token_two, 'channel_id': c_id, 'message': "hello"}).status_code == 403
    

#testing invalid message send length
def test_invalid_message_send_length(message_fixture):
    token = message_fixture[0]
    c_id = message_fixture[1]

    assert requests.post(config.url + 'message/send/v2', json={'token': token, 'channel_id': c_id, 'message': "A while back I needed to count the amount of letters that a piece of text in an email template had (to avoid passing any character limits). Unfortunately, I could not think of a quick way to do so on my macbook and I therefore turned to the Internet. There were a couple of tools out there, but none of them met my standards and since I am a web designer I thought: why not do it myself and help others along the way? And... here is the result, hope it helA while back I needed to count the amount of letters that a piece of text in an email template had (to avoid passing any character limits). Unfortunately, I could not think of a quick way to do so on my macbook and I therefore turned to the Internet.There were a couple of tools out there, but none of them met my standards and since I am a web designer I thought: why not do it myself and help others along the way? A while back I needed to count the amount of letters that a piece of text in an email template had (to avoid passing any charact"}).status_code == 400
  

#testing invalid message length for edit
def test_invalid_message_edit_length(message_fixture):
    token = message_fixture[0]
    c_id = message_fixture[1]

    m_id = requests.post(config.url + 'message/send/v2', json={'token': token, 'channel_id': c_id, 'message': "hello"}).json()["message_id"]

    assert requests.put(config.url + 'message/edit/v2', json={'token': token, 'message_id': m_id, 'message': "A while back I needed to count the amount of letters that a piece of text in an email template had (to avoid passing any character limits). Unfortunately, I could not think of a quick way to do so on my macbook and I therefore turned to the Internet. There were a couple of tools out there, but none of them met my standards and since I am a web designer I thought: why not do it myself and help others along the way? And... here is the result, hope it helA while back I needed to count the amount of letters that a piece of text in an email template had (to avoid passing any character limits). Unfortunately, I could not think of a quick way to do so on my macbook and I therefore turned to the Internet.There were a couple of tools out there, but none of them met my standards and since I am a web designer I thought: why not do it myself and help others along the way? A while back I needed to count the amount of letters that a piece of text in an email template had (to avoid passing any charact"}).status_code == 400
      

#checking if editor is authorised
def test_check_message_editor(message_fixture):
    token = message_fixture[0]
    c_id = message_fixture[1]
    token_two = message_fixture[2]

    m_id = requests.post(config.url + 'message/send/v2', json={'token': token, 'channel_id': c_id, 'message': "hello"}).json()["message_id"]
    assert requests.put(config.url + 'message/edit/v2', json={'token': token_two, 'message_id': m_id,'message': 'not authorised'}).status_code == 403


#checking if remove works and raise error when removing non-existent message
def test_check_remove_message(message_fixture):
    token = message_fixture[0]
    c_id = message_fixture[1]

    m_id = requests.post(config.url + 'message/send/v2', json={'token': token, 'channel_id': c_id, 'message': "hello"}).json()["message_id"]
    requests.delete(config.url + 'message/remove/v1', json={'token': token, 'message_id': m_id})
    
    assert requests.delete(config.url + 'message/remove/v1', json={'token': token, 'message_id': m_id}).status_code == 400

#raise error when unauthorised user attempts to remove message
def test_check_unauthorised_remove(message_fixture):
    token = message_fixture[0]
    c_id = message_fixture[1]
    token_two = message_fixture[2]

    m_id = requests.post(config.url + 'message/send/v2', json={'token': token, 'channel_id': c_id, 'message': "hello"}).json()["message_id"]

    assert requests.delete(config.url + 'message/remove/v1', json={'token': token_two, 'message_id': m_id}).status_code == 403


#check if owner of channel can remove message
def test_owner_remove_message(message_fixture):
    token = message_fixture[0]
    c_id = message_fixture[1]
    token_two = message_fixture[2]

    requests.post(config.url + 'channel/join/v2', json={'token': token_two, "channel_id": c_id})
    
    m_id = requests.post(config.url + 'message/send/v2', json={'token': token_two, 'channel_id': c_id, 'message': "hello"}).json()["message_id"]
    requests.delete(config.url + 'message/remove/v1', json={'token': token, 'message_id': m_id})

    assert requests.delete(config.url + 'message/remove/v1', json={'token': token, 'message_id': m_id}).status_code == 400

#check if the message id is unique
def test_unique_share_message_id(message_fixture):
    token = message_fixture[0]
    c_id = message_fixture[1]
    c_id_two = message_fixture[3]
    u_id = message_fixture[4]

    m_id = requests.post(config.url + 'message/send/v2', json={'token': token, 'channel_id': c_id, 'message': "hello"}).json()["message_id"]
    shared_m_id = requests.post(config.url + 'message/share/v1', json={'token': token, 'og_message_id': m_id, "message": "", 'channel_id': c_id_two, "dm_id": -1}).json()["shared_message_id"]
    timestamp = int(time.time())
    assert requests.get(config.url + 'channel/messages/v2', params={'token': token, 'channel_id': c_id_two, 'start': 0}).json() == {
        'messages': [
            {
                'message_id': shared_m_id,
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


#testing share with unauthorised user
def test_unauthorised_share(message_fixture):
    token = message_fixture[0]
    c_id = message_fixture[1]
    token_two = message_fixture[2]
    c_id_two = message_fixture[3]

    m_id = requests.post(config.url + 'message/send/v2', json={'token': token, 'channel_id': c_id, 'message': "hello"}).json()["message_id"]
    assert requests.post(config.url + 'message/share/v1', json={'token': token_two, 'og_message_id': m_id, "message": "", 'channel_id': c_id_two, "dm_id": -1}).status_code == 403

#test if message send works
def test_message_send(message_fixture):
    token = message_fixture[0]
    c_id = message_fixture[1]
    u_id = message_fixture[4]

    m_id = requests.post(config.url + 'message/send/v2', json={'token': token, 'channel_id': c_id, 'message': "hello"}).json()["message_id"]
    timestamp = int(time.time())
    assert requests.get(config.url + 'channel/messages/v2', params={'token': token, 'channel_id': c_id, 'start': 0}).json() == {
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

#test if message edit works
def test_message_edit(message_fixture):
    token = message_fixture[0]
    c_id = message_fixture[1]
    u_id = message_fixture[4]


    m_id = requests.post(config.url + 'message/send/v2', json={'token': token, 'channel_id': c_id, 'message': "hello"}).json()["message_id"]
    timestamp = int(time.time())
    requests.put(config.url + 'message/edit/v2', json={'token': token, 'message_id': m_id,'message': 'goodbye'})
    
    assert requests.get(config.url + 'channel/messages/v2', params={'token': token, 'channel_id': c_id, 'start': 0}).json() == {
        'messages': [
            {
                'message_id': m_id,
                'u_id': u_id,
                'message': 'goodbye',
                'time_created': timestamp,
                'reacts': [],
                'is_pinned': False
            }
        ],
        'start': 0,
        'end': -1,
    }

#test if message delete works
def test_message_delete(message_fixture):
    token = message_fixture[0]
    c_id = message_fixture[1]

    m_id = requests.post(config.url + 'message/send/v2', json={'token': token, 'channel_id': c_id, 'message': "hello"}).json()["message_id"]
    requests.delete(config.url + 'message/remove/v1', json={'token': token, 'message_id': m_id})
    
    assert requests.get(config.url + 'channel/messages/v2', params={'token': token, 'channel_id': c_id, 'start': 0}).json() == {
        'messages': [],
        'start': 0,
        'end': -1,
    }

#test if message edit with no comment deletes it works
def test_message_edit_delete(message_fixture):
    token = message_fixture[0]
    c_id = message_fixture[1]

    m_id = requests.post(config.url + 'message/send/v2', json={'token': token, 'channel_id': c_id, 'message': "hello"}).json()["message_id"]
    requests.put(config.url + 'message/edit/v2', json={'token': token, 'message_id': m_id,'message': ''})
    assert requests.get(config.url + 'channel/messages/v2', params={'token': token, 'channel_id': c_id, 'start': 0}).json() == {
        'messages': [],
        'start': 0,
        'end': -1,
    }

#test if message is sent 5 secs before raise InputError
def test_message_send_later_error(message_fixture):
    token = message_fixture[0]
    c_id = message_fixture[1]
    future_timestamp = int(time.time()) - 5 
    assert requests.post(config.url + 'message/sendlater/v1', json={'token': token, 'channel_id': c_id, 'message': "hello", 'time_sent': future_timestamp}).status_code == 400

#test if message is sent 5 secs later than deletes msg
def test_message_send_later(message_fixture):
    token = message_fixture[0]
    c_id = message_fixture[1]
    u_id = message_fixture[4]

    future_timestamp = int(time.time()) + 5
    m_id = requests.post(config.url + 'message/sendlater/v1', json={'token': token, 'channel_id': c_id, 'message': "hello", 'time_sent': future_timestamp}).json()['message_id']
    assert requests.get(config.url + 'channel/messages/v2', params={'token': token, 'channel_id': c_id, 'start': 0}).json() == {
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
    requests.delete(config.url + 'message/remove/v1', json={'token': token, 'message_id': m_id})

#test if reacting and unreacting to message works then deletes msg
def test_message_react(message_fixture):
    token = message_fixture[0]
    token_two = message_fixture[2]
    c_id = message_fixture[1]
    u_id = message_fixture[4]
    u_id_two = message_fixture[5]

    m_id = requests.post(config.url + 'message/send/v2', json={'token': token, 'channel_id': c_id, 'message': "hello"}).json()["message_id"]
    timestamp = int(time.time())
    requests.post(config.url + 'channel/invite/v2', json={'token': token, 'channel_id': c_id, 'u_id': u_id_two})
    requests.post(config.url + 'message/react/v1', json={'token': token, 'message_id': m_id, 'react_id': 1})
    requests.post(config.url + 'message/react/v1', json={'token': token_two, 'message_id': m_id, 'react_id': 1})
    assert requests.get(config.url + 'channel/messages/v2', params={'token': token, 'channel_id': c_id, 'start': 0}).json() == {      
        'messages': [
            {
                'message_id': m_id,
                'u_id': u_id,
                'message': 'hello',
                'time_created': timestamp,
                'reacts': [
                    {
                        'react_id': 1,
                        'u_ids': [u_id, u_id_two],
                        'is_this_user_reacted': True
                    },
                ],
                'is_pinned': False
            }
        ],
        'start': 0,
        'end': -1,
    }
    requests.post(config.url + 'message/unreact/v1', json={'token': token_two, 'message_id': m_id, 'react_id': 1})
    assert requests.get(config.url + 'channel/messages/v2', params={'token': token, 'channel_id': c_id, 'start': 0}).json() == {      
        'messages': [
            {
                'message_id': m_id,
                'u_id': u_id,
                'message': 'hello',
                'time_created': timestamp,
                'reacts': [
                    {
                        'react_id': 1,
                        'u_ids': [u_id],
                        'is_this_user_reacted': True
                    },
                ],
                'is_pinned': False
            }
        ],
        'start': 0,
        'end': -1,
    }
    requests.delete(config.url + 'message/remove/v1', json={'token': token, 'message_id': m_id})

#test if reacting and unreacting to dm works then deletes msg
def test_message_react_dm(message_fixture):
    token = message_fixture[0]
    token_two = message_fixture[2]
    u_id = message_fixture[4]
    u_id_two = message_fixture[5]
    dm_id = message_fixture[6]

    timestamp = int(time.time())
    m_id = requests.post(config.url + 'message/senddm/v1', json={'token': token, 'dm_id': dm_id, 'message': "hello"}).json()["message_id"]
    requests.post(config.url + 'message/react/v1', json={'token': token, 'message_id': m_id, 'react_id': 1})
    requests.post(config.url + 'message/react/v1', json={'token': token_two, 'message_id': m_id, 'react_id': 1})
    assert requests.get(config.url + 'dm/messages/v1', params={'token': token, 'dm_id': dm_id, 'start': 0}).json() == {      
        'messages': [
            {
                'message_id': m_id,
                'u_id': u_id,
                'message': 'hello',
                'time_created': timestamp,
                'reacts': [
                    {
                        'react_id': 1,
                        'u_ids': [u_id, u_id_two],
                        'is_this_user_reacted': True
                    },
                ],
                'is_pinned': False
            }
        ],
        'start': 0,
        'end': -1,
    }
    requests.post(config.url + 'message/unreact/v1', json={'token': token_two, 'message_id': m_id, 'react_id': 1})
    assert requests.get(config.url + 'dm/messages/v1', params={'token': token, 'dm_id': dm_id, 'start': 0}).json() == {      
        'messages': [
            {
                'message_id': m_id,
                'u_id': u_id,
                'message': 'hello',
                'time_created': timestamp,
                'reacts': [
                    {
                        'react_id': 1,
                        'u_ids': [u_id],
                        'is_this_user_reacted': True
                    },
                ],
                'is_pinned': False
            }
        ],
        'start': 0,
        'end': -1,
    }
    requests.delete(config.url + 'message/remove/v1', json={'token': token, 'message_id': m_id})

#test if pinning and unpinning a message works
def test_message_pin(message_fixture):
    token = message_fixture[0]
    c_id = message_fixture[1]
    u_id = message_fixture[4]

    m_id = requests.post(config.url + 'message/send/v2', json={'token': token, 'channel_id': c_id, 'message': "hello"}).json()["message_id"]
    timestamp = int(time.time())
    requests.post(config.url + 'message/pin/v1', json={'token': token, 'message_id': m_id})
    assert requests.get(config.url + 'channel/messages/v2', params={'token': token, 'channel_id': c_id, 'start': 0}).json() == {      
        'messages': [
            {
                'message_id': m_id,
                'u_id': u_id,
                'message': 'hello',
                'time_created': timestamp,
                'reacts': [],
                'is_pinned': True
            }
        ],
        'start': 0,
        'end': -1,
    } 

    requests.post(config.url + 'message/unpin/v1', json={'token': token, 'message_id': m_id})
    assert requests.get(config.url + 'channel/messages/v2', params={'token': token, 'channel_id': c_id, 'start': 0}).json() == {      
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

#test if pinning and unpinning a dm works
def test_message_pin_dm(message_fixture):
    token = message_fixture[0]
    u_id = message_fixture[4]
    dm_id = message_fixture[6]

    timestamp = int(time.time())
    m_id = requests.post(config.url + 'message/senddm/v1', json={'token': token, 'dm_id': dm_id, 'message': "hello"}).json()["message_id"]
    requests.post(config.url + 'message/pin/v1', json={'token': token, 'message_id': m_id})
    assert requests.get(config.url + 'dm/messages/v1', params={'token': token, 'dm_id': dm_id, 'start': 0}).json() == {      
        'messages': [
            {
                'message_id': m_id,
                'u_id': u_id,
                'message': 'hello',
                'time_created': timestamp,
                'reacts': [],
                'is_pinned': True
            }
        ],
        'start': 0,
        'end': -1,
    } 

    requests.post(config.url + 'message/unpin/v1', json={'token': token, 'message_id': m_id})
    assert requests.get(config.url + 'dm/messages/v1', params={'token': token, 'dm_id': dm_id, 'start': 0}).json() == {      
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

#test when token is invalid
def test_invalid_token(message_fixture):
    token = message_fixture[2]
    c_id = message_fixture[1]

    
    requests.post(config.url + 'channel/join/v2', json={'token': token, "channel_id": c_id})
    
    m_id = requests.post(config.url + 'message/send/v2', json={'token': token, 'channel_id': c_id, 'message': "hello"}).json()["message_id"]

    c_id_two = message_fixture[3]
    
    requests.post(config.url + 'channel/join/v2', json={'token': token, "channel_id": c_id_two})
    requests.post(config.url + 'auth/logout/v1', json={'token': token})

    assert requests.post(config.url + 'message/send/v2', json={'token': token, 'channel_id': c_id, 'message': "hello"}).status_code == 403
    assert requests.put(config.url + 'message/edit/v2', json={'token': token, 'message_id': m_id,'message': 'a while'}).status_code == 403 
    assert requests.delete(config.url + 'message/remove/v1', json={'token': token, 'message_id': m_id}).status_code == 403
    assert requests.post(config.url + 'message/share/v1', json={'token': token, 'og_message_id': m_id, "message": "", 'channel_id': c_id_two, "dm_id": -1}).status_code == 403
        

