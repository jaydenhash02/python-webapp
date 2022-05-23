from src.error import InputError, AccessError
from src.data import channel_template, SECRET, load_data, get_data, save
import time
import jwt

# Invites a user (with user id u_id) to join a channel with ID channel_id. 
# Once invited the user is added to the channel immediately
def channel_invite_v2(token, channel_id, u_id):
    '''
    Takes the authorised user id and channel id to invite a user
    into the channel

    Arguments:
        auth_user_id    (int)    - id of the authorised user
        channel_id      (int)    - id of the channel
        u_id            (int)    - id of the user being invited

    Exceptions:
        InputError   - Occurs when channel_id does not refer to a valid channel
        InputError   - Occurs when u_id does not refer to a valid user
        AccessError  - Occurs when auth_user_id is not a member of the channel
        AccessError  - Occurs when the token passed in is not a valid id

    Return Value:
        Nothing
    '''
    load_data()
    data = get_data()

    auth_user_id = jwt.decode(token, SECRET, algorithms=['HS256'])['auth_user_id']
        
    #checks if id from token is valid
    if token_valid(token, data) == False:
        raise AccessError("Invalid token")

    # InputError when u_id does not refer to a valid user
    if valid_user_id(u_id, data) == False:
        raise InputError("Invalid u_id")

    # InputError when channel_id does not refer to a valid channel
    channel_index = valid_channel_id(channel_id, data)
    if channel_index == -1:
        raise InputError("Invalid channel id")

    # AccessError when the authorised user is not already a member of the channel
    if member_of_channel(channel_index, auth_user_id, data) == False: 
        raise AccessError("The authorised user is not a member of the channel")
 
    # Add u_id to channels members_id 
    
    if already_in_channel(u_id, channel_id, data) == False:
        data['channels'][channel_index]['members_id'].append(u_id) 
        notification_channel(u_id, channel_id, auth_user_id, data)
        analytic_user(u_id, data)

    save()
    return {}

# Given a Channel with ID channel_id that the authorised user is part of, provide basic details about the channel
def channel_details_v2(token, channel_id):
    '''
    Takes the authorised user id and channel id to provide basic details
    about the channel

    Arguments:
        auth_user_id    (int)    - id of the authorised user
        channel_id      (int)    - id of the channel

    Exceptions:
        InputError   - Occurs when channel_id does not refer to a valid channel
        AccessError  - Occurs when auth_user_id is not a member of the channel
        AccessError  - Occurs when the token passed in is not a valid id

    Return Value:
        Returns name, owner_members, all_members as a dictionary
    '''
    load_data()
    data = get_data()
    auth_user_id = jwt.decode(token, SECRET, algorithms=['HS256'])['auth_user_id']

    #checks if id from token is valid
    if token_valid(token, data) == False:
        raise AccessError("Invalid token")

    # InputError when auth_user_id does not refer to a valid user
    if valid_user_id(auth_user_id, data) == False:
        raise AccessError("Invalid auth user id")    

    # InputError when channel_id does not refer to a valid channel
    valid_channel = False
    for index in range(len(data['channels'])):
        if data['channels'][index]['channel_id'] == channel_id:
            valid_channel = True
            channelName = data['channels'][index]['name']
            channel_index = index
    if valid_channel == False:
        raise InputError("Invalid Channel ID")

    # AccessError when the authorised user is not already a member of the channel
    if member_of_channel(channel_index, auth_user_id, data) == False: 
        raise AccessError("The authorised user is not a member of the channel")

    if data['channels'][channel_index]['private'] == True:
        is_public = False
    else:
        is_public = True

    # Making output dictionary
    ownerTemplate = {}
    memberTemplate = {}
    output = {
        'name': channelName,
        'is_public': is_public, 
        'owner_members': [],
        'all_members': []
    }

    #creates the dictionary of the new owner and appends it to data
    for index in range(len(data['channels'][channel_index]['owners_id'])):
        ownerId = data['channels'][channel_index]['owners_id'][index]
        for index in range(len(data['users'])):
            if data['users'][index]['auth_user_id'] == ownerId:
                email = data['users'][index]['email']
                firstName = data['users'][index]['name_first']
                lastName = data['users'][index]['name_last']
                handleStr = data['users'][index]['handle_str']
                profile_img_url = data['users'][index]['profile_img_url']
                ownerTemplate.update({'u_id': ownerId})
                ownerTemplate.update({'email': email})
                ownerTemplate.update({'name_first': firstName})
                ownerTemplate.update({'name_last': lastName})
                ownerTemplate.update({'handle_str': handleStr})
                ownerTemplate.update({'profile_img_url': profile_img_url})
                copy = ownerTemplate.copy()
                output['owner_members'].append(copy)

    #creates the dictionary of the new user and appends it to data
    for index in range(len(data['channels'][channel_index]['members_id'])):
        memberId = data['channels'][channel_index]['members_id'][index]
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
                output['all_members'].append(copy)

    save()
    return output

def channel_messages_v2(token, channel_id, start):
    '''
    Takes the authorised user id, channel id and start value to provide 
    details of the messages in the channel

    Arguments:
        auth_user_id    (int)    - id of the authorised user
        channel_id      (int)    - id of the channel
        start           (int)    - starting value for indexing

    Exceptions:
        InputError   - Occurs when channel_id does not refer to a valid channel
        InputError   - Occurs when the start value is greater than the total number
                       of messages in the channel 
        AccessError  - Occurs when auth_user_id is not a member of the channel
        AccessError  - Occurs when the token passed in is not a valid id
   
    Return Value:
        Returns messages, start, end as dictionary
    '''
    load_data()
    data = get_data()
    auth_user_id = jwt.decode(token, SECRET, algorithms=['HS256'])['auth_user_id']

    #checks if id from token is valid
    if token_valid(token, data) == False:
        raise AccessError("Invalid token")

    # InputError when auth_user_id does not refer to a valid user
    if valid_user_id(auth_user_id, data) == False:
        raise AccessError("Invalid auth user id")

    # InputError when channel_id does not refer to a valid channel
    channel_index = valid_channel_id(channel_id, data)
    if channel_index == -1:
        raise InputError("Invalid channel id")

    # InputError when start is greater than the total number of msgs in channel
    if start > len(data['channels'][channel_index]['messages']):
        raise InputError("Not enough messages in the channel")

    # AccessError when the authorised user is not already a member of the channel
    if member_of_channel(channel_index, auth_user_id, data) == False: 
        raise AccessError("The authorised user is not a member of the channel")

    # Making output dictionary
    length = len(data['channels'][channel_index]['messages'])
    end = start + 50

    if end > length:
        end = -1
    else:
        length = end

    messagesTemplate = {}
    output = {
        'messages': [],
        'start': start,
        'end':end,
    }

    temp = start

    #creates the dictionary of the new message and appends it to data    
    for index in range(len(data['channels'][channel_index]['messages'])):
        messageId = data['channels'][channel_index]['messages'][index]['message_id']
        uId = data['channels'][channel_index]['messages'][index]['user_id']
        message = data['channels'][channel_index]['messages'][index]['message']
        timeCreated = data['channels'][channel_index]['messages'][index]['time_created']
        reacts = data['channels'][channel_index]['messages'][index]['reacts']
        is_pinned = data['channels'][channel_index]['messages'][index]['is_pinned']

        is_this_user_reacted = has_user_reacted(auth_user_id, messageId, data)[0]
        is_empty = has_user_reacted(auth_user_id, messageId, data)[1]
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

def channel_leave_v1(token, channel_id):
    '''
    leave channel given token and channel id

    Arguments:
        token      (int)    - token of authorised user
        channel_id (int)    - id of channel being left

    Exceptions:
        InputError  - Occurs when channel id is invalid
        AccessError - Occurs when token is invalid
        AccessError - Occurs when authorised user is not a member of the channel
        AccessError - Occurs when the token passed in is not a valid id

    Return Value:
        No return value
    '''
    load_data()
    data = get_data()
    auth_user_id = jwt.decode(token, SECRET, algorithms=['HS256'])['auth_user_id']

    #checks if id from token is valid
    if token_valid(token, data) == False:
        raise AccessError("Invalid token")

    # InputError when channel_id does not refer to a valid channel
    channel_index = valid_channel_id(channel_id, data)
    if channel_index == -1:
        raise InputError("Invalid channel id")

    # AccessError when the authorised user is not already a member of the channel
    if member_of_channel(channel_index, auth_user_id, data) == False: 
        raise AccessError("The authorised user is not a member of the channel")

    # removes user from owner
    for index in range(len(data['channels'][channel_index]['owners_id'])):
        if data['channels'][channel_index]['owners_id'][index] == auth_user_id:
            data['channels'][channel_index]['owners_id'].pop(index)

    # removes user from member
    for index in range(len(data['channels'][channel_index]['members_id'])):
        if data['channels'][channel_index]['members_id'][index] == auth_user_id:
            data['channels'][channel_index]['members_id'].pop(index)

    analytic_user(auth_user_id, data)
    
    save()
    return {}

# Given a channel_id of a channel that the authorised user can join, adds them to that channel
def channel_join_v2(token, channel_id):
    '''
    Takes the authorised user id and channel id so the authorised user 
    can join the channel

    Arguments:
        auth_user_id    (int)    - id of the authorised user
        channel_id      (int)    - id of the channel

    Exceptions:
        InputError   - Occurs when channel_id does not refer to a valid channel
        AccessError  - Occurs when channel_id refers to a channel that is private
        AccessError  - Occurs when the token passed in is not a valid id
   
    Return Value:
        Nothing
    '''
    load_data()
    data = get_data()
    auth_user_id = jwt.decode(token, SECRET, algorithms=['HS256'])['auth_user_id']

    #checks if id from token is valid
    if token_valid(token, data) == False:
        raise AccessError("Invalid token")

    # InputError when auth_user_id does not refer to a valid user
    if valid_user_id(auth_user_id, data) == False:
        raise AccessError("Invalid auth user id") 

    # InputError when channel_id does not refer to a valid channel
    channel_index = valid_channel_id(channel_id, data)
    if channel_index == -1:
        raise InputError("Invalid channel id")

    # AccessError when any of the channel_id refers to a channel that is private
    # (When the authorised user is not a global owner)
    if check_global_owner(auth_user_id, data) == False:
        private_channel = False
        if data['channels'][channel_index]['private'] == True:
            private_channel = True
        if private_channel == True:
            raise AccessError("Channel is private")
    
    # Add user to channel    
    if already_in_channel(auth_user_id, channel_id, data) == False:
        data['channels'][channel_index]['members_id'].append(auth_user_id) 
        analytic_user(auth_user_id, data)

    save()
    return {}

def channel_addowner_v1(token, channel_id, u_id):
    '''
    adds owner given token, channel id and user id

    Arguments:
        token      (int)    - token of authorised user
        channel_id (int)    - id of channel 
        u_id       (int)    - id of user being added as owner

    Exceptions:
        InputError  - Occurs when channel id is invalid
        InputError  - Occurs when the user is already owner
        AccessError - Occurs when the token passed in is not a valid id
        AccessError - Occurs when authorised user is not an owner of the channel

    Return Value:
        No return value
    '''
    load_data()
    data = get_data()
    auth_user_id = jwt.decode(token, SECRET, algorithms=['HS256'])['auth_user_id']

    #checks if id from token is valid
    if token_valid(token, data) == False:
        raise AccessError("Invalid token")

    # InputError when channel_id does not refer to a valid channel
    channel_index = valid_channel_id(channel_id, data)
    if channel_index == -1:
        raise InputError("Invalid channel id")
    
    # InputError when user with u_id is already an owner of the channel
    if is_owner(channel_index, u_id, data) == True:
        raise InputError("User with u_id is already an owner of the channel")

    # AccessError when user with auth_user_id is not an owner of the channel or Dreams
    if is_owner(channel_index, auth_user_id, data) == False and check_global_owner(auth_user_id, data) == False:
        raise AccessError("The authorised user is not an owner of the channel or Dreams")

    if member_of_channel(channel_index, u_id, data) == False:
        data['channels'][channel_index]['members_id'].append(u_id)

    data['channels'][channel_index]['owners_id'].append(u_id)
    save()
    return {}

def channel_removeowner_v1(token, channel_id, u_id):
    '''
    removes owner given token, channel id and user id

    Arguments:
        token      (int)    - token of authorised user
        channel_id (int)    - id of channel 
        u_id       (int)    - id of user being removed as owner

    Exceptions:
        InputError  - Occurs when channel id is invalid
        InputError  - Occurs when the user is already owner
        InputError  - Occurs when the user is currently the only owner
        AccessError - Occurs when the token passed in is not a valid id
        AccessError - Occurs when authorised user is not an owner of the channel

    Return Value:
        No return value
    '''
    load_data()
    data = get_data()
    auth_user_id = jwt.decode(token, SECRET, algorithms=['HS256'])['auth_user_id']

    #checks if id from token is valid
    if token_valid(token, data) == False:
        raise AccessError("Invalid token")
    
    
    channel_index = valid_channel_id(channel_id, data)

    # AcessError when user with auth_user_id is not an owner of the channel or Dreams
    if is_owner(channel_index, auth_user_id, data) == False and check_global_owner(auth_user_id, data) == False:
        raise AccessError("The authorised user is not an owner of the channel or Dreams")
        
    # InputError when channel_id does not refer to a valid channel
    if channel_index == -1:
        raise InputError("Invalid channel id")
    
    # InputError when user with u_id is not a member of the channel
    if member_of_channel(channel_index, u_id, data) == False:
        raise InputError("User with u_id is already an owner of the channel")

    # InputError when the user is currently the only owner
    if len(data['channels'][channel_index]['owners_id']) == 1:
        raise InputError("User is currently the only owner")

    for index in range(len(data['channels'])):
        if u_id in data['channels'][index]['owners_id']:
            data['channels'][index]['owners_id'].remove(u_id)

    for index in range(len(data['channels'])):
        if u_id in data['channels'][index]['members_id']:
            data['channels'][index]['members_id'].remove(u_id)

    save()
    return {}

# Helper function that returns True if auth_user_id is a global owner.
# If not, return False
def check_global_owner(auth_user_id, data):
    for index in range(len(data['users'])):
        if data['users'][index]['auth_user_id'] == auth_user_id:
            if data['users'][index]['permission_id'] == 1:
                return True
            else:
                return False

# Helper function that returns True if user_id is a valid user id
# If not, return False
def valid_user_id(user_id, data):
    for index in range(len(data['users'])):
        if data['users'][index]['auth_user_id'] == user_id:
            return True
    return False

# Helper function that returns the index when it finds the valid channel
# If not, return -1
def valid_channel_id(channel_id, data):
    for index in range(len(data['channels'])):
        if data['channels'][index]['channel_id'] == channel_id: 
            return index
    return -1

# Helper function that returns True if user_id is a member of the channel
# If not, return False
def member_of_channel(channel_index, user_id, data):
    for index in range(len(data['channels'][channel_index]['members_id'])):
        if data['channels'][channel_index]['members_id'][index] == user_id:
            return True
    return False

# Helper function that returns True if user_id is an owner of the channel
# If not, return False
def is_owner(channel_index, user_id, data):
    for index in range(len(data['channels'][channel_index]['owners_id'])):
        if data['channels'][channel_index]['owners_id'][index] == user_id:
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

#checks if id is already in the server   
def already_in_channel(u_id, channel_id, data):
    for index in range(len(data['channels'])):
        if data['channels'][index]['channel_id'] == channel_id:
            if u_id in data['channels'][index]['members_id']: 
                return True
    return False

#finds handle of an user
def handle_finder(u_id, data):
    for index in range(len(data['users'])):
        if u_id == data['users'][index]['auth_user_id']:
            return data['users'][index]['handle_str']

#finds channel name of an user
def channel_name_finder(channel_id, data):
    for index in range(len(data['channels'])):
        if data['channels'][index]['channel_id'] == channel_id:
            return data['channels'][index]['name']

#creates a notification whenever an user is invited
def notification_channel(u_id, channel_id, auth_user_id, data):
    channel_name = channel_name_finder(channel_id, data)
    handle = handle_finder(auth_user_id, data)
    notification = {'user_id': [u_id],
                    'channel_id': channel_id,
                    'dm_id': -1,
                    'message': handle + ' added you to ' + channel_name,
                    }
    data['notifications'].append(notification)

#changes user analytics whenever a user joins a channel
def analytic_user(u_id, data):
    time_stamp = int(time.time())
    for index in range(len(data['user_analytics'])):
        if u_id == data['user_analytics'][index]['user_id']:
            data['user_analytics'][index]['channels'].append({'num_channels_joined': total_channels(u_id, data), 'time_stamp': time_stamp})

#finds total amount of channels a user is in
def total_channels(u_id, data):
    total = 0
    for index in range(len(data['channels'])):
        if u_id in data['channels'][index]['members_id']:
            total += 1
    return total
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
