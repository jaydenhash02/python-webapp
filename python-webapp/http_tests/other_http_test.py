import pytest
import requests
import json
from src import config
from src.other import clear_v1
import random
import time
from src.http_fixture import other_fixture

#registers a user and creates a channel and checks if data is deleted
def test_clear(other_fixture):
    token = other_fixture[0]
    requests.post(config.url + "channels/create/v2", json={"token": token, "name": 'My Channel', "is_public": True})
    requests.delete(config.url + "clear/v1")
    val = requests.post(config.url + 'auth/register/v2', json={"email": "alexloke@gmail.com","password": "abcdefg", "name_first": "alex", "name_last": "loke"})
    token_four = val.json()["token"]
    data = {'users': [{'u_id': 1, 'email': 'alexloke@gmail.com', 'name_first': 'alex', 'name_last': 'loke', 'handle_str': 'alexloke', 'profile_img_url': f'http://localhost:{config.port}/static/default.jpg'}]}
    info = requests.get(config.url + "users/all/v1", params={"token": token_four})
    assert json.loads(info.text) == data
    info_one = requests.get(config.url + "channels/listall/v2", params={"token": token_four})
    assert json.loads(info_one.text) == {'channels': []}
        
#test if search works correctly
def test_search(other_fixture):
    token = other_fixture[0]
    u_id = other_fixture[1]
    token_two = other_fixture[2]
    u_id_two = other_fixture[3]
    u_id_three = other_fixture[5]

    val = requests.post(config.url + "channels/create/v2", json={"token": token, "name": 'My Channel', "is_public": True})
    channel_id = val.json()['channel_id']
    val_two = requests.post(config.url + "message/send/v2", json={"token": token, "channel_id": channel_id, "message": 'hello im henry'})
    message_id = val_two.json()['message_id']

    val_three = requests.post(config.url + "dm/create/v1", json={"token": token, "u_ids": [u_id_two]})
    dm_id = val_three.json()['dm_id']
    val_four = requests.post(config.url + "dm/create/v1", json={"token": token, "u_ids": [u_id_three]})
    dm_id_two = val_four.json()['dm_id']

    val_five = requests.post(config.url + "message/senddm/v1", json={"token": token, "dm_id": dm_id, 'message': 'hello im jayden'})
    message_id_two = val_five.json()['message_id']
    
    requests.post(config.url + "message/senddm/v1", json={"token": token_two, "dm_id": dm_id_two, 'message': 'hello im oliver'})
    val_five = requests.get(config.url + "search/v2", params={"token": token, "query_str": 'hello'})
    output = val_five.json()
    assert output['messages'][1]['message_id'] == message_id
    assert output['messages'][1]['u_id'] == u_id
    assert output['messages'][1]['message'] == 'hello im henry'
    assert output['messages'][0]['message_id'] == message_id_two
    assert output['messages'][0]['u_id'] == u_id
    assert output['messages'][0]['message'] == 'hello im jayden'

#test if error is rasied with query string >1000 characters
def test_search_querystr_length(other_fixture):
    token = other_fixture[0]
    assert requests.get(config.url + "search/v2", params={"token": token, "query_str": '5bQzlPhre49wTUhyGYG495cWyercmeBNRiye75JOWqht5ot8GjKdrdXR3DWQ1HnIrQcL1plvGMqJ4k1ITt1MLxbk01DaNFXGfirKBFvVeuXwnBb7CCvXAKYf5qiLwYdzNMLW11UF9MtdPkwqmdI0iGjEucUpuKqZhIJLXEH0ODs9aMq1JDDpp1KDzxYLQk0y8GDvt8cwqWJdrdfhf1fFf9oGfLuCfwYJrCSxGmn0vENceYIY9DjxJn4v6kXqMtkOR5Qp3ASSlbf5ZKzA0rSHIysBcSK04yOzJoWdG2seCq9FpfFr2Zb1G8lF1Lefu1vvK8NU6wC9EJEN0sNhoYOKBBh3svs7XRaIFfZu8YVpYCmtz3kmSUBtcc2utO0Fji949U86zRUjbCUvpjPpD4NIPb0fTxvK2iEUiWpDTvmFmpbq6JcK7B3lwMxqTG4NGnsRQjUkd7wKAvEPuTESMcA6FqctanHRUDSspsPnPHJkMfR599vjzlzLF4fYKr0xeVpPJASjMn0JUVSVnTUjJ5Hnae19cViWAt1Eqi3839sWgTqy8MZaqwLNcPPH69DF6HnZw7po9NaCrQoHZwpFJOYT1hvqeqm3KXNmiwfbEA6NYjfukLVe8Ki2t9StNZ693mJ5kSKRqwM1KrRu6qIgubSuV7TsAHvU6YzdkZ2gtuRV71CaJfTv38QoqgHIfQ8Lw4jMWQPfceYsr7lftWJbCZQIkMjNCodxVfLN6E4a78DXZSD7YhZ8wUXJnpd5dPr8XP3pWe5GVRVbjiT1i475LpqXgVaXrUNmCHDAeTIpKQhs5M0kpKqaDI72mZEvMR9eeXJWVqJVxKvnJT3Kp8ATSjp056Ko9LSHj1KE8yg9j6uxLs2knPwlm8JpT8EJoaSEWeV2vp6phIyZ45vWR1lhFxCKyirT5r4JropQkJntUCzxKddkQANlp7ZRZZgWO0zVMjHrEan4VNvDnPXgkDS3TTkQMrIlx9hHJ419Cst4faObm'}).status_code == 400

#test if error is rasied with invalid token
def test_search_invalid_token(other_fixture):
    token = other_fixture[0]
    requests.post(config.url + "auth/logout/v1", json={"token": token})
    assert requests.get(config.url + "search/v2", params={"token": token, "query_str": 'hello'}).status_code == 403

#test if admin can remove a user successfully
def test_admin_user_remove(other_fixture):
    token = other_fixture[0]
    u_id = other_fixture[3]
    token_two = other_fixture[2]

    val = requests.post(config.url + "channels/create/v2", json={"token": token, "name": 'My Channel', "is_public": True})
    channel_id = val.json()['channel_id']
    requests.post(config.url + "channels/create/v2", json={"token": token, "name": 'My Channel', "is_public": True})
    requests.post(config.url + "channel/join/v2", json={"token": token_two, "channel_id": channel_id})
    requests.post(config.url + "message/send/v2", json={"token": token_two, "channel_id": channel_id, "message": 'hello im henry'})
    requests.delete(config.url + "admin/user/remove/v1", json={"token": token, "u_id": u_id})
    data = requests.get(config.url + "channel/messages/v2", params={"token": token, "channel_id": channel_id, 'start': 0})
    assert data.json()['messages'][0]['message'] == 'Removed user'
    output = requests.get(config.url + "user/profile/v2", params={"token": token, "u_id": u_id})
    assert output.json()['user']['name_first'] == 'Removed' and output.json()['user']['name_last'] == 'user'

#test if error is rasied with invalid u_id
def test_invalid_u_id_admin_remove(other_fixture):
    u_id = other_fixture[1]
    u_id_two = other_fixture[3]
    u_id_three = other_fixture[5]
    token = other_fixture[0]
    invalid_id = random.randint(0, 100)

    while invalid_id == u_id or invalid_id == u_id_two or invalid_id == u_id_three:
        invalid_id = random.randint(0, 100)

    assert requests.delete(config.url + "admin/user/remove/v1", json={"token": token, "u_id": invalid_id}).status_code == 400

#test if error is raised if admin attempts to remove the only owner
def test_admin_user_remove_only_owner(other_fixture):
    token = other_fixture[0]
    u_id = other_fixture[1]
    assert requests.delete(config.url + "admin/user/remove/v1", json={"token": token, "u_id": u_id}).status_code == 400

#test if error is raised if a non admin attempts to someone
def test_admin_user_remove_not_owner(other_fixture):
    token = other_fixture[2]
    u_id = other_fixture[5]
    assert requests.delete(config.url + "admin/user/remove/v1", json={"token": token, "u_id": u_id}).status_code == 403

#test if error is raised if token is invalid
def test_admin_user_remove_invalid_token(other_fixture):
    token = other_fixture[0]
    u_id = other_fixture[3]
    requests.post(config.url + "auth/logout/v1", json={"token": token})
    assert requests.delete(config.url + "admin/user/remove/v1", json={"token": token, "u_id": u_id}).status_code == 403

#test if permission change works
def test_user_permission_change(other_fixture):
    token = other_fixture[0]
    token_two = other_fixture[2]
    u_id = other_fixture[3]
    u_id_two = other_fixture[5]
    permission_id = 1
    requests.post(config.url + "admin/userpermission/change/v1", json={"token": token, "u_id": u_id, "permission_id": permission_id})
    requests.delete(config.url + "admin/user/remove/v1", json={"token": token_two, "u_id": u_id_two})
    info = requests.get(config.url + "user/profile/v2", params={"token": token_two, "u_id": u_id_two})
    assert info.json()['user']['name_first'] == 'Removed' and info.json()['user']['name_last'] == 'user'

#test if error is raised if u id is invalid
def test_invalid_u_id_permission_change(other_fixture):
    u_id = other_fixture[1]
    u_id_two = other_fixture[3]
    u_id_three = other_fixture[5]
    token = other_fixture[0]
    permission_id = 1
    invalid_id = random.randint(0, 100)

    while invalid_id == u_id or invalid_id == u_id_two or invalid_id == u_id_three:
        invalid_id = random.randint(0, 100)
    assert requests.post(config.url + "admin/userpermission/change/v1", json={"token": token, "u_id": invalid_id, 'permission_id': permission_id}).status_code == 400

#test if error is raised if a permission id is invalid
def test_invalid_permission_id(other_fixture):
    token = other_fixture[0]
    u_id = other_fixture[3]
    invalid_permission_id = 3
    assert requests.post(config.url + "admin/userpermission/change/v1", json={"token": token, "u_id": u_id, 'permission_id': invalid_permission_id}).status_code == 400

#test if error is raised if a non admin attempts change someones id
def test_admin_user_permission_not_owner(other_fixture):
    token = other_fixture[2]
    u_id = other_fixture[5]
    permission_id = 1
    assert requests.post(config.url + "admin/userpermission/change/v1", json={"token": token, "u_id": u_id, 'permission_id': permission_id}).status_code == 403

#test if error is raised if token is invalid
def test_admin_user_permission_invalid_token(other_fixture):
    token = other_fixture[0]
    u_id = other_fixture[3]
    permission_id = 1
    requests.post(config.url + "auth/logout/v1", json={"token": token})
    assert requests.post(config.url + "admin/userpermission/change/v1", json={"token": token, "u_id": u_id, 'permission_id': permission_id}).status_code == 403

#test if notifications works
def test_notification_get_v1(other_fixture):
    token = other_fixture[0]
    token_two = other_fixture[2]
    u_id_two = other_fixture[3]
    u_id_three = other_fixture[5]
    val = requests.post(config.url + "channels/create/v2", json={"token": token, "name": 'My Channel', "is_public": True})
    channel_id = val.json()['channel_id']
    val_two = requests.post(config.url + "channels/create/v2", json={"token": token, "name": '2nd Channel', "is_public": True})
    channel_id_two = val_two.json()['channel_id']
    requests.post(config.url + "channel/invite/v2", json={"token": token, "channel_id": channel_id, "u_id": u_id_two})

    val_three = requests.post(config.url + "dm/create/v1", json={"token": token, "u_ids": [u_id_three]})
    dm_id = val_three.json()['dm_id']
    val_four = requests.post(config.url + "dm/create/v1", json={"token": token, "u_ids": [u_id_two]})
    dm_id_two = val_four.json()['dm_id']
    requests.post(config.url + "dm/invite/v1", json={"token": token, 'dm_id': dm_id, "u_id":u_id_two})

    requests.post(config.url + "message/send/v2", json={"token": token, "channel_id": channel_id, "message": 'Hi @jaydenxian'})
    requests.post(config.url + "message/send/v2", json={"token": token, "channel_id": channel_id_two, "message": 'Hello @jaydenxian'})
    requests.post(config.url + "message/senddm/v1", json={"token": token, "dm_id": dm_id, 'message': 'what up @jaydenxian'})

    output = requests.get(config.url + "notifications/get/v1", params={"token": token_two})
    data = output.json()
    assert data == {'notifications': [{'channel_id': -1, 'dm_id': dm_id, 'notification_message': 'henrylei tagged you in henrylei, oliverxu: what up @jaydenxian'},
                                                                 {'channel_id': channel_id, 'dm_id': -1, 'notification_message': 'henrylei tagged you in My Channel: Hi @jaydenxian'},
                                                                 {'channel_id': -1, 'dm_id': dm_id, 'notification_message': 'henrylei added you to henrylei, oliverxu'},
                                                                 {'channel_id': -1, 'dm_id': dm_id_two, 'notification_message': 'henrylei added you to henrylei, jaydenxian'},
                                                                 {'channel_id': channel_id, 'dm_id': -1, 'notification_message': 'henrylei added you to My Channel'}]}

#test if error is raised if token is invalid                                                       
def test_notifications_permission_invalid_token(other_fixture):
    token = other_fixture[0]
    requests.post(config.url + "auth/logout/v1", json={"token": token})
    assert requests.get(config.url + "notifications/get/v1", params={"token": token}).status_code == 403

