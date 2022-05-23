import json
import requests
import urllib
import pytest
from src import config
from src.http_fixture import channels_fixture

# testing for invalid token in channels_create_v2
def test_invalid_token_channels_create_http(channels_fixture): 
    token = channels_fixture[0]
    requests.post(config.url + "auth/logout/v1", json={
        'token':token,
    })
    assert requests.post(config.url + "channels/create/v2", json={
        'token':token,
        'name':'My Channel',
        'is_public':True,
    }).status_code == 403

#testing for invalid token in channels_listall_v2
def test_invalid_token_channels_listall_http(channels_fixture):
    token = channels_fixture[0]
    requests.post(config.url + "auth/logout/v1", json={
        'token':token,
    })
    assert requests.get(config.url + "channels/listall/v2", params={
        'token':token,
    }).status_code == 403


#testing for invalid token in channels_listall_v2
def test_invalid_token_channels_list_http(channels_fixture):
    token = channels_fixture[0]
    requests.post(config.url + "auth/logout/v1", json={
        'token':token,
    })
    assert requests.get(config.url + "channels/list/v2", params={
        'token':token,
    }).status_code == 403

#testing for channel names that are too long
def test_long_one_error_channels_create(channels_fixture): 
    token = channels_fixture[1]
    assert requests.post(config.url + 'channels/create/v2', json={
        'token': token,
        'name': 'ThisChannelNameIsVeryLongAndMustBeOver20CharactersLong', 
        'is_public': True
    }).status_code == 400

    assert requests.post(config.url + 'channels/create/v2', json={
        'token': token,
        'name': '696969696969696969669696696969696969', 
        'is_public': True
    }).status_code == 400

#test if channel list all correctly lists one channel
def test_channels_listall_one_channel(channels_fixture): 
    token = channels_fixture[0]
    c_id = channels_fixture[3]
    resp = requests.get(config.url + 'channels/listall/v2', params={
        'token': token,
    })
    data_output = {
        'channels': [
            {
                'channel_id': c_id, 
                'name': 'My Channel'
            }
        ]
    }
    assert json.loads(resp.text) == data_output

#test if channel list correctly lists one channel
def test_channels_list_one_channel(channels_fixture): 
    token = channels_fixture[0]
    c_id = channels_fixture[3]
    resp = requests.get(config.url + 'channels/list/v2', params={
        'token': token,
    })
    data_output = {
        'channels': [
            {
                'channel_id': c_id, 
                'name': 'My Channel'
            }
        ]
    }
    assert json.loads(resp.text) == data_output

#test if channel list all correctly lists channels of differnet users
def test_channels_list_two_channels_different_user(channels_fixture): 
    token_one = channels_fixture[0]
    token_two = channels_fixture[1]
    c_id1 = channels_fixture[3]
    c_id2 = requests.post(config.url + 'channels/create/v2', json={
        'token': token_two,
        'name': 'My Channel2', 
        'is_public': True,
    }).json()['channel_id']

    response1 = requests.get(config.url + 'channels/list/v2', params={
        'token': token_one,
    })
    data1 = {
        'channels': [
            {
                'channel_id': c_id1,
                'name': 'My Channel'
            }
        ]
    }

    assert json.loads(response1.text) == data1

    response2 = requests.get(config.url + 'channels/list/v2', params={
        'token': token_two,
    })
    data2 = {
        'channels': [
            {
                'channel_id': c_id2,
                'name': 'My Channel2'
            }
        ]
    }
    assert json.loads(response2.text) == data2

#test if channel list all correctly lists three channels
def test_channels_listall_three_channel(channels_fixture): 
    token_one = channels_fixture[0]
    token_two = channels_fixture[1]
    token_three = channels_fixture[2]

    c_id1 = channels_fixture[3]

    c_id2 = requests.post(config.url + 'channels/create/v2', json={
        'token': token_two,
        'name': 'My Channel2', 
        'is_public': True
    }).json()["channel_id"]

    c_id3 = requests.post(config.url + 'channels/create/v2', json={
        'token': token_three,
        'name': 'My Channel3', 
        'is_public': True
    }).json()['channel_id']

    resp = requests.get(config.url + 'channels/listall/v2', params={
        'token': token_one,
    })
    assert json.loads(resp.text) == {
        'channels': [
            {
                'channel_id': c_id1, 
                'name': 'My Channel'
            },
            {
                'channel_id': c_id2, 
                'name': 'My Channel2'
            },
            {
                'channel_id': c_id3, 
                'name': 'My Channel3'
            },
        ]
    }
#test if channel list all correctly lists multiple channels from different users
def test_channels_list_three_channel_different_users_created(channels_fixture): 
    token_one = channels_fixture[0]
    token_two = channels_fixture[1]
    token_three = channels_fixture[2]

    c_id1 = channels_fixture[3]

    c_id2 = requests.post(config.url + 'channels/create/v2', json={
        'token': token_two,
        'name': 'My Channel2', 
        'is_public': True
    }).json()['channel_id']

    c_id3 = requests.post(config.url + 'channels/create/v2', json={
        'token': token_three,
        'name': 'My Channel3', 
        'is_public': True
    }).json()['channel_id']

    list_one = requests.get(config.url + 'channels/list/v2', params={
        'token': token_one,
    })
    assert json.loads(list_one.text) == {
        'channels': [
            {
                'channel_id': c_id1,
                'name': 'My Channel'
            }
        ]
    }
    list_two = requests.get(config.url + 'channels/list/v2', params={
        'token': token_two,
    })
    assert json.loads(list_two.text) == {
        'channels': [
            {
                'channel_id': c_id2,
                'name': 'My Channel2'
            }
        ]
    }
    list_three = requests.get(config.url + 'channels/list/v2', params={
        'token': token_three,
    })
    assert json.loads(list_three.text) == {
        'channels': [
            {
                'channel_id': c_id3,
                'name': 'My Channel3'
            }
        ]
    }


    resp = requests.get(config.url + 'channels/listall/v2', params={
        'token': token_one,
    })
    assert json.loads(resp.text) == {
        'channels': [
            {
                'channel_id': c_id1, 
                'name': 'My Channel'
            },
            {
                'channel_id': c_id2, 
                'name': 'My Channel2'
            },
            {
                'channel_id': c_id3, 
                'name': 'My Channel3'
            },
        ]
    }

#test if global owner successfully joins a priv channel
def test_global_owner_joining_priv(channels_fixture):
    token1 = channels_fixture[0]
    token2 = channels_fixture[1]
    c_id = requests.post(config.url + 'channels/create/v2', json={
        'token': token2,
        'name': 'My Private Channel', 
        'is_public': False
    }).json()['channel_id']
    requests.post(config.url + 'channel/join/v2', json={
        'token': token1,
        'channel_id': c_id
        })
    resp = requests.get(config.url + 'channels/list/v2', params={
        'token': token1,
    })
    assert json.loads(resp.text) == {
        'channels':[
            {
                'channel_id': channels_fixture[3],
                'name': 'My Channel',
            },
            {
                'channel_id': c_id,
                'name': 'My Private Channel',
            },
        ],
    }
