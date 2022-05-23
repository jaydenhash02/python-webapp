from src.error import InputError, AccessError
from json import loads, dumps
from src.data import user_template, SECRET, load_data, get_data, save, channel_template
import time
import jwt

# channels/list/v2
def channels_list_v2(token):
    '''
    Takes an user's token and provides a list of channels that user is a member of

    Arguments:
        token (string) - token of the user that the list of channels belongs to

    Exceptions:
        AccessError  - Occurs when the token passed in is not a valid id

    Return Value:
        Returns a dictionary containing the information of the channels the user is a member of
    '''
    
    #creates a dictionary for the list of channels
    channels_list = {
        'channels': [],
    }

    # retrieve data from data.json file
    load_data()
    data = get_data()

    #decode token to get the payload
    decoded_instance = jwt.decode(token, SECRET, algorithms=['HS256'])
    auth_user_id = decoded_instance['auth_user_id']

    #checks if id from token is valid
    if token_valid(token, data) == False:
        raise AccessError("Invalid token")


    #loops through the data and channels
    for index in range(len(data['channels'])):
        for member in data['channels'][index]['members_id']:
            #if the auth_user_id is a member of the channel
            #creates a new dictionary with the information of the channel and adds it to the list
            if member == auth_user_id:
                channel_id = data['channels'][index]['channel_id']
                name = data['channels'][index]['name']
                user_channel = {
                    'channel_id': channel_id,
                    'name': name,
                }
                channels_list['channels'].append(user_channel)
                
    # save the data after updating json file
    save()

    #returns the list of channels
    return channels_list


# channels/listall/v2
def channels_listall_v2(token):
    '''
    Provides a list of every channel 

    Arguments:
        token(string)       - token of the user (it doesn't matter whose token to use as it provides info
                              on all channels)

    Exceptions:
        AccessError  - Occurs when the token passed in is not a valid id

    Return Value:
        Returns a dictionary containing the information of every channel
    '''
    # retrieve data from json file
    load_data()
    data = get_data()

    #checks if id from token is valid
    if token_valid(token, data) == False:
        raise AccessError("Invalid token")
    #creates a dictionary for the list of channels
    channels_list = {
        'channels': [],
    }

    #decode 
    jwt.decode(token, SECRET, algorithms=['HS256'])
    
    #loops through the data and channels
    for index in range(len(data['channels'])):
        #creates a new dictionary with the information of every channel and adds it to the list
        channel_id = data['channels'][index]['channel_id']
        name = data['channels'][index]['name']
        
        user_channel = {
            'channel_id': channel_id,
            'name': name,
        }
        channels_list['channels'].append(user_channel)

    # saves the data to the json file
    save()

    #returns the list of channels
    return channels_list


# channels/create/v2
def channels_create_v2(token, name, is_public):
    '''
    Takes inputs and creates a new channel storing them in the data. 
    Creates a channel_id and returns it.

    Arguments:
        token (string)          - token of user creating channel
        name (string)           - name of channel created
        is_public (boolean)     - permission of channel, whether it is public or private

    Exceptions:
        InputError  - Occurs when name entered is longer than 20 characters
        AccessError - Occurs when the token passed in is not a valid id


    Return Value:
        Returns channel_id of new channel if successfully registered
    '''
    # use data from json file
    load_data()
    data = get_data()

    #decode 
    decoded_instance = jwt.decode(token, SECRET, algorithms=['HS256'])
    auth_user_id = decoded_instance['auth_user_id']

    #checks if id from token is valid
    if token_valid(token, data) == False:
        raise AccessError("Invalid token")

    #checks if length of name is less than 20 characters
    if len(name) > 20:
        raise InputError("Name is longer than 20 characters")
    
    #creates a channel id
    total_channels = len(data['channels']) + 1

    #checks is channel is public or private
    if is_public == True:
        private = False
    else:
        private = True

    #changes the values in the template to the inputs  
    channel_template.update({'channel_id': total_channels})
    channel_template.update({'name': name})
    channel_template.update({'owners_id': [auth_user_id]})
    channel_template.update({'members_id': [auth_user_id]})
    channel_template.update({'private': private})
    channel_template.update({'standup_messages': []})
    channel_template.update({'is_active': False})
    channel_template.update({'time_finish': None})

    #appends the dictionary to the list of channels
    dictionary_copy = channel_template.copy()
    data['channels'].append(dictionary_copy)

    analytic_user(auth_user_id, data)
    analytic_server(data)

    # saves data on data.json file
    save()

    #returns the channel id
    return {'channel_id': total_channels} 

#checks if token is valid
def token_valid(token, data):
    decoded_token = jwt.decode(token, SECRET, algorithms=['HS256'])
    valid_auth_id = False
    valid_session_id = False
    session_id = decoded_token['session_id']
    auth_id = decoded_token['auth_user_id']

    for index in range(len(data['users'])):
        for x in data['users'][index]['session_id']:
            if x == session_id:
                valid_session_id = True

    for index in range(len(data['users'])):
        if data['users'][index]['auth_user_id'] == auth_id:
            valid_auth_id = True

    if (valid_auth_id == True) and (valid_session_id == True):
        return True
    else:
        return False

#changes user analytics whenever a user joins a channel
def analytic_user(u_id, data):
    time_stamp = int(time.time())
    for index in range(len(data['user_analytics'])):
        if u_id == data['user_analytics'][index]['user_id']:
            data['user_analytics'][index]['channels'].append({'num_channels_joined': total_user_channels(u_id, data), 'time_stamp': time_stamp})

#finds total amount of channels a user is in
def total_user_channels(u_id, data):
    total = 0
    for index in range(len(data['channels'])):
        if u_id in data['channels'][index]['members_id']:
            total += 1
    return total

#changes server analytics whenever a server is made
def analytic_server(data):
    time_stamp = int(time.time())
    data['server_analytics']['channels'].append({'num_channels_exist': len(data['channels']), 'time_stamp': time_stamp})