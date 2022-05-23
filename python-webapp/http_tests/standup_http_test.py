import pytest
import json
import random
import time
from datetime import datetime, timedelta
from src import config
import requests
from src.http_fixture import standup_fixture

# testing for invalid token in standup_start_v1 (POST)
def test_invalid_token_standup_start_http(standup_fixture): 
    token = standup_fixture[0]
    c_id = standup_fixture[3]
    length = 1
    requests.post(config.url + "auth/logout/v1", json={
        'token':token,
    })
    assert requests.post(config.url + "standup/start/v1", json={
        'token':token,
        'channel_id':c_id,
        'length': length,
    }).status_code == 403

#testing for invalid token in standup_active_v1 (GET)
def test_invalid_token_standup_active_http(standup_fixture):
    token = standup_fixture[0]
    c_id = standup_fixture[3]
    length = 1
    requests.post(config.url + "standup/start/v1", json={
        'token':token,
        'channel_id':c_id,
        'length': length,
    })
    time.sleep(length)
    requests.post(config.url + "auth/logout/v1", json={
        'token':token,
    })
    assert requests.get(config.url + "standup/active/v1", params={
        'token': token,
        'channel_id': c_id,
    }).status_code == 403

#testing for invalid token in standup_send_v1 (POST)
def test_invalid_token_standup_send_http(standup_fixture):
    token = standup_fixture[0]
    c_id = standup_fixture[3]
    length = 1
    
    requests.post(config.url + "standup/start/v1", json={
        'token':token,
        'channel_id':c_id,
        'length': length,
    })
    time.sleep(length)
    requests.post(config.url + "auth/logout/v1", json={
        'token':token,
    })

    assert requests.post(config.url + "standup/send/v1", json={
        'token':token,
        'channel_id':c_id,
        'message':'Hello',
    }).status_code == 403


def test_invalid_channel_id_http(standup_fixture):
    token = standup_fixture[0]
    c_id = standup_fixture[3]

    invalid_c_id = random.randint(0, 10)
    while invalid_c_id == c_id:
        invalid_c_id = random.randint(0, 10)

    length = 1
    assert requests.post(config.url + "standup/start/v1", json={
        'token':token,
        'channel_id':invalid_c_id,
        'length': length,
    }).status_code == 400

    assert requests.get(config.url + "standup/active/v1", params={
        'token':token,
        'channel_id': invalid_c_id,
    }).status_code == 400

    assert requests.post(config.url + "standup/send/v1", json={
        'token':token,
        'channel_id':invalid_c_id,
        'message':'Hello',
    }).status_code == 400

def test_already_active_standup_http(standup_fixture):
    token = standup_fixture[0]
    c_id = standup_fixture[3]
    length = 1
    requests.post(config.url + "standup/start/v1", json={
        'token':token,
        'channel_id':c_id,
        'length': length,
    })
    assert requests.post(config.url + "standup/start/v1", json={
        'token':token,
        'channel_id':c_id,
        'length': 3,
    }).status_code == 400
    time.sleep(length)

def test_not_active_standup_http(standup_fixture):
    token = standup_fixture[0]
    c_id = standup_fixture[3]

    assert requests.post(config.url + "standup/send/v1", json={
        'token':token,
        'channel_id':c_id,
        'message':'Hello',
    }).status_code == 400

def test_message_length_http(standup_fixture):  
    token = standup_fixture[0]
    c_id = standup_fixture[3]
    length = 1
    requests.post(config.url + "standup/start/v1", json={
        'token':token,
        'channel_id':c_id,
        'length': length,
    })
    time.sleep(length)
    assert requests.post(config.url + "standup/send/v1", json={
        'token':token,
        'channel_id':c_id,
        'message':'L' * 1001,
    }).status_code == 400

def test_unauthorised_user_http(standup_fixture):
    token = standup_fixture[0]
    c_id = standup_fixture[3]
    token_two = standup_fixture[1]
    length = 1
    assert requests.post(config.url + "standup/start/v1", json={
        'token':token_two,
        'channel_id':c_id,
        'length': length,
    }).status_code == 403

    requests.post(config.url + "standup/start/v1", json={
        'token':token,
        'channel_id':c_id,
        'length': length,
    })
    time.sleep(length)
    assert requests.post(config.url + "standup/send/v1", json={
        'token':token_two,
        'channel_id':c_id,
        'message':'hello',
    }).status_code == 403

def test_standup_inactive_no_standup_started_http(standup_fixture):
    token = standup_fixture[0]
    c_id = standup_fixture[3]

    output = {
        'is_active': False,
        'time_finish': None,
    }

    response = requests.get(config.url + "standup/active/v1", params={
        'token':token,
        'channel_id': c_id,
    }) 
    
    assert json.loads(response.text) == output

def test_standup_active_standup_started_http(standup_fixture):
    token = standup_fixture[0]
    c_id = standup_fixture[3]
    length = 1
    time_finish = requests.post(config.url + "standup/start/v1", json={
        'token':token,
        'channel_id':c_id,
        'length': length,
    }).json()['time_finish']
    output = {
        'is_active': True,
        'time_finish': time_finish,
    }

    response = requests.get(config.url + "standup/active/v1", params={
        'token':token,
        'channel_id': c_id,
    }) 

    assert json.loads(response.text) == output

def test_standup_start_functional_http(standup_fixture): 
    token = standup_fixture[0]
    c_id = standup_fixture[3]
    length = 1
    time_finish = (datetime.now() + timedelta(seconds=length)).strftime("%H:%M:%S")
    output = {'time_finish': time_finish}
    response = requests.post(config.url + "standup/start/v1", json={
        'token':token,
        'channel_id':c_id,
        'length': 1,
    })
    assert json.loads(response.text) == output
    time.sleep(length)

def test_standup_send_after_standup_is_over_http(standup_fixture):
    token = standup_fixture[0]
    c_id = standup_fixture[3]
    length = 1
    requests.post(config.url + "standup/start/v1", json={
        'token':token,
        'channel_id':c_id,
        'length': length,
    })
    time.sleep(length)

    assert requests.post(config.url + "standup/send/v1", json={
        'token':token,
        'channel_id':c_id,
        'message':'hello',
    }).status_code == 400

def test_standup_send_functional(standup_fixture):
    token = standup_fixture[0]
    length = 1
    c_id = standup_fixture[3]
    requests.post(config.url + "standup/start/v1", json={
        'token':token,
        'channel_id':c_id,
        'length': length,
    })
    
    requests.post(config.url + "standup/send/v1", json={
        'token':token,
        'channel_id':c_id,
        'message':"Let's begin this standup",
    })
    requests.post(config.url + "standup/send/v1", json={
        'token':token,
        'channel_id':c_id,
        'message':"It has begun",
    })
    time.sleep(length)

    data = 'henrylei' + ': ' + "Let's begin this standup" + '\n' + 'henrylei' + ': ' + "It has begun" + '\n'

    info = requests.get(config.url + "channel/messages/v2", params={"token": token, "channel_id": c_id, "start": 0})
    assert json.loads(info.text)['messages'][0]['message'] == data
    
def test_standup_send_functional_message_send(standup_fixture):
    token = standup_fixture[0]
    length = 1
    c_id = standup_fixture[3]
    requests.post(config.url + "standup/start/v1", json={
        'token':token,
        'channel_id':c_id,
        'length': length,
    })
    
    requests.post(config.url + 'message/send/v2', json={
        'token':token,
        'channel_id':c_id,
        'message':"Let's begin this standup",
    })
    requests.post(config.url + 'message/send/v2', json={
        'token':token,
        'channel_id':c_id,
        'message':"It has begun",
    })
    time.sleep(length)

    data = 'henrylei' + ': ' + "Let's begin this standup" + '\n' + 'henrylei' + ': ' + "It has begun" + '\n'

    info = requests.get(config.url + "channel/messages/v2", params={"token": token, "channel_id": c_id, "start": 0})
    assert json.loads(info.text)['messages'][0]['message'] == data
