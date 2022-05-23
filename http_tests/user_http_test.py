import pytest
import requests
import json
from src import config
import random
import time
from src.http_fixture import user_fixture

#test if user profile works
def test_user_profile(user_fixture):
    u_id = user_fixture[1]
    token = user_fixture[0]
    data = {'user': {
                    'u_id': u_id,
                    'email': 'henrylei@gmail.com',
                    'name_first': 'henry',
                    'name_last': 'lei',
                    'handle_str': 'henrylei',
                    'profile_img_url': f'http://localhost:{config.port}/static/default.jpg',
                },}
    info = requests.get(config.url + "user/profile/v2", params={"token": token, "u_id": u_id})
    assert json.loads(info.text) == data

#tests if input error is raised with invalid auth id
def test_invalid_user_id_profile(user_fixture):
    u_id = user_fixture[1]
    u_id_two = user_fixture[3]
    token = user_fixture[0]
    invalid_id = random.randint(0, 10)
    while invalid_id == u_id or invalid_id == u_id_two:
        invalid_id = random.randint(0, 10)

    assert requests.get(config.url + "user/profile/v2", params={"token": token, "u_id": invalid_id}).status_code == 400

#tests if access error is raised with invalid token
def test_invalid_token_profile(user_fixture):
    u_id = user_fixture[1]
    token = user_fixture[0]
    requests.post(config.url + "auth/logout/v1", json={"token": token})
    assert requests.get(config.url + "user/profile/v2", params={"token": token, "u_id": u_id}).status_code == 403

#test if profile setname works
def test_profile_setname(user_fixture):
    u_id = user_fixture[1]
    token = user_fixture[0]
    requests.put(config.url + "user/profile/setname/v2", json={"token": token, "name_first": "alex", "name_last": "loke"})
    info = requests.get(config.url + "user/profile/v2", params={"token": token, "u_id": u_id})
    assert json.loads(info.text)['user']['name_first'] == 'alex' and json.loads(info.text)['user']['name_last'] == 'loke'

#test if input error is raised with empty name inputs
def test_profile_setname_empty(user_fixture):
    token = user_fixture[0]
    assert requests.put(config.url + "user/profile/setname/v2", json={"token": token, "name_first": '', "name_last": "loke"}).status_code == 400
    assert requests.put(config.url + "user/profile/setname/v2", json={"token": token, "name_first": "alex", "name_last": ''}).status_code == 400

#test if input error is raised if name is longer than fifty characters
def test_profile_setname_long(user_fixture):
    token = user_fixture[0]
    assert requests.put(config.url + "user/profile/setname/v2", json={"token": token, "name_first": "thisnameissuperongandhopefullyitismorethanfiftycharacterssoaninputerrorisraised", "name_last": "loke"}).status_code == 400
    assert requests.put(config.url + "user/profile/setname/v2", json={"token": token, "name_first": "alex", "name_last": "thisnameissuperongandhopefullyitismorethanfiftycharacterssoaninputerrorisraised"}).status_code == 400

#test if access error is raised with invalid token
def test_invalid_token_setname(user_fixture):
    token = user_fixture[0]
    requests.post(config.url + "auth/logout/v1", json={"token": token})
    assert requests.put(config.url + "user/profile/setname/v2", json={"token": token, "name_first": "alex", "name_last": "loke"}).status_code == 403

#test if profile setname works
def test_profile_setemail(user_fixture):
    u_id = user_fixture[1]
    token = user_fixture[0]
    requests.put(config.url + "user/profile/setemail/v2", json={"token": token, "email": "alexloke@gmail.com"})
    info = requests.get(config.url + "user/profile/v2", params={"token": token, "u_id": u_id})
    assert json.loads(info.text)['user']['email'] == 'alexloke@gmail.com'

#test if error is raised if email is invalid
def test_profile_invalid_email(user_fixture):
    token = user_fixture[0]
    assert requests.put(config.url + "user/profile/setemail/v2", json={"token": token, "email": "bued@^&!&*@gma@gmail.com"}).status_code == 400

#test if error email is already used
def test_profile_email_already_used(user_fixture):
    token = user_fixture[0]
    assert requests.put(config.url + "user/profile/setemail/v2", json={"token": token, "email": "jimmywang@gmail.com"}).status_code == 400

#test if error is raised if token is invalid
def test_invalid_token_setemail(user_fixture):
    token = user_fixture[0]
    requests.post(config.url + "auth/logout/v1", json={"token": token})
    assert requests.put(config.url + "user/profile/setemail/v2", json={"token": token, "email": "alexloke@gmail.com"}).status_code == 403

    #test if profile sethandle works
def test_profile_sethandle(user_fixture):
    u_id = user_fixture[1]
    token = user_fixture[0]
    requests.put(config.url + "user/profile/sethandle/v1", json={"token": token, "handle_str": "alexloke"})
    info = requests.get(config.url + "user/profile/v2", params={"token": token, "u_id": u_id})
    assert json.loads(info.text)['user']['handle_str'] == 'alexloke'

#test if input error is raised if name is longer than twenty characters or less than 3
def test_profile_handle_invalid_length(user_fixture):
    token = user_fixture[0]
    assert requests.put(config.url + "user/profile/sethandle/v1", json={"token": token, "handle_str": "hi"}).status_code == 400
    assert requests.put(config.url + "user/profile/sethandle/v1", json={"token": token, "handle_str": "thishandleiswaylongerthantwentycharacters"}).status_code == 400

#test if inputerror is raised if handle is already used
def test_profile_setname_handle_already_used(user_fixture):
    token = user_fixture[0]
    assert requests.put(config.url + "user/profile/sethandle/v1", json={"token": token, "handle_str": "jimmywang"}).status_code == 400

#test if access error is raised with invalid token
def test_invalid_token_sethandle(user_fixture):
    token = user_fixture[0]
    requests.post(config.url + "auth/logout/v1", json={"token": token})
    assert requests.put(config.url + "user/profile/sethandle/v1", json={"token": token, "handle_str": "alexloke"}).status_code == 403

#test if user all works
def test_user_all(user_fixture):
    token = user_fixture[0]
    u_id = user_fixture[1]
    u_id_two = user_fixture[3]
    data = {'users': [{'u_id': u_id, 'email': 'henrylei@gmail.com', 'name_first': 'henry', 'name_last': 'lei', 'handle_str': 'henrylei', 'profile_img_url': f'http://localhost:{config.port}/static/default.jpg', }, 
                      {'u_id': u_id_two, 'email': 'jimmywang@gmail.com', 'name_first': 'jimmy', 'name_last': 'wang', 'handle_str': 'jimmywang', 'profile_img_url': f'http://localhost:{config.port}/static/default.jpg'}]}
    info = requests.get(config.url + "users/all/v1", params={"token": token})
    assert json.loads(info.text) == data

#test if access error is raised with invalid token
def test_invalid_token_all(user_fixture):
    token = user_fixture[0]
    requests.post(config.url + "auth/logout/v1", json={"token": token})
    assert requests.get(config.url + "users/all/v1", params={"token": token,}).status_code == 403

def test_user_stats(user_fixture):
    token = user_fixture[0]
    token_two = user_fixture[2]
    u_id_two = user_fixture[3]
    c_id_one = requests.post(config.url + "channels/create/v2", json={"token": token, "name": "My Channel", "is_public": True}).json()["channel_id"]
    c_id_two = requests.post(config.url + "channels/create/v2", json={"token": token_two, "name": "2nd Channel", "is_public": True}).json()["channel_id"]
    requests.post(config.url + 'message/send/v2', json={'token': token, 'channel_id': c_id_one, 'message': "hello"})
    requests.post(config.url + 'message/send/v2', json={'token': token_two, 'channel_id': c_id_two, 'message': "hello"})
    requests.post(config.url + 'dm/create/v1', json={'token': token, 'u_ids': [u_id_two]})

    info = requests.get(config.url + 'user/stats/v1', params={'token': token})
    assert json.loads(info.text)['user_stats']['channels_joined'][-1]['num_channels_joined'] == 1

    info = requests.get(config.url + 'user/stats/v1', params={'token': token})
    assert json.loads(info.text)['user_stats']['dms_joined'][-1]['num_dms_joined'] == 1

    info = requests.get(config.url + 'user/stats/v1', params={'token': token})
    assert json.loads(info.text)['user_stats']['messages_sent'][-1]['num_messages_sent'] == 1

    info = requests.get(config.url + 'user/stats/v1', params={'token': token})
    assert json.loads(info.text)['user_stats']['involvement_rate'] == 3/5

def test_users_stats(user_fixture):
    token = user_fixture[0]
    token_two = user_fixture[2]
    u_id_two = user_fixture[3]
    c_id_one = requests.post(config.url + "channels/create/v2", json={"token": token, "name": "My Channel", "is_public": True}).json()["channel_id"]
    c_id_two = requests.post(config.url + "channels/create/v2", json={"token": token_two, "name": "2nd Channel", "is_public": True}).json()["channel_id"]
    requests.post(config.url + 'message/send/v2', json={'token': token, 'channel_id': c_id_one, 'message': "hello"})
    requests.post(config.url + 'message/send/v2', json={'token': token_two, 'channel_id': c_id_two, 'message': "hello"})
    requests.post(config.url + 'dm/create/v1', json={'token': token, 'u_ids': [u_id_two]})

    info = requests.get(config.url + 'users/stats/v1', params={'token': token})
    assert json.loads(info.text)['dreams_stats']['channels_exist'][-1]['num_channels_exist'] == 2

    info = requests.get(config.url + 'users/stats/v1', params={'token': token})
    assert json.loads(info.text)['dreams_stats']['dms_exist'][-1]['num_dms_exist'] == 1

    info = requests.get(config.url + 'users/stats/v1', params={'token': token})
    assert json.loads(info.text)['dreams_stats']['messages_exist'][-1]['num_messages_exist'] == 2

    info = requests.get(config.url + 'users/stats/v1', params={'token': token})
    assert json.loads(info.text)['dreams_stats']['utilization_rate'] == 2/2

def test_users_stats_multiple_users(user_fixture):
    token = user_fixture[0]
    token_two = user_fixture[2]
    requests.post(config.url + "channels/create/v2", json={"token": token, "name": "My Channel", "is_public": True}).json()["channel_id"]
    requests.post(config.url + "channels/create/v2", json={"token": token_two, "name": "2nd Channel", "is_public": True}).json()["channel_id"]
    
    requests.post(config.url + 'auth/register/v2', json={"email": "henrylei1@gmail.com","password": "abcdefg", "name_first": "henry", "name_last": "lei"})
    requests.post(config.url + 'auth/register/v2', json={"email": "henrylei2@gmail.com","password": "abcdefg", "name_first": "henry", "name_last": "lei"})
    requests.post(config.url + 'auth/register/v2', json={"email": "henrylei3@gmail.com","password": "abcdefg", "name_first": "henry", "name_last": "lei"})
    requests.post(config.url + 'auth/register/v2', json={"email": "henrylei4@gmail.com","password": "abcdefg", "name_first": "henry", "name_last": "lei"})
    requests.post(config.url + 'auth/register/v2', json={"email": "henrylei5@gmail.com","password": "abcdefg", "name_first": "henry", "name_last": "lei"})

    info = requests.get(config.url + 'users/stats/v1', params={'token': token})
    assert json.loads(info.text)['dreams_stats']['utilization_rate'] == 2/7

def test_user_stats_invalid_token(user_fixture):
    token = user_fixture[0]
    requests.post(config.url + "auth/logout/v1", json={"token": token})
    assert requests.get(config.url + 'user/stats/v1', params={'token': token}).status_code == 403

def test_users_stats_invalid_token(user_fixture):    
    token = user_fixture[0]
    requests.post(config.url + "auth/logout/v1", json={"token": token})
    assert requests.get(config.url + 'user/stats/v1', params={'token': token}).status_code == 403

def test_user_profile_image(user_fixture):
    token = user_fixture[0]
    u_id = user_fixture[1]
    requests.post(config.url + '/user/profile/uploadphoto/v1', json={'token': token, 'img_url': 'https://upload.wikimedia.org/wikipedia/commons/7/75/Max_Verstappen_2017_Malaysia_3.jpg', 'x_start': 0, 'y_start': 0, 'x_end': 500, 'y_end': 500})
    info = requests.get(config.url + "user/profile/v2", params={"token": token, "u_id": u_id})

    assert json.loads(info.text) == {'user': {
                            'u_id': u_id,
                            'email': 'henrylei@gmail.com',
                            'name_first': 'henry',
                            'name_last': 'lei',
                            'handle_str': 'henrylei',
                            'profile_img_url': f'http://localhost:{config.port}/static/{u_id}.jpg',
                        },}

def test_user_profile_http(user_fixture):
    token = user_fixture[0]
    assert requests.post(config.url + '/user/profile/uploadphoto/v1', json={'token': token, 'img_url': 'fakeurl.jpg', 'x_start': 0, 'y_start': 0, 'x_end': 500, 'y_end': 500}).status_code == 400


def test_user_profile_jpg(user_fixture):
    token = user_fixture[0]
    assert requests.post(config.url + '/user/profile/uploadphoto/v1', json={'token': token, 'img_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/PNG_transparency_demonstration_1.png/280px-PNG_transparency_demonstration_1.png', 'x_start': 0, 'y_start': 0, 'x_end': 500, 'y_end': 500}).status_code == 400

def test_user_profile_invalid_crop(user_fixture):
    token = user_fixture[0]
    assert requests.post(config.url + '/user/profile/uploadphoto/v1', json={'token': token, 'img_url': 'https://upload.wikimedia.org/wikipedia/commons/7/75/Max_Verstappen_2017_Malaysia_3.jpg', 'x_start': 0, 'y_start': 0, 'x_end': 5000, 'y_end': 5000}).status_code == 400

def test_user_profile_invalid_token(user_fixture):
    token = user_fixture[0]
    requests.post(config.url + "auth/logout/v1", json={"token": token})
    assert requests.post(config.url + '/user/profile/uploadphoto/v1', json={'token': token, 'img_url': 'https://upload.wikimedia.org/wikipedia/commons/7/75/Max_Verstappen_2017_Malaysia_3.jpg', 'x_start': 0, 'y_start': 0, 'x_end': 100, 'y_end': 100}).status_code == 403

