import pytest
import random
from src import config
from src.auth import auth_login_v2, auth_register_v2, auth_logout_v1
from src.error import InputError, AccessError
from src.user import user_profile_v2, user_profile_setname_v2, user_profile_setemail_v2, user_profile_sethandle_v1, user_all_v1, user_stats_v1, users_stats_v1, user_profile_uploadphoto_v1
from src.channel import channel_invite_v2, channel_details_v2, channel_messages_v2, channel_join_v2, channel_addowner_v1, channel_removeowner_v1, channel_leave_v1
from src.dm import dm_details_v1, dm_list_v1, dm_create_v1, dm_remove_v1, dm_invite_v1, dm_leave_v1, dm_messages_v1, message_senddm_v1
from src.channels import channels_list_v2, channels_listall_v2, channels_create_v2
from src.message import message_send_v2
from src.other import clear_v1
from src.fixture import user_fixture

#test if user profile works
def test_user_profile(user_fixture):
    u_id = user_fixture['val']['auth_user_id']
    token = user_fixture['val']['token']
    output = user_profile_v2(token, u_id)
    assert output == {'user': {
                            'u_id': u_id,
                            'email': 'henrylei@gmail.com',
                            'name_first': 'henry',
                            'name_last': 'lei',
                            'handle_str': 'henrylei',
                            'profile_img_url': f'http://localhost:{config.port}/static/default.jpg'
                        },}

#tests if input error is raised with invalid auth id
def test_invalid_user_id_profile(user_fixture):
    u_id = user_fixture['val']['auth_user_id']
    u_id_two = user_fixture['val_two']['auth_user_id']
    token = user_fixture['val']['token']
    invalid_id = random.randint(0, 10)
    while invalid_id == u_id or invalid_id == u_id_two:
        invalid_id = random.randint(0, 10)

    with pytest.raises(InputError):
        user_profile_v2(token, invalid_id)

#tests if access error is raised with invalid token
def test_invalid_token_profile(user_fixture):
    u_id = user_fixture['val']['auth_user_id']
    token = user_fixture['val']['token']
    auth_logout_v1(token)
    with pytest.raises(AccessError):
        user_profile_v2(token, u_id)

#test if profile setname works
def test_profile_setname(user_fixture):
    u_id = user_fixture['val']['auth_user_id']
    token = user_fixture['val']['token']
    user_profile_setname_v2(token, 'alex', 'loke')
    output = user_profile_v2(token, u_id)
    assert output['user']['name_first'] == 'alex' and output['user']['name_last'] == 'loke'

#test if input error is raised with empty name inputs
def test_profile_setname_empty(user_fixture):
    token = user_fixture['val']['token']
    with pytest.raises(InputError):
        user_profile_setname_v2(token, '', 'loke')
    with pytest.raises(InputError):
        user_profile_setname_v2(token, 'alex', '')

#test if input error is raised if name is longer than fifty characters
def test_profile_setname_long(user_fixture):
    token = user_fixture['val']['token']
    with pytest.raises(InputError):
        user_profile_setname_v2(token, 'thisnameissuperongandhopefullyitismorethanfiftycharacterssoaninputerrorisraised', 'loke')
    with pytest.raises(InputError):
        user_profile_setname_v2(token, 'alex', 'thisnameissuperongandhopefullyitismorethanfiftycharacterssoaninputerrorisraised')

#test if access error is raised with invalid token
def test_invalid_token_setname(user_fixture):
    token = user_fixture['val']['token']
    auth_logout_v1(token)
    with pytest.raises(AccessError):
        user_profile_setname_v2(token, 'alex', 'loke')

#test if profile setemail works
def test_profile_setemail(user_fixture):
    u_id = user_fixture['val']['auth_user_id']
    token = user_fixture['val']['token']
    user_profile_setemail_v2(token, 'alexloke@gmail.com')
    output = user_profile_v2(token, u_id)
    assert output['user']['email'] == 'alexloke@gmail.com'

#test if inputerror is raised if an invalid email is used
def test_profile_invalid_email(user_fixture):
    token = user_fixture['val']['token']
    with pytest.raises(InputError):
        user_profile_setemail_v2(token, 'bued@^&!&*@gma@gmail.com')

#test if inputerror is raised if email is already used
def test_profile_email_already_used(user_fixture):
    token = user_fixture['val']['token']
    with pytest.raises(InputError):
        user_profile_setemail_v2(token, 'jimmywang@gmail.com')

#test if access error is raised with invalid token
def test_invalid_token_setemail(user_fixture):
    token = user_fixture['val']['token']
    auth_logout_v1(token)
    with pytest.raises(AccessError):
        user_profile_setemail_v2(token, 'alexloke@gmail.com')

#test if profile sethandle works
def test_profile_sethandle(user_fixture):
    u_id = user_fixture['val']['auth_user_id']
    token = user_fixture['val']['token']
    user_profile_sethandle_v1(token, 'alexloke')
    output = user_profile_v2(token, u_id)
    assert output['user']['handle_str'] == 'alexloke'

#test if input error is raised if name is longer than twenty characters or less than 3
def test_profile_handle_invalid_length(user_fixture):
    token = user_fixture['val']['token']
    with pytest.raises(InputError):
        user_profile_sethandle_v1(token, 'hi')
    with pytest.raises(InputError):
        user_profile_sethandle_v1(token, 'thishandleiswaylongerthantwentycharacters')

#test if inputerror is raised if handle is already used
def test_profile_setname_handle_already_used(user_fixture):
    token = user_fixture['val']['token']
    with pytest.raises(InputError):
        user_profile_sethandle_v1(token, 'jimmywang')

#test if access error is raised with invalid token
def test_invalid_token_sethandle(user_fixture):
    token = user_fixture['val']['token']
    auth_logout_v1(token)
    with pytest.raises(AccessError):
        user_profile_sethandle_v1(token, 'alexloke')

#test if user all works
def test_user_all(user_fixture):
    token = user_fixture['val']['token']
    u_id = user_fixture['val']['auth_user_id']
    u_id_two = user_fixture['val_two']['auth_user_id']
    output = user_all_v1(token)
    assert output == {'users': [{'u_id': u_id, 'email': 'henrylei@gmail.com', 'name_first': 'henry', 'name_last': 'lei', 'handle_str': 'henrylei', 'profile_img_url': f'http://localhost:{config.port}/static/default.jpg'}, 
                      {'u_id': u_id_two, 'email': 'jimmywang@gmail.com', 'name_first': 'jimmy', 'name_last': 'wang', 'handle_str': 'jimmywang', 'profile_img_url': f'http://localhost:{config.port}/static/default.jpg'}]}

#test if access error is raised with invalid token
def test_invalid_token_all(user_fixture):
    token = user_fixture['val']['token']
    auth_logout_v1(token)
    with pytest.raises(AccessError):
        user_all_v1(token)

def test_user_stats(user_fixture):
    token = user_fixture['val']['token']
    token_two = user_fixture['val_two']['token']
    u_id_two = user_fixture['val_two']['auth_user_id']
    c_id_one = channels_create_v2(token,'My Channel', True)['channel_id']
    c_id_two = channels_create_v2(token_two,'2nd Channel', True)['channel_id']
    message_send_v2(token, c_id_one, "hello")
    message_send_v2(token_two, c_id_two, "hello")
    dm_create_v1(token, [u_id_two])
    assert user_stats_v1(token)['user_stats']['channels_joined'][-1]['num_channels_joined'] == 1
    assert user_stats_v1(token)['user_stats']['dms_joined'][-1]['num_dms_joined'] == 1
    assert user_stats_v1(token)['user_stats']['messages_sent'][-1]['num_messages_sent'] == 1
    assert user_stats_v1(token)['user_stats']['involvement_rate'] == 3/5

def test_users_stats(user_fixture):
    token = user_fixture['val']['token']
    token_two = user_fixture['val_two']['token']
    u_id_two = user_fixture['val_two']['auth_user_id']
    c_id_one = channels_create_v2(token,'My Channel', True)['channel_id']
    c_id_two = channels_create_v2(token_two,'2nd Channel', True)['channel_id']
    message_send_v2(token, c_id_one, "hello")
    message_send_v2(token_two, c_id_two, "hello")
    dm_create_v1(token, [u_id_two])
    assert users_stats_v1(token)['dreams_stats']['channels_exist'][-1]['num_channels_exist'] == 2
    assert users_stats_v1(token)['dreams_stats']['dms_exist'][-1]['num_dms_exist'] == 1
    assert users_stats_v1(token)['dreams_stats']['messages_exist'][-1]['num_messages_exist'] == 2
    assert users_stats_v1(token)['dreams_stats']['utilization_rate'] == 2/2

def test_users_stats_multiple_users(user_fixture):
    token = user_fixture['val']['token']
    token_two = user_fixture['val_two']['token']
    channels_create_v2(token,'My Channel', True)
    channels_create_v2(token_two,'2nd Channel', True)
    auth_register_v2('henrylei1@gmail.com', 'abcdefg', 'henry', 'lei')
    auth_register_v2('henrylei2@gmail.com', 'abcdefg', 'henry', 'lei')
    auth_register_v2('henrylei3@gmail.com', 'abcdefg', 'henry', 'lei')
    auth_register_v2('henrylei4@gmail.com', 'abcdefg', 'henry', 'lei')
    auth_register_v2('henrylei5@gmail.com', 'abcdefg', 'henry', 'lei')
    assert users_stats_v1(token)['dreams_stats']['utilization_rate'] == 2/7

def test_user_stats_invalid_token(user_fixture):
    token = user_fixture['val']['token']
    auth_logout_v1(token)
    with pytest.raises(AccessError):
        user_stats_v1(token)

def test_users_stats_invalid_token(user_fixture):    
    token = user_fixture['val']['token']
    auth_logout_v1(token)
    with pytest.raises(AccessError):
        users_stats_v1(token)

def test_user_profile_img(user_fixture):
    token = user_fixture['val']['token']
    u_id = user_fixture['val']['auth_user_id']
    user_profile_uploadphoto_v1(token, 'https://upload.wikimedia.org/wikipedia/commons/7/75/Max_Verstappen_2017_Malaysia_3.jpg', 0, 0, 500, 500)
    output = user_profile_v2(token, u_id)
    assert output == {'user': {
                            'u_id': u_id,
                            'email': 'henrylei@gmail.com',
                            'name_first': 'henry',
                            'name_last': 'lei',
                            'handle_str': 'henrylei',
                            'profile_img_url': f'http://localhost:{config.port}/static/{u_id}.jpg',
                        },}

def test_user_profile_http(user_fixture):
    token = user_fixture['val']['token']
    with pytest.raises(InputError):
        user_profile_uploadphoto_v1(token, 'fakeurl.jpg', 0, 0, 100, 100)

def test_user_profile_jpg(user_fixture):
    token = user_fixture['val']['token']
    with pytest.raises(InputError):
        user_profile_uploadphoto_v1(token, 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/PNG_transparency_demonstration_1.png/280px-PNG_transparency_demonstration_1.png', 0, 0, 100, 100)

def test_user_profile_invalid_crop(user_fixture):
    token = user_fixture['val']['token']
    with pytest.raises(InputError):
        user_profile_uploadphoto_v1(token, 'https://upload.wikimedia.org/wikipedia/commons/7/75/Max_Verstappen_2017_Malaysia_3.jpg', 1000, 1000, 0, 0)

def test_user_profile_invalid_token(user_fixture):
    token = user_fixture['val']['token']
    auth_logout_v1(token)
    with pytest.raises(AccessError):
        user_profile_uploadphoto_v1(token, 'https://upload.wikimedia.org/wikipedia/commons/7/75/Max_Verstappen_2017_Malaysia_3.jpg', 0, 0, 100, 100)
