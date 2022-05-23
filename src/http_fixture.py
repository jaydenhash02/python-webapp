import pytest
import requests
import json
import random
import time
from src import config
from src.other import clear_v1

@pytest.fixture
def auth_fixture(): # pragma: no cover
    requests.delete(config.url + "clear/v1")

@pytest.fixture
def channel_fixture(): # pragma: no cover
    requests.delete(config.url + "clear/v1")
    val = requests.post(config.url + 'auth/register/v2', json={"email": "henrylei@gmail.com","password": "abcdefg", "name_first": "henry", "name_last": "lei"})
    token = val.json()["token"]
    u_id = val.json()["auth_user_id"]
    val_two = requests.post(config.url + "auth/register/v2", json={"email": "second@gmail.com","password": "abcdefg", "name_first": "random", "name_last": "person"})
    token_two = val_two.json()["token"]
    u_id_two = val_two.json()["auth_user_id"]
    val_three = requests.post(config.url + "auth/register/v2", json={"email": "third@gmail.com","password": "abcdefg", "name_first": "random", "name_last": "person"})
    token_three = val_three.json()["token"]
    u_id_three = val_three.json()["auth_user_id"]
    c_id = requests.post(config.url + "channels/create/v2", json={"token": token,"name": "My Channel", "is_public": True}).json()["channel_id"]
    return token, u_id, token_two, u_id_two, token_three, u_id_three, c_id

#registers 3 users and creates a channel
@pytest.fixture
def channels_fixture(): # pragma: no cover
    requests.delete(config.url + "clear/v1")
    val = requests.post(config.url + 'auth/register/v2', json={"email": "henrylei@gmail.com","password": "abcdefg","name_first": "henry","name_last": "lei"})
    token = val.json()["token"]

    val_two = requests.post(config.url + "auth/register/v2", json={
        "email": "second@gmail.com",
        "password": "abcdefg", 
        "name_first": "random", 
        "name_last": "person",
    })
    token_two = val_two.json()["token"]

    val_three = requests.post(config.url + "auth/register/v2", json={
        "email": "third@gmail.com",
        "password": "abcdefg", 
        "name_first": "random", 
        "name_last": "person",
    })
    token_three = val_three.json()["token"]

    c_id = requests.post(config.url + "channels/create/v2", json={
        "token": token,
        "name": "My Channel", 
        "is_public": True,
    }).json()["channel_id"]
    return token, token_two, token_three, c_id

#registers 3 users and creates a dm
@pytest.fixture
def dm_fixture(): # pragma: no cover
    requests.delete(config.url + 'clear/v1')
    val = requests.post(config.url + 'auth/register/v2', json={'email': 'henrylei@gmail.com','password': 'abcdefg', 'name_first': 'henry', 'name_last': 'lei'})
    token = val.json()['token']
    u_id = val.json()['auth_user_id']
    val_two = requests.post(config.url + 'auth/register/v2', json={'email': 'second@gmail.com','password': 'abcdefg', 'name_first': 'random', 'name_last': 'person'})
    token_two = val_two.json()['token']
    u_id_two = val_two.json()['auth_user_id']
    val_three = requests.post(config.url + 'auth/register/v2', json={'email': 'third@gmail.com','password': 'abcdefg', 'name_first': 'random', 'name_last': 'person'})
    token_three = val_three.json()['token']
    u_id_three = val_three.json()['auth_user_id']
    dm_id = requests.post(config.url + 'dm/create/v1', json={'token': token, 'u_ids': [u_id_two]}).json()['dm_id']
    return token, u_id, token_two, u_id_two, token_three, u_id_three, dm_id

@pytest.fixture
def message_fixture(): # pragma: no cover
    requests.delete(config.url + 'clear/v1')
    val = requests.post(config.url + 'auth/register/v2', json={'email': 'henrylei@gmail.com','password': 'abcdefg', 'name_first': 'henry', 'name_last': 'lei'})
    token = val.json()['token']
    u_id = val.json()['auth_user_id']
    val_two = requests.post(config.url  + 'auth/register/v2', json={'email': 'second@gmail.com', 'password': 'abcdefg', 'name_first': 'random', 'name_last': 'person'})
    token_two = val_two.json()['token']
    u_id_two = val_two.json()['auth_user_id']
    c_id = requests.post(config.url + 'channels/create/v2', json={'token': token, 'name': 'My Channel', 'is_public': True}).json()['channel_id']
    c_id_two = requests.post(config.url + 'channels/create/v2', json={'token': token, 'name': 'My Second Channel', 'is_public': True}).json()['channel_id']
    dm_id = requests.post(config.url + 'dm/create/v1', json={'token': token, 'u_ids': [u_id_two]}).json()['dm_id']
    return token, c_id, token_two, c_id_two, u_id, u_id_two, dm_id

#registers 3 users
@pytest.fixture
def other_fixture(): # pragma: no cover
    requests.delete(config.url + "clear/v1")
    val = requests.post(config.url + 'auth/register/v2', json={"email": "henrylei@gmail.com","password": "abcdefg", "name_first": "henry", "name_last": "lei"})
    token = val.json()["token"]
    u_id = val.json()["auth_user_id"]
    val_two = requests.post(config.url + "auth/register/v2", json={"email": "jaydenxian@gmail.com","password": "abcdefg", "name_first": "jayden", "name_last": "xian"})
    token_two = val_two.json()["token"]
    u_id_two = val_two.json()["auth_user_id"]
    val_three = requests.post(config.url + "auth/register/v2", json={"email": "oliverxu@gmail.com","password": "abcdefg", "name_first": "oliver", "name_last": "xu"})
    token_three = val_three.json()["token"]
    u_id_three = val_three.json()["auth_user_id"]
    return token, u_id, token_two, u_id_two, token_three, u_id_three

#registers 3 users and creates a channel
@pytest.fixture
def standup_fixture(): # pragma: no cover
    requests.delete(config.url + "clear/v1")
    val = requests.post(config.url + 'auth/register/v2', json={
        "email": "henrylei@gmail.com",
        "password": "abcdefg",
        "name_first": "henry",
        "name_last": "lei",
    })
    token = val.json()["token"]
    u_id = val.json()["auth_user_id"]

    val_two = requests.post(config.url + "auth/register/v2", json={
        "email": "second@gmail.com",
        "password": "abcdefg", 
        "name_first": "random", 
        "name_last": "person",
    })
    token_two = val_two.json()["token"]

    val_three = requests.post(config.url + "auth/register/v2", json={
        "email": "third@gmail.com",
        "password": "abcdefg", 
        "name_first": "random", 
        "name_last": "person",
    })
    token_three = val_three.json()["token"]

    c_id = requests.post(config.url + "channels/create/v2", json={
        "token": token,
        "name": "My Channel", 
        "is_public": True,
    }).json()["channel_id"]
    return token, token_two, token_three, c_id, u_id

@pytest.fixture
def user_fixture(): # pragma: no cover
    requests.delete(config.url + "clear/v1")
    val = requests.post(config.url + 'auth/register/v2', json={"email": "henrylei@gmail.com","password": "abcdefg", "name_first": "henry", "name_last": "lei"})
    token = val.json()["token"]
    u_id = val.json()["auth_user_id"]
    val_two = requests.post(config.url + "auth/register/v2", json={"email": "jimmywang@gmail.com","password": "abcdefg", "name_first": "jimmy", "name_last": "wang"})
    token_two = val_two.json()["token"]
    u_id_two = val_two.json()["auth_user_id"]
    return token, u_id, token_two, u_id_two