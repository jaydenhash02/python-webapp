import pytest
import random
from datetime import datetime, timedelta, timezone
import time
from src.auth import auth_login_v2, auth_register_v2, auth_logout_v1
from src.channel import channel_invite_v2, channel_details_v2, channel_messages_v2, channel_join_v2, channel_addowner_v1, channel_removeowner_v1, channel_leave_v1
from src.channels import channels_list_v2, channels_listall_v2, channels_create_v2
from src.message import message_send_v2
from src.other import clear_v1
from src.error import InputError, AccessError
from src.standup import standup_start_v1, standup_send_v1, standup_active_v1
from src.fixture import standup_fixture
import time

''' 
standup is an X minute period where users can send messages that at the end of the period will
automatically be collated and summarised to all users
'''

def test_invalid_channel_id(standup_fixture):
    token = standup_fixture[0]
    c_id = standup_fixture[6]

    invalid_c_id = random.randint(0, 10)
    while invalid_c_id == c_id:
        invalid_c_id = random.randint(0, 10)

    with pytest.raises(InputError):
        standup_start_v1(token, invalid_c_id, 30)
    with pytest.raises(InputError):
        standup_active_v1(token, invalid_c_id)
    with pytest.raises(InputError):
        standup_send_v1(token, invalid_c_id, 'hello')

def test_already_active_standup(standup_fixture):
    token = standup_fixture[0]
    c_id = standup_fixture[6]

    standup_start_v1(token, c_id, 1)
    with pytest.raises(InputError):
        standup_start_v1(token, c_id, 1)
    time.sleep(1)
    
def test_not_active_standup(standup_fixture):
    token = standup_fixture[0]
    c_id = standup_fixture[6]

    with pytest.raises(InputError):
        standup_send_v1(token, c_id, 'hello')

def test_message_length(standup_fixture):
    token = standup_fixture[0]
    c_id = standup_fixture[6]

    standup_start_v1(token, c_id, 1)
    with pytest.raises(InputError):
        standup_send_v1(token, c_id, "character" * 300)
    time.sleep(1)

def test_unauthorised_user(standup_fixture):
    token = standup_fixture[0]
    c_id = standup_fixture[6]
    token_two = standup_fixture[2]

    with pytest.raises(AccessError):
        standup_start_v1(token_two, c_id, 10)
    
    standup_start_v1(token, c_id, 1)
    with pytest.raises(AccessError):
        standup_send_v1(token_two, c_id, "hello")
    time.sleep(1)

#tests if access error is raised with invalid token in standup_start_v1
def test_invalid_token_standup_start_v1(standup_fixture):
    c_id = standup_fixture[6]
    token = standup_fixture[0]
    length = 1
    auth_logout_v1(token)
    with pytest.raises(AccessError):
        standup_start_v1(token, c_id, length)

#tests if access error is raised with invalid token in startup_send_v1
def test_invalid_token_standup_send_v1(standup_fixture):
    c_id = standup_fixture[6]
    token = standup_fixture[0]
    length = 1
    message = "I love Jimmy Wang"
    standup_start_v1(token, c_id, length)
    auth_logout_v1(token)
    with pytest.raises(AccessError):
        standup_send_v1(token, c_id, message)
    time.sleep(length)

#tests if access error is raised with invalid token in startup_active_v1
def test_invalid_token_standup_active_v1(standup_fixture):
    c_id = standup_fixture[6]
    token = standup_fixture[0]
    length = 1
    standup_start_v1(token, c_id, length)
    auth_logout_v1(token)
    with pytest.raises(AccessError):
        standup_active_v1(token, c_id)   
    time.sleep(length)

def test_standup_inactive_no_standup_started(standup_fixture):
    token = standup_fixture[0]
    c_id = standup_fixture[6]
    output = {
        'is_active': False,
        'time_finish': None,
    }
    assert standup_active_v1(token, c_id) == output

def test_standup_active_standup_started(standup_fixture):
    token1 = standup_fixture[0]
    c_id = standup_fixture[6]
    length = 5
    time_finish = standup_start_v1(token1, c_id, length)['time_finish']
    output = {
        'is_active': True,
        'time_finish': time_finish,
    }
    assert standup_active_v1(token1, c_id) == output
    time.sleep(length)

def test_standup_start_functional(standup_fixture): 
    token = standup_fixture[0]
    c_id = standup_fixture[6]
    length = 1
    time_finish = (datetime.now() + timedelta(seconds=length)).strftime("%H:%M:%S")
    output = {'time_finish': time_finish}
    assert standup_start_v1(token, c_id, length) == output
    time.sleep(length)

def test_standup_send_functional(standup_fixture):
    token = standup_fixture[0]
    length = 1
    c_id = standup_fixture[6]
    standup_start_v1(token, c_id, length)
    standup_send_v1(token, c_id, "Let's begin this standup")
    standup_send_v1(token, c_id, "It has begun")
    time.sleep(length)
    assert channel_messages_v2(token, c_id, 0)['messages'][0]['message'] == 'henrylei' + ': ' + "Let's begin this standup" + '\n' + 'henrylei' + ': ' + "It has begun" + '\n'

def test_standup_send_after_standup_is_over(standup_fixture):
    token = standup_fixture[0]
    length = 1
    c_id = standup_fixture[6]
    standup_start_v1(token, c_id, length)
    time.sleep(length)
    with pytest.raises(InputError):
        standup_send_v1(token, c_id, 'hello people')

def test_standup_send_functional_message_send(standup_fixture):
    token = standup_fixture[0]
    length = 1
    c_id = standup_fixture[6]
    standup_start_v1(token, c_id, length)
    message_send_v2(token, c_id, "Let's begin this standup")
    message_send_v2(token, c_id, "It has begun")
    time.sleep(length)
    assert channel_messages_v2(token, c_id, 0)['messages'][0]['message'] == 'henrylei' + ': ' + "Let's begin this standup" + '\n' + 'henrylei' + ': ' + "It has begun" + '\n'