import pytest
import requests
import json
import random
from src import config
from src.other import clear_v1
from src.auth import auth_passwordreset_request_v1
from src.http_fixture import auth_fixture

#test if login is successful and returns correct dict
def test_auth_login(auth_fixture):
    resp_one = requests.post(config.url + 'auth/register/v2', json={'email': 'henrylei@gmail.com','password': 'abcdefg', 'name_first': 'henry', 'name_last': 'lei'})
    resp_two = requests.post(config.url + 'auth/login/v2', json={'email': 'henrylei@gmail.com','password': 'abcdefg'})
    u_id = resp_one.json()['auth_user_id']
    u_id_two = resp_two.json()['auth_user_id']
    assert u_id == u_id_two

#test if input error is raised with invalid email
def test_invalid_email(auth_fixture):
    assert requests.post(config.url + 'auth/register/v2', json={'email': '!2#$%&@7@gmail.com','password': 'abcdefg', 'name_first': 'henry', 'name_last': 'lei'}).status_code == 400
    assert requests.post(config.url + 'auth/login/v2', json={'email': 'whizzfizz','password': 'abcdefg'}).status_code == 400

#test if input error is raised with missing email
def test_email_does_not_belong_to_user(auth_fixture):
    requests.post(config.url + 'auth/register/v2', json={'email': 'henrylei@gmail.com','password': 'abcdefg', 'name_first': 'henry', 'name_last': 'lei'})
    assert requests.post(config.url + 'auth/login/v2', json={'email': 'whizzbang@gmail.com','password': 'abcdefg'}).status_code == 400


#test if input error is raised with incorrect password
def test_incorrect_password(auth_fixture):
    requests.post(config.url + 'auth/register/v2', json={'email': 'henrylei@gmail.com','password': 'abcdefg', 'name_first': 'henry', 'name_last': 'lei'})
    assert requests.post(config.url + 'auth/login/v2', json={'email': 'henrylei@gmail.com','password': 'jayden'}).status_code == 400


#test if attempting to register with same user raises input error
def test_email_already_used(auth_fixture):
    requests.post(config.url + 'auth/register/v2', json={'email': 'henrylei@gmail.com','password': 'abcdefg', 'name_first': 'henry', 'name_last': 'lei'})
    assert requests.post(config.url + 'auth/register/v2', json={'email': 'henrylei@gmail.com','password': 'abcdefg', 'name_first': 'henry', 'name_last': 'lei'}).status_code == 400


#test if input error is raised with password too short
def test_password_too_short(auth_fixture):
    assert requests.post(config.url + 'auth/register/v2', json={'email': 'henrylei@gmail.com','password': 'hi', 'name_first': 'henry', 'name_last': 'lei'}).status_code == 400


#test if input error is raised with empty first or last name
def test_empty_name(auth_fixture):
    assert requests.post(config.url + 'auth/register/v2', json={'email': 'henrylei@gmail.com','password': 'abcdefg', 'name_first': '', 'name_last': 'lei'}).status_code == 400
    assert requests.post(config.url + 'auth/register/v2', json={'email': 'henrylei@gmail.com','password': 'abcdefg', 'name_first': 'henry', 'name_last': ''}).status_code == 400


#test if input error is raised with name > 50 characters
def test_name_too_long(auth_fixture):
    assert requests.post(config.url + 'auth/register/v2', json={'email': 'henrylei@gmail.com','password': 'abcdefg', 'name_first': 'thisnameiswaytoolongandislongerthanfiftycharacterssoitisinvalid', 'name_last': 'lei'}).status_code == 400
    assert requests.post(config.url + 'auth/register/v2', json={'email': 'henrylei@gmail.com','password': 'abcdefg', 'name_first': 'henry', 'name_last': 'thisnameiswaytoolongandislongerthanfiftycharacterssoitisinvalid'}).status_code == 400


#test if multiple users can sucessfully register
def test_register_multiple_users(auth_fixture):
    resp_one = requests.post(config.url + 'auth/register/v2', json={'email': 'henrylei@gmail.com','password': 'abcdefg', 'name_first': 'henry', 'name_last': 'lei'})
    resp_two = requests.post(config.url + 'auth/login/v2', json={'email': 'henrylei@gmail.com','password': 'abcdefg'})
    assert json.loads(resp_one.text)['auth_user_id'] == json.loads(resp_two.text)['auth_user_id']
    resp_three = requests.post(config.url + 'auth/register/v2', json={'email': 'jimmywang@gmail.com','password': 'abcdefg', 'name_first': 'jimmy', 'name_last': 'wang'})
    resp_four = requests.post(config.url + 'auth/login/v2', json={'email': 'jimmywang@gmail.com','password': 'abcdefg'})
    assert json.loads(resp_three.text)['auth_user_id'] == json.loads(resp_four.text)['auth_user_id']
    resp_five = requests.post(config.url + 'auth/register/v2', json={'email': 'jaydenxian@gmail.com','password': 'abcdefg', 'name_first': 'jayden', 'name_last': 'xian'})
    resp_six = requests.post(config.url + 'auth/login/v2', json={'email': 'jaydenxian@gmail.com','password': 'abcdefg'})
    assert json.loads(resp_five.text)['auth_user_id'] == json.loads(resp_six.text)['auth_user_id']

#test if logout sucessfully works
def test_logout(auth_fixture):
    requests.post(config.url + 'auth/register/v2', json={'email': 'henrylei@gmail.com','password': 'abcdefg', 'name_first': 'henry', 'name_last': 'lei'})
    data = requests.post(config.url + 'auth/login/v2', json={'email': 'henrylei@gmail.com','password': 'abcdefg'})
    token = data.json()['token']
    resp = requests.post(config.url + 'auth/logout/v1', json={'token': token})
    assert json.loads(resp.text) == {'is_success': True}

#testing if handle string works according to spec
def test_returns_handle(auth_fixture):
    data = requests.post(config.url + 'auth/register/v2', json={'email': 'henrylei@gmail.com','password': 'abcdefg', 'name_first': 'Henry', 'name_last': 'Lei@ hi'})
    u_id = data.json()['auth_user_id']
    token = data.json()['token']
    resp = requests.get(config.url + 'user/profile/v2', params={'token': token, 'u_id': u_id})
    assert json.loads(resp.text)['user']['handle_str'] == 'henryleihi'

#testing if handle string works
def test_returns_unique_handle(auth_fixture):
    requests.post(config.url + 'auth/register/v2', json={'email': 'henrylei@gmail.com','password': 'abcdefg', 'name_first': 'Henry', 'name_last': 'Lei'})
    data = requests.post(config.url + 'auth/register/v2', json={'email': 'henrylei1@gmail.com','password': 'abcdefg', 'name_first': 'Henry', 'name_last': 'Lei'})
    u_id = data.json()['auth_user_id']
    token = data.json()['token']
    resp = requests.get(config.url + 'user/profile/v2', params={'token': token, 'u_id': u_id})
    assert json.loads(resp.text)['user']['handle_str'] == 'henrylei0'

#testing if handle string is longer than 20 characters
def test_return_character_cutoff(auth_fixture):
    data = requests.post(config.url + 'auth/register/v2', json={'email': 'henrylei@gmail.com','password': 'abcdefg', 'name_first': 'mr', 'name_last': 'superlongnamethatdoesntfit'})
    u_id = data.json()['auth_user_id']
    token = data.json()['token']
    resp = requests.get(config.url + 'user/profile/v2', params={'token': token, 'u_id': u_id})
    assert json.loads(resp.text)['user']['handle_str'] == 'mrsuperlongnamethatd'

#testing if password reset_request_raises any errors
def test_passwordreset_request(auth_fixture):
    requests.post(config.url + 'auth/register/v2', json={'email': 'comp1531assignment@gmail.com', 'password': 'abcdefg', 'name_first': 'henry', 'name_last': 'lei'})
    resp = requests.post(config.url + 'auth/passwordreset/request/v1', json={'email': 'comp1531assignment@gmail.com'})
    assert json.loads(resp.text) == {}

#testing if input error is rasied with an invalid code
def test_passwordreset_invalid_code(auth_fixture):
    requests.post(config.url + 'auth/register/v2', json={'email': 'comp1531assignment@gmail.com', 'password': 'abcdefg', 'name_first': 'henry', 'name_last': 'lei'})
    invalid_code = random.randint(0, 9999)
    assert requests.post(config.url + 'auth/passwordreset/reset/v1', json={'reset_code': invalid_code, 'new_password': 'qwerty'}).status_code == 400

#testing if input error is raised with a password shorter than 6 characters, WHITEBOX TEST
def test_passwordreset_password_short(auth_fixture):
    requests.post(config.url + 'auth/register/v2', json={'email': 'comp1531assignment@gmail.com', 'password': 'abcdefg', 'name_first': 'henry', 'name_last': 'lei'})
    reset_code = auth_passwordreset_request_v1('comp1531assignment@gmail.com')
    assert requests.post(config.url + 'auth/passwordreset/reset/v1', json={'reset_code': reset_code, 'new_password': 'hi'}).status_code == 400

