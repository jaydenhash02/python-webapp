import sys
import pytest
from json import dumps
from flask import Flask, request, send_from_directory
from flask_mail import Mail, Message
from flask_cors import CORS
from src import config
from src.error import InputError
from src.auth import auth_login_v2, auth_register_v2, auth_logout_v1, auth_passwordreset_request_v1, auth_passwordreset_reset_v1
from src.channel import channel_invite_v2, channel_details_v2, channel_messages_v2, channel_leave_v1, channel_join_v2, channel_addowner_v1, channel_removeowner_v1
from src.channels import channels_create_v2, channels_list_v2, channels_listall_v2
from src.message import message_send_v2, message_edit_v2, message_remove_v1, message_share_v1, message_sendlater_v1, message_react_v1, message_unreact_v1, message_pin_v1, message_unpin_v1
from src.dm import dm_details_v1, dm_list_v1, dm_create_v1, dm_remove_v1, dm_invite_v1, dm_leave_v1, dm_messages_v1, message_senddm_v1
from src.user import user_profile_sethandle_v1, user_profile_setemail_v2, user_profile_setname_v2, user_profile_v2, user_all_v1, user_stats_v1, users_stats_v1, user_profile_uploadphoto_v1
from src.other import search_v1, admin_user_permission_change_v1, admin_user_remove_v1, notifications_get_v1, clear_v1
from src.standup import standup_start_v1, standup_send_v1, standup_active_v1

@pytest.fixture 
def auth_fixture(): # pragma: no cover
    clear_v1()

#registers 3 users and creates a channel
@pytest.fixture
def channel_fixture(): # pragma: no cover
    clear_v1()
    val = auth_register_v2('henrylei@gmail.com', 'abcdefg', 'henry', 'lei')
    token = val['token']
    u_id = val['auth_user_id']
    val_two = auth_register_v2('second@gmail.com', 'abcdefg', 'random', 'person')
    token_two = val_two['token']
    u_id_two = val_two['auth_user_id']
    val_three = auth_register_v2('third@gmail.com', 'abcdefg', 'random', 'person')
    token_three = val_three['token']
    u_id_three = val_three['auth_user_id']
    c_id = channels_create_v2(token, 'My Channel', True)['channel_id']
    return token, u_id, token_two, u_id_two, token_three, u_id_three, c_id

#registers 4 users 
@pytest.fixture
def channels_fixture(): # pragma: no cover
    clear_v1()
    val_one = auth_register_v2('henrylei@gmail.com', 'abcdefg', 'henry', 'lei')
    token_one = val_one['token']

    val_two = auth_register_v2('second@gmail.com', 'abcdefg', 'random', 'person')
    token_two = val_two['token']

    val_three = auth_register_v2('third@gmail.com', 'abcdefg', 'random', 'person')
    token_three = val_three['token']

    val_four = auth_register_v2('fourth@gmail.com', 'abcdefg', 'fourth', 'person')
    token_four = val_four['token']

    return token_one, token_two, token_three, token_four

@pytest.fixture
def dm_fixture(): # pragma: no cover
    clear_v1()
    val = auth_register_v2('henrylei@gmail.com', 'abcdefg', 'henry', 'lei')
    token = val['token']
    u_id = val['auth_user_id']
    val_two = auth_register_v2('second@gmail.com', 'abcdefg', 'random', 'person')
    token_two = val_two['token']
    u_id_two = val_two['auth_user_id']
    val_three = auth_register_v2('third@gmail.com', 'abcdefg',   'random', 'person')
    token_three = val_three['token']
    u_id_three = val_three['auth_user_id']
    dm_id = dm_create_v1(token, [u_id_two])['dm_id'] 
    return token, u_id, token_two, u_id_two, token_three, u_id_three, dm_id

@pytest.fixture
def message_fixture(): # pragma: no cover
    clear_v1()
    val = auth_register_v2('henrylei@gmail.com', 'abcdefg', 'henry', 'lei')
    token = val['token']
    u_id = val['auth_user_id']
    val_two = auth_register_v2('second@gmail.com', 'abcdefg', 'random', 'person')
    token_two = val_two['token']
    u_id_two = val_two['auth_user_id']
    c_id = channels_create_v2(token, 'My Channel', True)['channel_id']
    c_id_two = channels_create_v2(token, "My Second Channel", True)['channel_id']
    dm_id = dm_create_v1(token, [u_id_two])['dm_id'] 
    return token, c_id, token_two, c_id_two, u_id, u_id_two, dm_id

@pytest.fixture
def other_fixture(): # pragma: no cover
    clear_v1()
    token = auth_register_v2('henrylei@gmail.com', 'abcdefg', 'henry', 'lei')
    token_two = auth_register_v2('jaydenxian@gmail.com', 'abcdefg', 'jayden', 'xian')
    token_three = auth_register_v2('oliverxu@gmail.com', 'abcdefg', 'oliver', 'xu')
    return token, token_two, token_three

@pytest.fixture
def user_fixture(): # pragma: no cover
    clear_v1()
    val = auth_register_v2('henrylei@gmail.com', 'abcdefg', 'henry', 'lei')
    val_two = auth_register_v2('jimmywang@gmail.com', 'abcdefg', 'jimmy', 'wang')
    return {'val': val, 'val_two': val_two}

#registers 3 users and creates a channel
@pytest.fixture
def standup_fixture(): # pragma: no cover
    clear_v1()
    val = auth_register_v2('henrylei@gmail.com', 'abcdefg', 'henry', 'lei')
    token = val['token']
    u_id = val['auth_user_id']
    val_two = auth_register_v2('second@gmail.com', 'abcdefg', 'random', 'person')
    token_two = val_two['token']
    u_id_two = val_two['auth_user_id']
    val_three = auth_register_v2('third@gmail.com', 'abcdefg', 'random', 'person')
    token_three = val_three['token']
    u_id_three = val_three['auth_user_id']
    c_id = channels_create_v2(token, 'My Channel', True)['channel_id']
    return token, u_id, token_two, u_id_two, token_three, u_id_three, c_id