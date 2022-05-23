import pytest
from src.auth import auth_register_v2, auth_logout_v1
from src.channel import channel_details_v2, channel_messages_v2, channel_join_v2
from src.channels import channels_list_v2, channels_listall_v2, channels_create_v2
from src.other import clear_v1
from src.error import InputError, AccessError
from src.fixture import channels_fixture

#test if channels are different   
def test_channels_create_non_equal(channels_fixture): 
    token1 = channels_fixture[0]
    token2 = channels_fixture[1]
    token3 = channels_fixture[2]
    token4 = channels_fixture[3]
    c_id1 = channels_create_v2(token1,'My Channel', True)
    c_id2 = channels_create_v2(token2,'My Channel', True)
    c_id3 = channels_create_v2(token3,'My Channel', True)
    c_id4 = channels_create_v2(token4,'My Channel', True)
    assert c_id1 != c_id2
    assert c_id1 != c_id3
    assert c_id1 != c_id4
    assert c_id2 != c_id3
    assert c_id2 != c_id4
    assert c_id3 != c_id4

#testing if input error is raised with channel name > 20 characters
def test_channel_name_length(channels_fixture):
    token = channels_fixture[0]
    with pytest.raises(InputError):
        channels_create_v2(token,'Wow this is a really long channel name', True)
    with pytest.raises(InputError):
        channels_create_v2(token,'HUEHUEHUEHEUHEUEHUHUEHEUEHUEHUEHUHUE', True)

#test if a channel is successfully created
def test_single_channels_list_all(channels_fixture):
    token1 = channels_fixture[0]
    channel_id = channels_create_v2(token1,'My Channel', True)
    assert channel_id['channel_id'] == channels_list_v2(token1)['channels'][0]['channel_id']

#test if multiple servers are correctly listed
def test_mutiple_channels_listall(channels_fixture):
    token1 = channels_fixture[0]
    token2 = channels_fixture[1]
    token3 = channels_fixture[2]
    c_id1 = channels_create_v2(token1,'My Channel', True)['channel_id']
    c_id2 = channels_create_v2(token1,'My 2nd Channel', True)['channel_id']
    c_id3 = channels_create_v2(token1,'My 3rd Channel', True)['channel_id']
    c_id4 = channels_create_v2(token2,'4th Channel', True)['channel_id']
    c_id5 = channels_create_v2(token3,'5th Channel', True)['channel_id']

    multiple_channels_listall_1 = channels_listall_v2(token1)
    multiple_channels_listall_2 = channels_listall_v2(token2)
    multiple_channels_listall_3 = channels_listall_v2(token3)

    assert multiple_channels_listall_1 == multiple_channels_listall_2
    assert multiple_channels_listall_2 == multiple_channels_listall_3

    assert channels_listall_v2(token1) == {
        'channels': [
        	{
        		'channel_id': c_id1,
        		'name': 'My Channel',
        	},
            {
        		'channel_id': c_id2,
        		'name': 'My 2nd Channel',
        	},
            {
        		'channel_id': c_id3,
        		'name': 'My 3rd Channel',
        	},
            {
        		'channel_id': c_id4,
        		'name': '4th Channel',
        	},
            {
        		'channel_id': c_id5,
        		'name': '5th Channel',
        	},
        ],
    }

#test if a user in multiple channels is listed 
def test_mutiple_channels_list(channels_fixture):
    token = channels_fixture[0]
    c_id1 = channels_create_v2(token,'My Channel', True)['channel_id']
    c_id2 = channels_create_v2(token,'My 2nd Channel', True)['channel_id']
    c_id3 = channels_create_v2(token,'My 3rd Channel', True)['channel_id']
    assert channels_list_v2(token) == {
        'channels': [
        	{
        		'channel_id': c_id1,
        		'name': 'My Channel',
        	},
            {
        		'channel_id': c_id2,
        		'name': 'My 2nd Channel',
        	},
            {
        		'channel_id': c_id3,
        		'name': 'My 3rd Channel',
        	},
        ],
    }

#test if global owner successfully joins a priv channel
def test_global_owner_joining_priv(channels_fixture):
    token1 = channels_fixture[0]
    token2 = channels_fixture[1]
    c_id = channels_create_v2(token2,'My Private Channel', False)['channel_id']
    channel_join_v2(token1,c_id)
    assert channels_list_v2(token1) == {
        'channels':[
            {
                'channel_id': c_id,
                'name': 'My Private Channel',
            },
        ],
    }

#testing for invalid token in channels_create_v2
def test_invalid_token_channels_create(channels_fixture): 
    token = channels_fixture[0]
    auth_logout_v1(token)
    with pytest.raises(AccessError):
        channels_create_v2(token,'My Channel', True)

#testing for invalid token in channels_listall_v2
def test_invalid_token_channels_listall(channels_fixture): 
    token = channels_fixture[0]
    auth_logout_v1(token)
    with pytest.raises(AccessError): 
        channels_listall_v2(token)

#testing for invalid token in channels_list_v2
def test_invalid_token_channels_list(channels_fixture): 
    token = channels_fixture[0]
    auth_logout_v1(token)
    with pytest.raises(AccessError): 
        channels_list_v2(token)