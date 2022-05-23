import pytest
import random

from src.user import user_profile_v2
from src.auth import auth_login_v2, auth_register_v2, auth_logout_v1, auth_passwordreset_reset_v1, auth_passwordreset_request_v1
from src.error import InputError, AccessError
from src.other import clear_v1
from src.fixture import auth_fixture

#test if login is successful 
def test_auth_login(auth_fixture):
    u_id = auth_register_v2('henrylei@gmail.com', 'abcdefg', 'henry', 'lei')['auth_user_id']
    u_id_two = auth_login_v2('henrylei@gmail.com', 'abcdefg')['auth_user_id']
    assert u_id == u_id_two

def test_unique_user_id(auth_fixture):
    u_id = auth_register_v2('henrylei@gmail.com', 'abcdefg', 'henry', 'lei')['auth_user_id']
    u_id_2 = auth_register_v2('jimmywang@gmail.com', 'abcdefg', 'henry', 'lei')['auth_user_id']
    assert u_id != u_id_2

#test if input error is raised with invalid email
def test_invalid_email(auth_fixture):
    with pytest.raises(InputError):
        auth_login_v2('!2#$%&@7@gmail.com', 'abcdefg')
    with pytest.raises(InputError):
        auth_register_v2('!2#$%&@7@gmail.com', 'abcdfeg', 'henry', 'lei')

#test if input error is raised with missing email
def test_email_does_not_belong_to_user(auth_fixture):
    auth_register_v2('henrylei@gmail.com', 'abcdefg', 'henry', 'lei')
    with pytest.raises(InputError):
        auth_login_v2('missing@gmail.com', 'abcdefg')

#test if input error is raised with incorrect password
def test_incorrect_password(auth_fixture):
    auth_register_v2('henrylei@gmail.com', 'abcdefg', 'henry', 'lei')
    with pytest.raises(InputError):
        auth_login_v2('henrylei@gmail.com', 'qwerty')

#test if attempting to register with same user raises input error
def test_email_already_used(auth_fixture):
    auth_register_v2('sameemail@gmail.com', 'abcdefg', 'henry', 'lei')
    with pytest.raises(InputError):
        auth_register_v2('sameemail@gmail.com', 'qwerty', 'name', 'name')

#test if input error is raised with password too short
def test_password_too_short(auth_fixture):
    with pytest.raises(InputError):
        auth_register_v2('sameemail@gmail.com', 'hi', 'name', 'name')

#test if input error is raised with empty first or last name
def test_empty_name(auth_fixture):
    with pytest.raises(InputError):
        auth_register_v2('henrylei@gmail.com', 'abcdefg', '', 'lei')
    with pytest.raises(InputError):
        auth_register_v2('henrylei@gmail.com', 'abcdefg', 'henry', '')

#test if input error is raised with name > 50 characters
def test_name_too_long(auth_fixture):
    with pytest.raises(InputError):
        auth_register_v2('henrylei@gmail.com', 'abcdefg', 'thisnameiswaytoolongandislongerthanfiftycharacterssoitisinvalid', 'lei')
    with pytest.raises(InputError):
        auth_register_v2('henrylei@gmail.com', 'abcdefg', 'henry', 'thisnameiswaytoolongandislongerthanfiftycharacterssoitisinvalid')

#test if multiple users can sucessfully register
def test_register_multiple_users(auth_fixture):
    
    u_id = auth_register_v2('henrylei@gmail.com', 'abcdefg', 'henry', 'lei')['auth_user_id']
    u_id_two = auth_login_v2('henrylei@gmail.com', 'abcdefg')['auth_user_id']
    assert u_id == u_id_two

    u_id = auth_register_v2('henrylei2@gmail.com', 'abcdefg', 'henry', 'lei')['auth_user_id']
    u_id_two = auth_login_v2('henrylei2@gmail.com', 'abcdefg')['auth_user_id']
    assert u_id == u_id_two
    
    u_id = auth_register_v2('anotheremail@gmail.com', 'wdibhqwiud', 'alex', 'loke')['auth_user_id']
    u_id_two = auth_login_v2('anotheremail@gmail.com', 'wdibhqwiud')['auth_user_id']
    assert u_id == u_id_two

#test if logout works
def test_logout(auth_fixture):
    auth_register_v2('henrylei@gmail.com', 'abcdefg', 'henry', 'lei')
    val = auth_login_v2('henrylei@gmail.com', 'abcdefg')
    token = val['token']
    assert auth_logout_v1(token) == {'is_success': True}

#test if access error is riased with invalid token
def test_invalid_logout(auth_fixture):
    auth_register_v2('henrylei@gmail.com', 'abcdefg', 'henry', 'lei')
    val = auth_login_v2('henrylei@gmail.com', 'abcdefg')
    token = val['token']
    auth_logout_v1(token)
    with pytest.raises(AccessError):
        auth_logout_v1(token)

#test if handle works
def test_returns_handle(auth_fixture):
    val = auth_register_v2('henrylei@gmail.com', 'abcdefg', 'Henry', 'Lei@ hi')
    token = val['token']
    u_id = val['auth_user_id']
    output = user_profile_v2(token, u_id)
    assert output['user']['handle_str'] == 'henryleihi'

#test if multiple same names have a unique handle 
def test_returns_unique_handle(auth_fixture):
    auth_register_v2('henrylei@gmail.com', 'abcdefg', 'henry', 'lei')
    val = auth_register_v2('henrylei1@gmail.com', 'abcdefg', 'henry', 'lei')
    token = val['token']
    u_id = val['auth_user_id']
    output = user_profile_v2(token, u_id)
    assert output['user']['handle_str'] == 'henrylei0'

#test if handle cuts off after 50 characters
def test_return_character_cutoff(auth_fixture):
    val = auth_register_v2('random@gmail.com', 'abcdefg', 'mr', 'superlongnamethatdoesntfit')
    token = val['token']
    u_id = val['auth_user_id']
    output = user_profile_v2(token, u_id)
    assert output['user']['handle_str'] == 'mrsuperlongnamethatd'

#whitebox test for password reset
def test_passwordreset_request(auth_fixture):
    auth_register_v2('henrylei@gmail.com', 'abcdefg', 'henry', 'lei')
    reset_code = auth_passwordreset_request_v1('henrylei@gmail.com')
    auth_passwordreset_reset_v1(reset_code, 'qwerty')
    auth_login_v2('henrylei@gmail.com', 'qwerty')
    with pytest.raises(InputError):
        auth_login_v2('henrylei@gmail.com', 'abcdefg')    

#whitebox test for password reset
def test_passwordreset_reset(auth_fixture):    
    auth_register_v2('henrylei@gmail.com', 'abcdefg', 'henry', 'lei')
    reset_code = auth_passwordreset_request_v1('henrylei@gmail.com')
    auth_passwordreset_reset_v1(reset_code, 'qwerty')
    with pytest.raises(InputError):
        auth_login_v2('henrylei@gmail.com', 'abcdefg')

#whitebox test for invalid reset code
def test_invalid_reset_code(auth_fixture):    
    auth_register_v2('henrylei@gmail.com', 'abcdefg', 'henry', 'lei')
    reset_code = auth_passwordreset_request_v1('henrylei@gmail.com')

    invalid_code = random.randint(10000, 99999)
    while invalid_code == reset_code:
        invalid_code = random.randint(10000, 99999)

    with pytest.raises(InputError):
        auth_passwordreset_reset_v1(invalid_code, 'qwerty')

#whitebox test for reset password too short
def test_reset_password_too_short(auth_fixture):
    auth_register_v2('henrylei@gmail.com', 'abcdefg', 'henry', 'lei')
    reset_code = auth_passwordreset_request_v1('henrylei@gmail.com')
    with pytest.raises(InputError):
        auth_passwordreset_reset_v1(reset_code, 'hi')