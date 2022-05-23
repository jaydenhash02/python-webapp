from src.error import InputError, AccessError
from json import loads, dumps
from src.data import user_template, SECRET, load_data, get_data, save, dms_template
from src.user import user_profile_v2
import jwt
import time, sched

def dm_details_v1(token, dm_id):
    '''
    Takes the token and dm id to provide basic details about the dm

    Arguments:
        token           (int)    - token of the authorised user
        dm_id           (int)    - id of the dm

    Exceptions:
        InputError   - Occurs when dm_id does not refer to a valid dm
        AccessError  - Occurs when authorised user is not a member of the dm
        AccessError  - Occurs when the token passed in is not a valid id

    Return Value:
        Returns name and members as a dictionary
    '''
    # use data from json file
    load_data()
    data = get_data()
    
    #get uid
    u_id = jwt.decode(token, SECRET, algorithms=['HS256'])['auth_user_id']

    # InputError when dm id is not a valid id
    dm_index = valid_dm_id(dm_id, data)

    #raise inputerror if dm id is invalid
    if dm_index == -1:
        raise InputError("Invalid dm id")

    # AccessError when the authorised user is not already a member of the dm
    if member_of_dm(dm_index, u_id, data) == False: 
        raise AccessError("The authorised user is not a member of the dm")
    
    # raise access error if token is invalid
    if token_valid(token, data) == False:
        raise AccessError("The token is invalid")

    # initialize dm name
    dm_name = data['dms'][dm_index]['name'] 
    
    #initialize member template
    memberTemplate = {}

    # Making output dictionary name, members
    output = {
        'name': dm_name,
        'members': []
    }

    # loop through data and find a match for member id
    for index in range(len(data['dms'][dm_index]['members_id'])):
        memberId = data['dms'][dm_index]['members_id'][index]
        # loop through and update member information
        for index in range(len(data['users'])):
            if data['users'][index]['auth_user_id'] == memberId:
                email = data['users'][index]['email']
                firstName = data['users'][index]['name_first']
                lastName = data['users'][index]['name_last']
                handleStr = data['users'][index]['handle_str']
                profile_img_url = data['users'][index]['profile_img_url']
                memberTemplate.update({'u_id': memberId})
                memberTemplate.update({'email': email})
                memberTemplate.update({'name_first': firstName})
                memberTemplate.update({'name_last': lastName})
                memberTemplate.update({'handle_str': handleStr})
                memberTemplate.update({'profile_img_url': profile_img_url})
                copy = memberTemplate.copy()
                output['members'].append(copy)
    return output

def dm_list_v1(token):
    '''
    Takes an user's token and provides a list of dms that user is a member of

    Arguments:
        token (string) - token of the user that the list of dms belongs to

    Exceptions:
        AccessError  - Occurs when the token passed in is not a valid id

    Return Value:
        Returns a dictionary containing the information of the dms the user is a member of
    '''
    #creates a dictionary for the list of dms
    dm_list = []

    # retrieve data from data.json file
    load_data()
    data = get_data()

    #decode token to get the payload
    decoded_instance = jwt.decode(token, SECRET, algorithms=['HS256'])
    auth_user_id = decoded_instance['auth_user_id']

    #loops through the data and dms
    for index in range(len(data['dms'])):
        for member in data['dms'][index]['members_id']:
            #if the auth_user_id is a member of the dm
            #creates a new dictionary with the information of the dm and adds it to the list
            if auth_user_id == member:
                dm_dict = {}
                dm_id = data['dms'][index]['dm_id']
                name = data['dms'][index]['name']
                dm_dict.update({'dm_id': dm_id})
                dm_dict.update({'name': name})
                dm_list.append(dm_dict)
                break
    
    # save the data after updating json file
    save()
    #returns the list of dms
    return {'dms':dm_list}

def dm_create_v1(token, u_ids):
    '''
    Takes inputs and creates a new dm storing them in the data. 
    Creates a dm_id and returns it.

    Arguments:
        token (string)          - token of user creating dm
        u_ids (string)          - ids of users being invited

    Exceptions:
        InputError  - Occurs when uid does not refer to a valid user
        AccessError - Occurs when the token passed in is not a valid id

    Return Value:
        Returns dictionary with dm_id and dm_name
    '''
    # use data from json file
    load_data()
    data = get_data()

    #decode 
    decoded_instance = jwt.decode(token, SECRET, algorithms=['HS256'])
    auth_user_id = decoded_instance['auth_user_id']

    
    #creates a dm id
    if len(data['dms']) == 0:
        dm_id = 1
    else:
        dm_id = data['dms'][-1]['dm_id'] + 1
    
    #name is a list of handle strings
    name = []
    
    # loop through uids
    for user in u_ids:
        # raise input error if user id is invalid
        if valid_user_id(user, data) == False:
            raise InputError("Invalid user id")
        # loop through data and append handle string if user id matches
        for index in range(len(data['users'])):
            if data['users'][index]['auth_user_id'] == user:
                name.append(data['users'][index]['handle_str'])

    #loop through and match logged in user 
    for index in range(len(data['users'])):
        if auth_user_id == data['users'][index]['auth_user_id']:
            name.append(data['users'][index]['handle_str'])
    
    name.sort()
        
    notification_dm_create(u_ids, dm_id, auth_user_id, data, name)

    u_ids.insert(0, auth_user_id)
    #changes the values in the template to the inputs  
    dms_template.update({'dm_id': dm_id})
    dms_template.update({'name': name})
    dms_template.update({'owners_id': [auth_user_id]})
    dms_template.update({'members_id': u_ids})

    #appends the dictionary to the list of dms
    dictionary_copy = dms_template.copy()
    data['dms'].append(dictionary_copy)

    analytic_server(data)
    analytic_multiple_user(dm_id, data)
    # saves data on data.json file
    save()
    
    #returns the dm id
    return {'dm_id': dm_id, 'dm_name': name} 

def dm_remove_v1(token, dm_id):
    '''
    Takes inputs and removes an existing DM. This can only be done by the original creator of the DM.

    Arguments:
        token (string)          - token of user removing dm
        dm_id (string)          - id of dm being removed

    Exceptions:
        InputError  - Occurs when dm_id does not refer to a valid dm
        AccessError - Occurs when the user is not the original creator of the DM
        AccessError - Occurs when the token passed in is not a valid id

    Return Value:
        No return value
    '''
    # use data from json file
    load_data()
    data = get_data()
    #decode
    u_id = jwt.decode(token, SECRET, algorithms=['HS256'])['auth_user_id']

    # InputError when dm id is not a valid id
    dm_index = valid_dm_id(dm_id, data)
    if dm_index == -1:
        raise InputError("Invalid dm id")

    # AccessError when user is not the original creator
    if is_owner(dm_index, u_id, data) == False:
        raise AccessError("The user is not the original creator of the DM")

    # remove the dm
    data['dms'].pop(dm_index)

    analytic_server(data)
    analytic_multiple_user(dm_id, data)
    save()
    return {}

def dm_invite_v1(token, dm_id, u_id):
    '''
    Takes the token and dm_id to invite a user with u_id into the dm

    Arguments:
        token           (int)    - token of the authorised user
        dm_id           (int)    - id of the dm
        u_id            (int)    - id of the user being invited

    Exceptions:
        InputError   - Occurs when dm_id does not refer to a valid dm
        InputError   - Occurs when u_id does not refer to a valid user
        AccessError  - Occurs when authorised user is not a member of the dm
        AccessError  - Occurs when the token passed in is not a valid id
   
    Return Value:
        No return value
    '''
    # use data from json file
    load_data()
    data = get_data()
    
    #decode 
    decoded_instance = jwt.decode(token, SECRET, algorithms=['HS256'])
    auth_user_id = decoded_instance['auth_user_id']

    #access error if token is invalid
    if token_valid(token, data) == False:
        raise AccessError("The token is invalid")

    # InputError when u_id does not refer to a valid user
    if valid_user_id(u_id, data) == False:
        raise InputError("Invalid user id")

    # InputError when dm_id does not refer to a valid dm
    dm_index = valid_dm_id(dm_id, data)
    if dm_index == -1:
        raise InputError("Invalid dm id")

    # AccessError when the authorised user is not already a member of the dm
    if member_of_dm(dm_index, auth_user_id, data) == False: 
        raise AccessError("The authorised user is not a member of the dm")
    
    if auth_user_id == u_id:
        return 

    for index in range(len(data['dms'])):
        if dm_id == data['dms'][index]['dm_id']:
            if u_id in data['dms'][index]['members_id']:
                return 

    # Add u_id to dms members_id 
    data['dms'][dm_index]['members_id'].append(u_id)
    notification_dm(u_id, dm_id, auth_user_id, data)
    analytic_user(u_id, data)
    save()
    return {}

def dm_leave_v1(token, dm_id):
    '''
    Takes inputs and removes and leaves an existing DM

    Arguments:
        token (string)          - token of user leaving dm
        dm_id (string)          - id of dm being left

    Exceptions:
        InputError  - Occurs when dm_id does not refer to a valid dm
        AccessError - Occurs when the token is invalid
        AccessError - Occurs when the authorised user is not a member of the dm
        AccessError - Occurs when the token passed in is not a valid id

    Return Value:
        No return value
    '''
    # use data from json file
    load_data()
    data = get_data()
    #decode
    u_id = jwt.decode(token, SECRET, algorithms=['HS256'])['auth_user_id']

    # InputError when dm id is not a valid id
    dm_index = valid_dm_id(dm_id, data)
    if dm_index == -1:
        raise InputError("Invalid dm id")
    # access error if token is invalid
    if token_valid(token, data) == False:
        raise AccessError("The token is invalid")

    # AccessError when the authorised user is not already a member of the dm
    if member_of_dm(dm_index, u_id, data) == False: 
        raise AccessError("The authorised user is not a member of the dm")

    for index in range(len(data['dms'])):
        if dm_id == data['dms'][index]['dm_id']:
            if u_id in data['dms'][index]['members_id']:
                data['dms'][index]['members_id'].remove(u_id)
    
    analytic_user(u_id, data)
    save()
    return {}

def dm_messages_v1(token, dm_id, start):
    '''
    Takes the token, dm id and start value to provide details of the messages in the dm

    Arguments:
        token           (int)    - token of the authorised user
        dm_id           (int)    - id of the dm
        start           (int)    - starting value for indexing

    Exceptions:
        InputError   - Occurs when dm_id does not refer to a valid dm
        InputError   - Occurs when the start value is greater than the total number of messages in the dm
        AccessError  - Occurs when token user is not a member of the dm
        AccessError  - Occurs when the token passed in is not a valid id
   
    Return Value:
        Returns messages, start, end as dictionary
    '''
    # use data from json file
    load_data()
    data = get_data()
    #decode
    u_id = jwt.decode(token, SECRET, algorithms=['HS256'])['auth_user_id']

    # InputError when dm id is not a valid id
    dm_index = valid_dm_id(dm_id, data)
    if dm_index == -1:
        raise InputError("Invalid dm id")

    # InputError when start is greater than the total number of msgs in dm
    if start > len(data['dms'][dm_index]['messages']):
        raise InputError("Not enough messages in the dm")

    # AccessError when the authorised user is not already a member of the dm
    if member_of_dm(dm_index, u_id, data) == False: 
        raise AccessError("The authorised user is not a member of the dm")
    # raise access error if token is invalid
    if token_valid(token, data) == False:
        raise AccessError("The token is invalid")
    # Making output dictionary
    length = len(data['dms'][dm_index]['messages'])
    end = start + 50

    if end > length:
        end = -1
    else:
        length = end

    #initialize message template
    messagesTemplate = {}
    # output dictionary has messages, start, end
    output = {
        'messages': [],
        'start': start,
        'end':end,
    }

    temp = start
    #loop through data and update information 
    for index in range(len(data['dms'][dm_index]['messages'])):
        messageId = data['dms'][dm_index]['messages'][index]['message_id']
        uId = data['dms'][dm_index]['messages'][index]['user_id']
        message = data['dms'][dm_index]['messages'][index]['message']
        timeCreated = data['dms'][dm_index]['messages'][index]['time_created']
        reacts = data['dms'][dm_index]['messages'][index]['reacts']
        is_pinned = data['dms'][dm_index]['messages'][index]['is_pinned']

        is_this_user_reacted = has_user_reacted(u_id, messageId, data)[0]
        is_empty = has_user_reacted(u_id, messageId, data)[1]
        if is_empty == False:
            reacts[0]['is_this_user_reacted'] = is_this_user_reacted 

        messagesTemplate.update({'message_id': messageId})
        messagesTemplate.update({'u_id': uId})
        messagesTemplate.update({'message': message})
        messagesTemplate.update({'time_created': timeCreated})
        messagesTemplate.update({'reacts': reacts})
        messagesTemplate.update({'is_pinned': is_pinned})
        copy = messagesTemplate.copy()
        output['messages'].append(copy)
        temp = temp + 1

        if temp == length:
            break
    
    save()
    return output

def message_senddm_v1(token, dm_id, message):
    '''
    Takes the token, dm id and message to send a message

    Arguments:
        token           (int)    - token of the authorised user
        dm_id           (int)    - id of the dm
        message         (string) - message being sent

    Exceptions:
        InputError   - Occurs when the message is over 1000 characters
        AccessError  - Occurs when token user is not a member of the dm
        AccessError  - Occurs when the token passed in is not a valid id
   
    Return Value:
        Returns a dictionary with message_id
    '''
    #use data
    load_data()
    data = get_data()
    #decode
    u_id = jwt.decode(token, SECRET, algorithms=['HS256'])['auth_user_id']

    dm_index = valid_dm_id(dm_id, data)
    if dm_index == -1:
        raise InputError("Invalid dm id")
    # InputError when message is more than 1000 characters 
    if len(message) > 1000:
        raise InputError("Message is more than 1000 characters")

    # Access error when the authorised user is not a member of the DM
    if is_member(u_id, -1, dm_id, data) == False and is_owner(dm_index, u_id, data) == False: 
        raise AccessError("The authorised user is not a member of the DM they are trying to post to")
    # access error if token is invalid
    if token_valid(token, data) == False:
        raise AccessError("The token is invalid")
    if len(data['messages']) == 0:
        message_id = 1
    else:
        message_id = data['messages'][0]['message_id'] + 1
    # initialize message template
    messagesTemplate = {}
    #get time 
    timestamp = int(time.time())
    #update message information
    messagesTemplate.update({'message_id': message_id})
    messagesTemplate.update({'user_id': u_id}) 
    messagesTemplate.update({'channel_id': None})
    messagesTemplate.update({'dm_id': dm_id})
    messagesTemplate.update({'message': message})
    messagesTemplate.update({'time_created': timestamp})
    messagesTemplate.update({'reacts': [] })
    messagesTemplate.update({'is_pinned': False})
    copy = messagesTemplate.copy()
    data['messages'].insert(0, copy)
    # loop through data and update index if dm id matches
    for index in range(len(data['dms'])):
        if data['dms'][index]['dm_id'] == dm_id:
            dm_index = index
            break

    data['dms'][dm_index]['messages'].insert(0, copy)
    notifications_message(dm_id, message, data, u_id)
    analytic_message_user(timestamp, u_id, data)
    analytic_message_server(timestamp, data)
    save()
    return {'message_id': message_id}

def message_sendlaterdm_v1(token, dm_id, message, time_sent):
    '''
    Takes the token, dm id, message, and a specified time to send the message later

    Arguments:
        token              (int)    - token of the authorised user
        dm_id              (int)    - id of the channel
        message            (string) - message being sent
        time_sent          (int)    - time to send message later

    Exceptions:
        AccessError  - Occurs when auth user is not a member of the dm
        InputError   - Occurs when the dm id is invalid
        InputError   - Occurs when the time sent is in the past
        InputError   - Occurs when the message is more than 1000 characters
   
    Return Value:
        Returns a dictionary with message id
    '''
    load_data()
    data = get_data()

    u_id = jwt.decode(token, SECRET, algorithms=['HS256'])['auth_user_id']

    # InputError when dm id is not a valid id
    dm_index = valid_dm_id(dm_id, data)
    if dm_index == -1:
        raise InputError("Invalid dm id")

    # InputError when message is more than 1000 characters 
    if len(message) > 1000:
        raise InputError("Message is more than 1000 characters")

    timestamp = int(time.time())
    time_diff = time_sent - timestamp

    # InputError when time sent is a time in the past
    if time_diff < 0:
        raise InputError("Time_sent is a time in the past")

    # AccessError when the authorised user is not a member of the channel
    if member_of_dm(dm_index, u_id, data) == False:
        raise AccessError("Authorised user is not a member of the dm")

    scheduler = sched.scheduler(time.time, time.sleep)
    scheduler.enter(time_diff, 1, send_msg_later_helper, (token, dm_id, message))
    scheduler.run()

    save()
    return {'message_id': msgId}

def valid_dm_id(dm_id, data):
    '''
    Helper function to check if dm id is valid

    Arguments:
        dm_id          (int)    - id of the dm
        data           (dict)   - loop through data to check if dm id is valid

    Exceptions:
        No exceptions because its a helper function
   
    Return Value:
        Returns index if dm_id is a valid dm id. If not, return -1
    '''
    for index in range(len(data['dms'])):
        if data['dms'][index]['dm_id'] == dm_id: 
            return index
    return -1

def member_of_dm(dm_index, user_id, data):
    '''
    Helper function to check if user is member of dm

    Arguments:
        user_id        (int)    - id of the authorised user
        dm_index       (int)    - index of the dm
        data           (dict)   - loop through data to check if user is a member of dm

    Exceptions:
        No exceptions because its a helper function
   
    Return Value:
        Returns True if user_id is a member of the dm. If not, return False
    '''
    for index in range(len(data['dms'][dm_index]['members_id'])):
        if data['dms'][dm_index]['members_id'][index] == user_id:
            return True
    return False

def valid_user_id(user_id, data):
    '''
    Helper function to check if user id is valid

    Arguments:
        user_id        (int)    - id of the authorised user
        data           (dict)   - loop through data to check if user id is valid

    Exceptions:
        No exceptions because its a helper function
   
    Return Value:
        Returns True if user_id is a valid user id. If not, return False
    '''
    for index in range(len(data['users'])):
        if data['users'][index]['auth_user_id'] == user_id:
            return True
    return False

def is_owner(dm_index, user_id, data):
    '''
    Helper function to check if user is owner of dm

    Arguments:
        user_id        (int)    - id of the authorised user
        dm_index       (int)    - index of the dm
        data           (dict)   - loop through data to check if user is owner of dm

    Exceptions:
        No exceptions because its a helper function
   
    Return Value:
        Returns True if user_id is owner. If not, return False
    '''
    for index in range(len(data['dms'][dm_index]['owners_id'])):
        if data['dms'][dm_index]['owners_id'][index] == user_id:
            return True
    return False

# Helper function that returns False if user of 'token' is not a member of the channel or dm
# If not, return True
def is_member(u_id, channel_id, dm_id, data):
    '''
    Helper function to check if user is member of dm

    Arguments:
        channel_id     (int)    - always -1, since channel is never used here
        user_id        (int)    - id of the authorised user
        dm_index       (int)    - index of the dm
        data           (dict)   - loop through data to check if user is member of dm

    Exceptions:
        No exceptions because its a helper function
   
    Return Value:
        Returns True if user_id is member. If not, return False
    '''
    is_member = False
    if channel_id == -1: # sent to dm
        for index in range(len(data['dms'])):
            if data['dms'][index]['dm_id'] == dm_id:
                if u_id in data['dms'][index]['members_id']:
                    is_member = True

    elif dm_id == -1: # sent to channel
        for index in range(len(data['channels'])):
            if data['channels'][index]['channel_id'] == channel_id:
                if u_id in data['channels'][index]['members_id']:
                    is_member = True

    return is_member

def token_valid(token, data):
    '''
    Helper function to check if token is valid

    Arguments:
        token          (int)    - token of the authorised user
        data           (dict)   - loop through data to check if token is valid

    Exceptions:
        No exceptions because its a helper function
   
    Return Value:
        Returns True if token is valid. If not, return False
    '''
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

#finds handle of user
def handle_finder(u_id, data):
    for index in range(len(data['users'])):
        if u_id == data['users'][index]['auth_user_id']:
            return data['users'][index]['handle_str']

#finds dm name from dm id
def dm_name_finder(dm_id, data):
    for index in range(len(data['dms'])):
        if data['dms'][index]['dm_id'] == dm_id:
            return data['dms'][index]['name']

#creates a notification when an user is invited to an existing dm
def notification_dm(u_id, dm_id, auth_user_id, data):
    handle = handle_finder(auth_user_id, data)
    dm_name = dm_name_finder(dm_id, data)
    result = ', '.join(str(i) for i in dm_name)     
    notification = {'user_id': [u_id],
                    'channel_id': -1,
                    'dm_id': dm_id,
                    'message': handle + ' added you to ' + result,
                    }
    data['notifications'].append(notification)

#creates a list of all handles that are part of a dm
def handle_dm_list(dm_id, data):
    member_list = []
    handle_list = []
    user = {'handle': 'hi', 'u_id': 1}
    for index in range(len(data['dms'])):
        if data['dms'][index]['dm_id'] == dm_id:
            member_list = data['dms'][index]['members_id']
    for index in range(len(data['users'])):
        for x in member_list:
            if data['users'][index]['auth_user_id'] == x:
                user = {'handle': data['users'][index]['handle_str'], 'u_id': x}
                handle_list.append(user)
    
    return handle_list

#creates a notification when a user is tagged
def notifications_message(dm_id, message, data, auth_user_id):
    handle_list = handle_dm_list(dm_id, data)
    for index in range(len(handle_list)):
        if ('@' + handle_list[index]['handle']) in message:
            handle = handle_finder(auth_user_id, data)
            dm_name = dm_name_finder(dm_id, data)
            name = ', '.join(str(i) for i in dm_name)   
            notification = {'user_id': [handle_list[index]['u_id']],
                            'channel_id': -1,
                            'dm_id': dm_id,
                            'message': handle + ' tagged you in ' + name + ': ' + message[:20],
                            }
            data['notifications'].append(notification)

#creates a notification when an user is invited to an new dm
def notification_dm_create(u_ids, dm_id, auth_user_id, data, name):
    handle = handle_finder(auth_user_id, data)
    result = ', '.join(str(i) for i in name)     
    notification = {'user_id': u_ids,
                    'channel_id': -1,
                    'dm_id': dm_id,
                    'message': handle + ' added you to ' + result,
                    }
    data['notifications'].append(notification)

#changes user analytics whenever a user joins a dm
def analytic_user(u_id, data):
    time_stamp = int(time.time())
    for index in range(len(data['user_analytics'])):
        if u_id == data['user_analytics'][index]['user_id']:
            data['user_analytics'][index]['dms'].append({'num_dms_joined': total_user_dms(u_id, data), 'time_stamp': time_stamp})

#changes user analytics whenever a dm is created
def analytic_multiple_user(dm_id, data):
    time_stamp = int(time.time())
    for x in range(len(data['dms'])):
        if data['dms'][x]['dm_id'] == dm_id:
            for z in data['dms'][x]['members_id']:
                u_id = z
                for index in range(len(data['user_analytics'])):
                    if u_id == data['user_analytics'][index]['user_id']:
                        data['user_analytics'][index]['dms'].append({'num_dms_joined': total_user_dms(u_id, data), 'time_stamp': time_stamp})

#finds total amount of dms a user is in
def total_user_dms(u_id, data):
    total = 0
    for index in range(len(data['dms'])):
        if u_id in data['dms'][index]['members_id']:
            total += 1
    return total

#changes server analytics whenever a server is made
def analytic_server(data):
    time_stamp = int(time.time())
    data['server_analytics']['dms'].append({'num_dms_exist': len(data['dms']), 'time_stamp': time_stamp})

#changes user analytics whenever a message is sent
def analytic_message_user(timestamp, u_id, data):
    for index in range(len(data['user_analytics'])):
        if u_id == data['user_analytics'][index]['user_id']:
            data['user_analytics'][index]['dms'].append({'num_messages_sent': len(data['user_analytics'][index]['messages']), 'time_stamp': timestamp})

#changes server analytics whenever a message is sent
def analytic_message_server(timestamp, data):
    data['server_analytics']['messages'].append({'num_messages_exist': len(data['messages']), 'time_stamp': timestamp})

#function to send msg later
def send_msg_later_helper(token, dm_id, message):
    load_data()
    data = get_data()
    u_id = jwt.decode(token, SECRET, algorithms=['HS256'])['auth_user_id']

    if len(data['messages']) == 0:
        message_id = 1
    else:
        message_id = data['messages'][0]['message_id'] + 1
    # initialize message template
    messagesTemplate = {}
    #get time 
    timestamp = int(time.time())
    #update message information
    messagesTemplate.update({'message_id': message_id})
    messagesTemplate.update({'user_id': u_id}) 
    messagesTemplate.update({'channel_id': None})
    messagesTemplate.update({'dm_id': dm_id})
    messagesTemplate.update({'message': message})
    messagesTemplate.update({'time_created': timestamp})
    messagesTemplate.update({'reacts': []})
    messagesTemplate.update({'is_pinned': False})
    copy = messagesTemplate.copy()
    data['messages'].insert(0, copy)
    # loop through data and update index if dm id matches
    for index in range(len(data['dms'])):
        if data['dms'][index]['dm_id'] == dm_id:
            dm_index = index
            break

    data['dms'][dm_index]['messages'].insert(0, copy)
    notifications_message(dm_id, message, data, u_id)
    save()
    global msgId
    msgId = message_id

# Helper function that returns True is the user has already reacted to message
# If not returns False
# Also returns a second value that is either True or False depending on if 'reacts' list is empty or not
def has_user_reacted(auth_user_id, messageId, data):
    for message_index in range(len(data['messages'])):
        if data['messages'][message_index]['message_id'] == messageId:
            if len(data['messages'][message_index]['reacts']) == 0:
                return False, True 
            else:
                for u_ids_index in range(len(data['messages'][message_index]['reacts'][0]['u_ids'])):
                    if data['messages'][message_index]['reacts'][0]['u_ids'][u_ids_index] == auth_user_id:
                        return True, False
    return False, False
