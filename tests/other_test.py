import pytest
import random

from src.auth import auth_login_v2, auth_register_v2, auth_logout_v1
from src.channel import channel_invite_v2, channel_details_v2, channel_messages_v2, channel_join_v2
from src.channels import channels_create_v2, channels_listall_v2
from src.dm import dm_create_v1, dm_details_v1, dm_invite_v1, dm_messages_v1, dm_list_v1, message_senddm_v1
from src.message import message_send_v2
from src.user import user_profile_v2, user_all_v1
from src import config
from src.other import clear_v1, search_v1, admin_user_remove_v1, admin_user_permission_change_v1, notifications_get_v1
from src.error import InputError, AccessError
from src.fixture import other_fixture

#registers a user and creates a channel and checks if data is deleted
def test_clear(other_fixture):
    token = other_fixture[0]['token']
    channels_create_v2(token, 'My Channel', True)
    clear_v1()
    token_four = auth_register_v2('alexloke@gmail.com', 'abcdefg', 'alex', 'loke')['token']
    assert user_all_v1(token_four) == {'users': [{'u_id': 1, 'email': 'alexloke@gmail.com', 'name_first': 'alex', 'name_last': 'loke', 'handle_str': 'alexloke', 'profile_img_url': f'http://localhost:{config.port}/static/default.jpg',}]}
    assert channels_listall_v2(token_four) == {'channels': []}
        
#test if search works correctly
def test_search(other_fixture):
    token = other_fixture[0]['token']
    u_id = other_fixture[0]['auth_user_id']
    token_two = other_fixture[1]['token']
    u_id_two = other_fixture[1]['auth_user_id']
    u_id_three = other_fixture[2]['auth_user_id']

    channel_id = channels_create_v2(token, 'My Channel', True)['channel_id']
    message_id = message_send_v2(token, channel_id, 'hello im henry')['message_id']

    dm_id = dm_create_v1(token, [u_id_two])['dm_id']
    dm_id_two = dm_create_v1(token_two, [u_id_three])['dm_id']
    message_id_two = message_senddm_v1(token, dm_id, 'hello im jayden')['message_id']
    message_senddm_v1(token_two, dm_id_two, 'hello im oliver')

    output = search_v1(token, 'hello') 
    assert output['messages'][1]['message_id'] == message_id
    assert output['messages'][1]['u_id'] == u_id
    assert output['messages'][1]['message'] == 'hello im henry'
    assert output['messages'][0]['message_id'] == message_id_two
    assert output['messages'][0]['u_id'] == u_id
    assert output['messages'][0]['message'] == 'hello im jayden'

#test if error is rasied with query string >1000 characters
def test_search_querystr_length(other_fixture):
    token = other_fixture[0]['token']
    channel_id = channels_create_v2(token, 'My Channel', True)['channel_id']
    message_send_v2(token, channel_id, 'hello im henry')
    with pytest.raises(InputError):
        search_v1(token, '5bQzlPhre49wTUhyGYG495cWyercmeBNRiye75JOWqht5ot8GjKdrdXR3DWQ1HnIrQcL1plvGMqJ4k1ITt1MLxbk01DaNFXGfirKBFvVeuXwnBb7CCvXAKYf5qiLwYdzNMLW11UF9MtdPkwqmdI0iGjEucUpuKqZhIJLXEH0ODs9aMq1JDDpp1KDzxYLQk0y8GDvt8cwqWJdrdfhf1fFf9oGfLuCfwYJrCSxGmn0vENceYIY9DjxJn4v6kXqMtkOR5Qp3ASSlbf5ZKzA0rSHIysBcSK04yOzJoWdG2seCq9FpfFr2Zb1G8lF1Lefu1vvK8NU6wC9EJEN0sNhoYOKBBh3svs7XRaIFfZu8YVpYCmtz3kmSUBtcc2utO0Fji949U86zRUjbCUvpjPpD4NIPb0fTxvK2iEUiWpDTvmFmpbq6JcK7B3lwMxqTG4NGnsRQjUkd7wKAvEPuTESMcA6FqctanHRUDSspsPnPHJkMfR599vjzlzLF4fYKr0xeVpPJASjMn0JUVSVnTUjJ5Hnae19cViWAt1Eqi3839sWgTqy8MZaqwLNcPPH69DF6HnZw7po9NaCrQoHZwpFJOYT1hvqeqm3KXNmiwfbEA6NYjfukLVe8Ki2t9StNZ693mJ5kSKRqwM1KrRu6qIgubSuV7TsAHvU6YzdkZ2gtuRV71CaJfTv38QoqgHIfQ8Lw4jMWQPfceYsr7lftWJbCZQIkMjNCodxVfLN6E4a78DXZSD7YhZ8wUXJnpd5dPr8XP3pWe5GVRVbjiT1i475LpqXgVaXrUNmCHDAeTIpKQhs5M0kpKqaDI72mZEvMR9eeXJWVqJVxKvnJT3Kp8ATSjp056Ko9LSHj1KE8yg9j6uxLs2knPwlm8JpT8EJoaSEWeV2vp6phIyZ45vWR1lhFxCKyirT5r4JropQkJntUCzxKddkQANlp7ZRZZgWO0zVMjHrEan4VNvDnPXgkDS3TTkQMrIlx9hHJ419Cst4faObm') 

#test if error is rasied with invalid token
def test_search_invalid_token(other_fixture):
    token = other_fixture[0]['token']
    auth_logout_v1(token)
    with pytest.raises(AccessError):
        search_v1(token, 'hello')

#test if admin can remove a user successfully
def test_admin_user_remove(other_fixture):
    token = other_fixture[0]['token']
    u_id = other_fixture[1]['auth_user_id']
    token_two = other_fixture[1]['token']
    channel_id = channels_create_v2(token, 'My Channel', True)['channel_id']
    channel_join_v2(token_two, channel_id)
    message_send_v2(token_two, channel_id, 'hello im henry')
    admin_user_remove_v1(token, u_id)
    assert channel_messages_v2(token, channel_id, 0)['messages'][0]['message'] == 'Removed user'
    output = user_profile_v2(token, u_id)
    assert output['user']['name_first'] == 'Removed' and output['user']['name_last'] == 'user'

#test if error is rasied with invalid u_id
def test_invalid_u_id_admin_remove(other_fixture):
    u_id = other_fixture[0]['auth_user_id']
    u_id_two = other_fixture[1]['auth_user_id']
    u_id_three = other_fixture[2]['auth_user_id']
    token = other_fixture[0]['token']
    invalid_id = random.randint(0, 100)

    while invalid_id == u_id or invalid_id == u_id_two or invalid_id == u_id_three:
        invalid_id = random.randint(0, 100)

    with pytest.raises(InputError):
        admin_user_remove_v1(token, invalid_id)

#test if error is raised if admin attempts to remove the only owner
def test_admin_user_remove_only_owner(other_fixture):
    token = other_fixture[0]['token']
    u_id = other_fixture[0]['auth_user_id']
    with pytest.raises(InputError):
        admin_user_remove_v1(token, u_id)

#test if error is raised if a non admin attempts to someone
def test_admin_user_remove_not_owner(other_fixture):
    token = other_fixture[1]['token']
    u_id = other_fixture[2]['auth_user_id']
    with pytest.raises(AccessError):
        admin_user_remove_v1(token, u_id)

#test if error is raised if token is invalid
def test_admin_user_remove_invalid_token(other_fixture):
    token = other_fixture[0]['token']
    u_id = other_fixture[1]['auth_user_id']
    auth_logout_v1(token)
    with pytest.raises(AccessError):
        admin_user_remove_v1(token, u_id)

#test if permission change works
def test_user_permission_change(other_fixture):
    token = other_fixture[0]['token']
    token_two = other_fixture[1]['token']
    u_id = other_fixture[1]['auth_user_id']
    u_id_two = other_fixture[2]['auth_user_id']
    permission_id = 1
    admin_user_permission_change_v1(token, u_id, permission_id)
    admin_user_remove_v1(token_two, u_id_two)
    output = user_profile_v2(token_two, u_id_two)
    assert output['user']['name_first'] == 'Removed' and output['user']['name_last'] == 'user'

#test if error is raised if u id is invalid
def test_invalid_u_id_permission_change(other_fixture):
    u_id = other_fixture[0]['auth_user_id']
    u_id_two = other_fixture[1]['auth_user_id']
    u_id_three = other_fixture[2]['auth_user_id']
    token = other_fixture[0]['token']
    permission_id = 1
    invalid_id = random.randint(0, 100)

    while invalid_id == u_id or invalid_id == u_id_two or invalid_id == u_id_three:
        invalid_id = random.randint(0, 100)

    with pytest.raises(InputError):
        admin_user_permission_change_v1(token, invalid_id, permission_id)

#test if error is raised if a permission id is invalid
def test_invalid_permission_id(other_fixture):
    token = other_fixture[0]['token']
    u_id = other_fixture[1]['auth_user_id']
    invalid_permission_id = 3
    with pytest.raises(InputError):
        admin_user_permission_change_v1(token, u_id, invalid_permission_id)

#test if error is raised if a non admin attempts change someones id
def test_admin_user_permission_not_owner(other_fixture):
    token = other_fixture[1]['token']
    u_id = other_fixture[2]['auth_user_id']
    permission_id = 1
    with pytest.raises(AccessError):
        admin_user_permission_change_v1(token, u_id, permission_id)

#test if error is raised if token is invalid
def test_admin_user_permission_invalid_token(other_fixture):
    token = other_fixture[0]['token']
    u_id = other_fixture[1]['auth_user_id']
    permission_id = 1
    auth_logout_v1(token)
    with pytest.raises(AccessError):
        admin_user_permission_change_v1(token, u_id, permission_id)

#test if notifications works
def test_notification_get_v1(other_fixture):
    token = other_fixture[0]['token']
    token_two = other_fixture[1]['token']
    u_id_two = other_fixture[1]['auth_user_id']
    u_id_three = other_fixture[2]['auth_user_id']
    channel_id = channels_create_v2(token, 'My Channel', True)['channel_id']
    channel_id_two = channels_create_v2(token, '2nd Channel', True)['channel_id']
    channel_invite_v2(token, channel_id, u_id_two)
    dm_id = dm_create_v1(token, [u_id_three])['dm_id']
    dm_id_two = dm_create_v1(token, [u_id_two])['dm_id']
    dm_invite_v1(token, dm_id, u_id_two)
    message_send_v2(token, channel_id, 'Hi @jaydenxian')
    message_send_v2(token, channel_id_two, 'Hello @jaydenxian')
    message_senddm_v1(token, dm_id, 'what up @jaydenxian')
    assert notifications_get_v1(token_two) == {'notifications': [{'channel_id': -1, 'dm_id': dm_id, 'notification_message': 'henrylei tagged you in henrylei, oliverxu: what up @jaydenxian'},
                                                                 {'channel_id': channel_id, 'dm_id': -1, 'notification_message': 'henrylei tagged you in My Channel: Hi @jaydenxian'},
                                                                 {'channel_id': -1, 'dm_id': dm_id, 'notification_message': 'henrylei added you to henrylei, oliverxu'},
                                                                 {'channel_id': -1, 'dm_id': dm_id_two, 'notification_message': 'henrylei added you to henrylei, jaydenxian'},
                                                                 {'channel_id': channel_id, 'dm_id': -1, 'notification_message': 'henrylei added you to My Channel'}]}

#test if error is raised if token is invalid                                                                                                          
def test_notifications_permission_invalid_token(other_fixture):
    token = other_fixture[0]['token']
    auth_logout_v1(token)
    with pytest.raises(AccessError):
        notifications_get_v1(token)
