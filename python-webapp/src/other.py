from src.error import InputError, AccessError
from src.data import SECRET, load_data, get_data, save
import jwt

def clear_v1():
    '''
    Clears all dictionaries within the lists in data
    Arguments:
        None

    Exceptions:
        None
   
    Return Value:
        None

    '''
    load_data()
    data = get_data()

    data['users'].clear()
    data['channels'].clear()
    data['messages'].clear()
    data['dms'].clear()
    data['deleted_users'].clear()
    data['notifications'].clear()
    data['user_analytics'].clear()
    data['server_analytics']['channels'].clear()
    data['server_analytics']['dms'].clear()
    data['server_analytics']['messages'].clear()


    save()

def search_v1(token, query_str):
    '''
    Given a query string, return a collection of messages in all 
    of the channels/DMs that the user has joined that match the query
    Arguments:
        token        (string)    - token of the authorised user
        query_str    (string)    - string of what is being searched

    Exceptions:
        InputError   - Occurs when query_str is above 1000 characters
        AccessError  - Occurs when the token passed in is not a valid id
   
    Return Value:
        messages that contain the query string in a dictionary containing message_id, u_id, message, time_created 

    '''
    load_data()
    data = get_data()

    decoded_token = (jwt.decode(token, SECRET, algorithms=['HS256']))
    
    #checks for len of query str
    if len(query_str) > 1000:
        raise InputError("Query_str is longer than 1000 characters")
    
    u_id = decoded_token['auth_user_id']

    #checks if id from token is valid
    if token_valid(token, data) == False:
        raise AccessError("Invalid token")

    channel_list = []
    dm_list = []
    output = []

    #finds channels and dms the user has joined
    for index in range(len(data['channels'])):
        if u_id in data['channels'][index]['members_id']:
            channel_list.append(data['channels'][index]['channel_id'])

    for index in range(len(data['dms'])):
        if u_id in data['dms'][index]['members_id']:
            dm_list.append(data['dms'][index]['dm_id'])

    #searches those channels and dms for messages that contain the query string
    for index in range(len(data['messages'])):
        for x in channel_list:
            if data['messages'][index]['channel_id'] == x or data['messages'][index]['dm_id'] == x:
                if query_str in data['messages'][index]['message']:
                    print(data['messages'][index])
                    message_template = {
                                        'message_id': data['messages'][index]['message_id'],
                                        'u_id': data['messages'][index]['user_id'],
                                        'message': data['messages'][index]['message'],
                                        'time_created': data['messages'][index]['time_created'],
                                        'reacts': data['messages'][index]['reacts'],
                                        'is_pinned': data['messages'][index]['is_pinned'],
                                        }
                    output.append(message_template)

    return {
        'messages': output
    }

def admin_user_permission_change_v1(token, u_id, permission_id):
    '''
    Given a User by their user ID, set their permissions to new permissions described by permission_id
    Arguments:
        token           (string)    - token of the authorised user
        u_id            (int)       - id of the user
        permission_id   (int)       - new permission id

    Exceptions:
        InputError   - Occurs when u_id does not refer to a valid user
        InputError   - Occurs when permission_id does not refer to a value permission
        AccessError  - Occurs when the authorised user is not an owner
        AccessError  - Occurs when the token passed in is not a valid id

    Return Value:
        None

    '''
    load_data()
    data = get_data()

    valid_permission_id = [1,2]
    
    decoded_token = (jwt.decode(token, SECRET, algorithms=['HS256']))

    #checks if id from token is valid
    if token_valid(token, data) == False:
        raise AccessError("Invalid token")

    #checks validty of u_id
    if invalid_u_id(u_id, data) == False:
        raise InputError("Invalid user id")

    #checks if permission id is valid
    if permission_id not in valid_permission_id:
        raise InputError("Invalid permission id")

    #checks if authorised user is an owner
    if token_is_owner(decoded_token, data) == False:
        raise AccessError("Authorised user is not an owner")

    #changes permission id
    for index in range(len(data['users'])):
        if data['users'][index]['auth_user_id'] == u_id:
            data['users'][index]['permission_id'] = permission_id
    
    save()

def admin_user_remove_v1(token, u_id):
    '''
    Given a User by their user ID, remove them from Dreamss
        token           (string)    - token of the authorised user
        u_id            (int)       - id of the user

    Exceptions:
        InputError   - Occurs when u_id does not refer to a valid user
        InputError   - Occurs when the user is currently the only owner
        AccessError  - Occurs when the authorised user is not an owner
        AccessError  - Occurs when the token passed in is not a valid id

    Return Value:
        None

    '''
    load_data()
    data = get_data()

    decoded_token = (jwt.decode(token, SECRET, algorithms=['HS256']))

    #checks if id from token is valid
    if token_valid(token, data) == False:
        raise AccessError("Invalid token")

    #checks if authorised user is an owner
    if token_is_owner(decoded_token, data) == False:
        raise AccessError("Authorised user is not an owner")

    #checks if the user removed is currently the only owner
    if user_is_only_owner(u_id, data) == True:
        raise InputError("User is the only owner")
    
    #checks if u id is valid
    if invalid_u_id(u_id, data) == False:
        raise InputError("Invalid user id")

    #removes the user and changes their name to removed user
    for index in range(len(data['users'])):
        if data['users'][index]['auth_user_id'] == u_id:
            data['users'][index]['name_first'] = 'Removed'
            data['users'][index]['name_last'] = 'user'
            data['deleted_users'].append(data['users'][index])
            data['users'].remove(data['users'][index])
            break
    
    #changes all their messages to Removed user
    for index in range(len(data['messages'])):
        if data['messages'][index]['user_id'] == u_id:
            print(data['messages'][index]['message'])
            data['messages'][index]['message'] = 'Removed user'
            print(data['messages'][index]['message'])
    
    #changes all their channel messages to Removed user
    for index in range(len(data['channels'])):
        for x in range(len(data['channels'][index]['messages'])):
            if data['channels'][index]['messages'][x]['user_id'] == u_id:
                data['channels'][index]['messages'][x]['message'] = 'Removed user'

    #changes all their dms to Removed user
    for index in range(len(data['dms'])):
        for x in range(len(data['dms'][index]['messages'])):
            if data['dms'][index]['messages'][x]['user_id'] == u_id:
                data['dmss'][index]['messages'][x]['message'] = 'Removed user'
    
    save()

def notifications_get_v1(token):
    '''
    Return the user's most recent 20 notifications    
    Arguments:
        token           (string)    - token of the authorised user

    Exceptions:
        None

    Return Value:
        None

    '''
    load_data()
    data = get_data()

    output = []

    decoded_token = (jwt.decode(token, SECRET, algorithms=['HS256']))
    #checks if id from token is valid
    if token_valid(token, data) == False:
        raise AccessError("Invalid token")

    u_id = decoded_token['auth_user_id']
    
    for index in range(len(data['notifications'])):
        if u_id in data['notifications'][index]['user_id']:
            notif = {'channel_id': data['notifications'][index]['channel_id'],
                    'dm_id': data['notifications'][index]['dm_id'],
                    'notification_message': data['notifications'][index]['message'],
            }

            output.insert(0, notif)
    output = output[:20]
    return {'notifications': output}

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

#checks if u_id is valid
def invalid_u_id(u_id, data):
    #loops through users checking u_id
    for index in range(len(data['users'])):
        if data['users'][index]['auth_user_id'] == u_id:
            return True
    return False

#checks if token is owner
def token_is_owner(token, data):
    u_id = token['auth_user_id']
    #loops through users checking u_id
    for index in range(len(data['users'])):
        if data['users'][index]['auth_user_id'] == u_id:
            if data['users'][index]['permission_id'] == 1:
                return True
    return False

#checks if user is the only owner
def user_is_only_owner(u_id, data):
    total_owners = 0
    id_owner = False
    for index in range(len(data['users'])):
        if data['users'][index]['permission_id'] == 1:
            total_owners += 1
            if data['users'][index]['auth_user_id'] == u_id:
                id_owner = True

    if total_owners == 1 and id_owner == True:
        return True
    
    else:
        return False
