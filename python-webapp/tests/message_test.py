import pytest
import random
from src.auth import auth_login_v2, auth_register_v2, auth_logout_v1
from src.channel import channel_invite_v2, channel_details_v2, channel_messages_v2, channel_join_v2
from src.channels import channels_list_v2, channels_listall_v2, channels_create_v2
from src.message import message_send_v2,message_edit_v2,message_remove_v1,message_share_v1,message_sendlater_v1,message_react_v1,message_unreact_v1,message_pin_v1,message_unpin_v1
from src.dm import dm_create_v1, dm_messages_v1, message_senddm_v1
from src.other import clear_v1
from src.error import InputError, AccessError
from src.fixture import message_fixture
import time

#testing unique message id in same channel
def test_message_send_unique(message_fixture):
    token = message_fixture[0]
    c_id = message_fixture[1]
    assert message_send_v2(token, c_id, "hello") != message_send_v2(token, c_id, "goodbye")

#testing unique message id in different channel
def test_message_send_two(message_fixture):
    token = message_fixture[0]
    c_id = message_fixture[1]
    c_id_two = message_fixture[3]

    assert message_send_v2(token, c_id, "hello") != message_send_v2(token, c_id_two, "hello")

#testing unauthorised user
def test_invalid_messager(message_fixture):
    token_two = message_fixture[2]
    c_id = message_fixture[1]

    with pytest.raises(AccessError):
        message_send_v2(token_two, c_id, "hello")

#testing invalid message send length
def test_invalid_message_send_length(message_fixture):
    token = message_fixture[0]
    c_id = message_fixture[1]

    with pytest.raises(InputError):
        message_send_v2(token, c_id, "A while back I needed to count the amount of letters that a piece of text in an email template had (to avoid passing any character limits). Unfortunately, I could not think of a quick way to do so on my macbook and I therefore turned to the Internet. There were a couple of tools out there, but none of them met my standards and since I am a web designer I thought: why not do it myself and help others along the way? And... here is the result, hope it helA while back I needed to count the amount of letters that a piece of text in an email template had (to avoid passing any character limits). Unfortunately, I could not think of a quick way to do so on my macbook and I therefore turned to the Internet.There were a couple of tools out there, but none of them met my standards and since I am a web designer I thought: why not do it myself and help others along the way? A while back I needed to count the amount of letters that a piece of text in an email template had (to avoid passing any charact")    

#testing invalid message length for edit
def test_invalid_message_edit_length(message_fixture):
    token = message_fixture[0]
    c_id = message_fixture[1]

    m_id = message_send_v2(token, c_id, "hello")['message_id']
    with pytest.raises(InputError):
        message_edit_v2(token, m_id, "A while back I needed to count the amount of letters that a piece of text in an email template had (to avoid passing any character limits). Unfortunately, I could not think of a quick way to do so on my macbook and I therefore turned to the Internet. There were a couple of tools out there, but none of them met my standards and since I am a web designer I thought: why not do it myself and help others along the way? And... here is the result, hope it helA while back I needed to count the amount of letters that a piece of text in an email template had (to avoid passing any character limits). Unfortunately, I could not think of a quick way to do so on my macbook and I therefore turned to the Internet.There were a couple of tools out there, but none of them met my standards and since I am a web designer I thought: why not do it myself and help others along the way? A while back I needed to count the amount of letters that a piece of text in an email template had (to avoid passing any charact")    

#checking if editor is authorised
def test_check_message_editor(message_fixture):
    token = message_fixture[0]
    c_id = message_fixture[1]
    token_two = message_fixture[2]

    m_id = message_send_v2(token, c_id, "hello")['message_id']
    with pytest.raises(AccessError):
        message_edit_v2(token_two, m_id, 'not authorised')

#checking if remove works and raise error when removing non-existent message
def test_check_remove_message(message_fixture):
    token = message_fixture[0]
    c_id = message_fixture[1]

    m_id = message_send_v2(token, c_id, "hello")['message_id']
    message_remove_v1(token, m_id)
    with pytest.raises(InputError):
        message_remove_v1(token, m_id)

#raise error when unauthorised user attempts to remove message
def test_check_unauthorised_remove(message_fixture):
    token = message_fixture[0]
    c_id = message_fixture[1]
    token_two = message_fixture[2]

    m_id = message_send_v2(token, c_id, "hello")['message_id']
    with pytest.raises(AccessError):
        message_remove_v1(token_two, m_id)

#check if owner of channel can remove message
def test_owner_remove_message(message_fixture):
    token = message_fixture[0]
    c_id = message_fixture[1]
    token_two = message_fixture[2]

    channel_join_v2(token_two, c_id)
    m_id = message_send_v2(token_two, c_id, "hello")['message_id']
    message_remove_v1(token, m_id)
    with pytest.raises(InputError):
        message_edit_v2(token, m_id, "no such message")

#check if the message id is unique
def test_unique_share_message_id(message_fixture):
    token = message_fixture[0]
    c_id = message_fixture[1]
    c_id_two = message_fixture[3]
    u_id = message_fixture[4]

    m_id = message_send_v2(token, c_id, "hello")['message_id']
    shared_m_id = message_share_v1(token, m_id, "", c_id_two, -1)['shared_message_id']
    timestamp = int(time.time())
    assert shared_m_id != m_id
    assert channel_messages_v2(token, c_id_two, 0) == {
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

    m_id = message_send_v2(token, c_id, "hello")['message_id']
    with pytest.raises(AccessError):
        message_share_v1(token_two, m_id, "", c_id_two, -1)

#test if message send works
def test_message_send(message_fixture):
    token = message_fixture[0]
    c_id = message_fixture[1]
    u_id = message_fixture[4]

    m_id = message_send_v2(token, c_id, "hello")['message_id']
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

#test if message send works
def test_message_edit(message_fixture):
    token = message_fixture[0]
    c_id = message_fixture[1]
    u_id = message_fixture[4]

    m_id = message_send_v2(token, c_id, "hello")['message_id']
    timestamp = int(time.time())
    message_edit_v2(token, m_id, 'goodbye')
    assert channel_messages_v2(token, c_id, 0) == {
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

    m_id = message_send_v2(token, c_id, "hello")['message_id']
    message_remove_v1(token, m_id)
    assert channel_messages_v2(token, c_id, 0) == {
        'messages': [],
        'start': 0,
        'end': -1,
    }

#test if message edit with no comment deletes it works
def test_message_edit_delete(message_fixture):
    token = message_fixture[0]
    c_id = message_fixture[1]

    m_id = message_send_v2(token, c_id, "hello")['message_id']
    message_edit_v2(token, m_id, '')
    assert channel_messages_v2(token, c_id, 0) == {
        'messages': [],
        'start': 0,
        'end': -1,
    }

#test if message is sent 5 secs before raises InputError
def test_message_send_later_error(message_fixture):
    token = message_fixture[0]
    c_id = message_fixture[1]

    future_timestamp = int(time.time()) - 5 
    with pytest.raises(InputError):
        message_sendlater_v1(token, c_id, 'hello', future_timestamp)

#test if message is sent 5 secs later then deletes msg
def test_message_send_later(message_fixture):
    token = message_fixture[0]
    c_id = message_fixture[1]
    u_id = message_fixture[4]

    future_timestamp = int(time.time()) + 5
    m_id = message_sendlater_v1(token, c_id, 'hello', future_timestamp)['message_id']
    assert channel_messages_v2(token, c_id, 0) == {
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

#test if reacting and unreacting to message works then deletes msg
def test_message_react(message_fixture):
    token = message_fixture[0]
    token_two = message_fixture[2]
    c_id = message_fixture[1]
    u_id = message_fixture[4]
    u_id_two = message_fixture[5]

    m_id = message_send_v2(token, c_id, "hello")['message_id']
    timestamp = int(time.time())
    channel_invite_v2(token, c_id, u_id_two)
    message_react_v1(token, m_id, 1)
    message_react_v1(token_two, m_id, 1)
    assert channel_messages_v2(token, c_id, 0) == {
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

    message_unreact_v1(token_two, m_id, 1)
    assert channel_messages_v2(token, c_id, 0) == {
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
                    } 
                ],
                'is_pinned': False
            }
        ],
        'start': 0,
        'end': -1,
    }
    message_remove_v1(token, m_id)

#tests if reacting and unreacting to dm works then deletes msg
def test_message_react_dm(message_fixture): 
    token = message_fixture[0]
    u_id = message_fixture[1]
    token_two = message_fixture[2]
    u_id_two = message_fixture[5]
    dm_id = message_fixture[6]

    timestamp = int(time.time())
    m_id = message_senddm_v1(token, dm_id, 'hello')['message_id']
    message_react_v1(token, m_id, 1)
    message_react_v1(token_two, m_id, 1)

    assert dm_messages_v1(token, dm_id, 0) == {
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
                    }
                ],
                'is_pinned': False
            }
        ],
        'start': 0,
        'end': -1
    }

    message_unreact_v1(token_two, m_id, 1)
    assert dm_messages_v1(token, dm_id, 0) == {
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
                    } 
                ],
                'is_pinned': False
            }
        ],
        'start': 0,
        'end': -1,
    }
    message_remove_v1(token, m_id)

#tests if pinning and unpinning a message works
def test_message_pin(message_fixture):
    token = message_fixture[0]
    c_id = message_fixture[1]
    u_id = message_fixture[4]

    m_id = message_send_v2(token, c_id, "hello")['message_id']
    timestamp = int(time.time())
    message_pin_v1(token, m_id)
    assert channel_messages_v2(token, c_id, 0) == {
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

    message_unpin_v1(token, m_id)
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
    message_remove_v1(token, m_id)

#tests if pinning and unpinning a dm works
def test_message_pin_dm(message_fixture):
    token = message_fixture[0]
    u_id = message_fixture[4]
    dm_id = message_fixture[6]

    m_id = message_senddm_v1(token, dm_id, "hello")['message_id']
    timestamp = int(time.time())
    message_pin_v1(token, m_id)
    assert dm_messages_v1(token, dm_id, 0) == {
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

    message_unpin_v1(token, m_id)
    assert dm_messages_v1(token, dm_id, 0) == {
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

def test_invalid_token(message_fixture):
    token = message_fixture[2]
    c_id = message_fixture[1]
    channel_join_v2(token, c_id)
    m_id = message_send_v2(token, c_id, "hello")['message_id']
    c_id_two = message_fixture[3]
    channel_join_v2(token, c_id_two)
    auth_logout_v1(token)

    with pytest.raises(AccessError):
        message_send_v2(token, c_id, "hello")
    with pytest.raises(AccessError):
        message_edit_v2(token, m_id, "A while")
    with pytest.raises(AccessError):
        message_remove_v1(token, m_id)
    with pytest.raises(AccessError):
        message_share_v1(token, m_id, "", c_id_two, -1)


