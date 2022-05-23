from src.error import InputError, AccessError
from src.data import load_data, get_data, save, channel_template, SECRET
from src.message import message_send_v2
import jwt
import time, sched
import threading
from datetime import datetime, timedelta, timezone


def standup_start_v1(token, channel_id, length):
    '''
    Takes a token, channel id and length to start a standup

    Arguments:
        token (string)    - token of the authorised user
        channel_id (int)  - id of the channel
        length (int)      - length of the standup
        ...

    Exceptions:
        AccessError  - Occurs when token is invalid
        AccessError  - Occurs when the user is not in the channel
        InputError   - Occurs when the channel ID is invalid
        InputError   - Occurs when a standup is already running in the channel

    Return Value:
        Returns the time that standup finishes (in a dictionary)
    '''
    load_data()
    data = get_data()
    auth_user_id = jwt.decode(token, SECRET, algorithms=['HS256'])['auth_user_id']

    #checks if id from token is valid
    if token_valid(token, data) == False:
        raise AccessError("Invalid token")

    #checks if channel_id is valid
    if valid_channel_id(channel_id, data) == False:
        raise InputError('Channel ID is not a valid channel')

    #checks if a user is part of the channel
    if in_channel(auth_user_id, channel_id, data) == False:
        raise AccessError('Authorised user is not in the channel')

    #checks if a standup is active
    if is_standup_active(channel_id, data) == True:
        raise InputError('An active standup is currently running in this channel')

    time_finish = (datetime.now() + timedelta(seconds=length)).strftime("%H:%M:%S")

    #sets values to standup finish
    for index in range(len(data['channels'])):
        if data['channels'][index]['channel_id'] == channel_id:
            data['channels'][index]['is_active'] = True
            data['channels'][index]['time_finish'] = time_finish

    #starts timer for when standup finishes
    timer = threading.Timer(length, startup_end, [channel_id, token])
    timer.start()
    save()
    return {'time_finish': time_finish}

def standup_active_v1(token, channel_id):
    '''
    Takes a token and channel id to indicate whether a standup is active and when it finishes

    Arguments:
        token (string)    - token of the authorised user
        channel_id (int)  - id of the channel
        ...

    Exceptions:
        AccessError  - Occurs when token is invalid
        InputError   - Occurs when the channel ID is invalid

    Return Value:
        Returns whether a standup is active and when it finishes (in a dictionary)
    '''
    load_data()
    data = get_data()

    #checks if channel_id is valid
    if valid_channel_id(channel_id, data) == False:
        raise InputError('Channel ID is not a valid channel')
    
    # AccessError if the token is invalid
    if token_valid(token, data) == False:
        raise AccessError("Invalid token")
    
    #gets data to see if active or not
    for index in range(len(data['channels'])):
        if data['channels'][index]['channel_id'] == channel_id:
            is_active = data['channels'][index]['is_active']
            time_finish = data['channels'][index]['time_finish']

    save()    
    return {'is_active': is_active, 'time_finish': time_finish}

def standup_send_v1(token, channel_id, message):
    '''
    Takes a token, channel id and message to send a message in a standup queue

    Arguments:
        token (string)    - token of the authorised user
        channel_id (int)  - id of the channel
        message (string)  - the message being sent
        ...

    Exceptions:
        AccessError  - Occurs when token is invalid
        AccessError  - Occurs when the user is not in the channel
        InputError   - Occurs when the channel ID is invalid
        InputError   - Occurs when a standup is not currently running in the channel
        InputError   - Occurs when the mesasge is more than 1000 characters

    Return Value:
        Returns an empty dictionary
    '''
    load_data()
    data = get_data()
    auth_user_id = jwt.decode(token, SECRET, algorithms=['HS256'])['auth_user_id']

    #checks if id from token is valid
    if token_valid(token, data) == False:
        raise AccessError("Invalid token")

    #checks if channel_id is valid
    if valid_channel_id(channel_id, data) == False:
        raise InputError('Channel ID is not a valid channel')

    #checks if user is a member of the channel
    if in_channel(auth_user_id, channel_id, data) == False:
        raise AccessError('Authorised user is not in the channel')

    #checks if message length is less than 1000 characters
    if len(message) > 1000:
        raise InputError('Message is more than 1000 characters')

    #checks if standup is active
    if is_standup_active(channel_id, data) == False:
        raise InputError('An active standup is not currently running in this channel')

    #finds the handle of user
    handle = handle_finder(auth_user_id, data)
    standup_message = f'{handle}: ' + message

    #saves the message to be sent later
    for index in range(len(data['channels'])):
        if data['channels'][index]['channel_id'] == channel_id:
            data['channels'][index]['standup_messages'].append(standup_message)

    save()
    return {}

#function called when standup finishes to send final message
def startup_end(channel_id, token):
    load_data()
    data = get_data()
    output = ''
    #concatenates all the messages into one message
    for index in range(len(data['channels'])):
        if data['channels'][index]['channel_id'] == channel_id: 
            for message in data['channels'][index]['standup_messages']:
                output += message + '\n'
            data['channels'][index]['is_active'] = False
            data['channels'][index]['time_finish'] = None
            data['channels'][index]['standup_messages'].clear()
    save()
    message_send_v2(token, channel_id, output)
    return

# Helper function that returns the index when it finds the valid channel
# If not, return false
def valid_channel_id(channel_id, data):
    for index in range(len(data['channels'])):
        if data['channels'][index]['channel_id'] == channel_id: 
            return True
    return False

#checks if id from token is valid
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

#checks if a standup is active
def is_standup_active(channel_id, data):
    for index in range(len(data['channels'])):
        if data['channels'][index]['channel_id'] == channel_id:
            return data['channels'][index]['is_active']

#checks if a user is part of a channel
def in_channel(auth_user_id, channel_id, data):
    for index in range(len(data['channels'])):
        if data['channels'][index]['channel_id'] == channel_id:
            if auth_user_id in data['channels'][index]['members_id']: 
                return True
    return False

#finds the handle of a user
def handle_finder(auth_user_id, data):
    for index in range(len(data['users'])):
        if auth_user_id == data['users'][index]['auth_user_id']:
            return data['users'][index]['handle_str']