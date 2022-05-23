from src.error import InputError, AccessError
from src.data import message_template, SECRET, load_data, get_data, save
import jwt 
import time, sched

def message_send_v2(token, channel_id, message):
    '''
    Takes the token, channel id and message to send a message

    Arguments:
        token           (int)    - token of the authorised user
        channel_id      (int)    - id of the channel
        message         (string) - message being sent

    Exceptions:
        InputError   - Occurs when the message is over 1000 characters
        AccessError  - Occurs when auth user is not a member of the channel
        AccessError  - Occurs when the token is invalid
   
    Return Value:
        Returns a dictionary with message id
    '''

    load_data()
    data = get_data()
    # InputError when message is more than 1000 characters 
    if len(message) > 1000:
        raise InputError("Message is more than 1000 characters")

    # AccessError when the authorised user is not already a member of the channel
    u_id = jwt.decode(token, SECRET, algorithms=['HS256'])['auth_user_id']
    
    #checks if id from token is valid
    if token_valid(token, data) == False:
        raise AccessError("Invalid token")

    #checks if u_id is a member of the channel
    if member_of_channel(channel_id, u_id, data) == False: 
        raise AccessError("The authorised user is not a member of the channel")

    #if standup is active buffers the message
    if is_standup_active(channel_id, data) == True:
        handle = handle_finder(u_id, data)
        standup_message = f'{handle}: ' + message

        for index in range(len(data['channels'])):
            if data['channels'][index]['channel_id'] == channel_id:
                data['channels'][index]['standup_messages'].append(standup_message)

        save()
        return {}
        

    if len(data['messages']) == 0:
        message_id = 1
    else:
        message_id = data['messages'][0]['message_id'] + 1

    timestamp = int(time.time())
    #creates a new message and appends it to data
    message_template.update({'message_id': message_id})
    message_template.update({'user_id': u_id}) 
    message_template.update({'channel_id': channel_id})
    message_template.update({'dm_id': None})
    message_template.update({'message': message})
    message_template.update({'time_created': timestamp})
    message_template.update({'reacts': [] })
    message_template.update({'is_pinned': False})
    copy = message_template.copy()
    data['messages'].insert(0, copy)
        
    for index in range(len(data['channels'])):
        if data['channels'][index]['channel_id'] == channel_id:
            channel_index = index
            break
    data['channels'][channel_index]['messages'].insert(0, copy)
    notifications_message(channel_id, message, data, u_id)
    analytic_message_user(timestamp, u_id, data)
    analytic_message_server(timestamp, data)

    save()
    return {'message_id': message_id}
    
def message_remove_v1(token, message_id):
    '''
    Takes the token and message id to remove a message

    Arguments:
        token           (int)    - token of the authorised user
        message_id      (int)    - id of the message

    Exceptions:
        InputError   - Occurs when the message doesnt exist
        AccessError  - Occurs when auth user is not owner of the channel
        AccessError  - Occurs when the token is invalid
   
    Return Value:
        Returns empty dictionary
    '''
    load_data()
    data = get_data()

    u_id = jwt.decode(token, SECRET, algorithms=['HS256'])['auth_user_id']
    result = is_owner(u_id, message_id, data)

    #checks if id from token is valid
    if token_valid(token, data) == False:
        raise AccessError("Invalid token")

    # Input error when the message with message_id no longer exists
    if does_message_exist(message_id, data) == False:
        raise InputError('Message not longer exists')

    # Access error when the authorised user is not the owner of the message or channel
    if result[0] == False:
        raise AccessError("The authorised user is not the owner of the message or channel")

    message_index = result[1]
    chat_index = result[2]
    chat_type = result[3]

    if chat_type == 0: # is channel
        for index in range(len(data['channels'][chat_index]['messages'])):
            if data['channels'][chat_index]['messages'][index]['message_id'] == message_id:
                data['channels'][chat_index]['messages'].pop(index)
                break
    elif chat_type == 1: # is dm
        for index in range(len(data['dms'][chat_index]['messages'])):
            if data['dms'][chat_index]['messages'][index]['message_id'] == message_id:
                data['dms'][chat_index]['messages'].pop(index)
                break
    
    data['messages'].pop(message_index)
    save()
    return {}

def message_edit_v2(token, message_id, message):
    '''
    Takes the token, message id and message to edit a message

    Arguments:
        token           (int)    - token of the authorised user
        message_id      (int)    - id of the message
        message         (string) - message being sent

    Exceptions:
        InputError   - Occurs when the message doesnt exist
        InputError   - Occurs when the message is over 1000 characters
        AccessError  - Occurs when auth user is not owner of the channel
        AccessError  - Occurs when the token is invalid
   
    Return Value:
        Returns an empty dictionary
    '''
    load_data()
    data = get_data()

    u_id = jwt.decode(token, SECRET, algorithms=['HS256'])['auth_user_id']
    result = is_owner(u_id, message_id, data)

    #checks if id from token is valid
    if token_valid(token, data) == False:
        raise AccessError("Invalid token")

    # InputError when message is more than 1000 characters 
    if len(message) > 1000:
        raise InputError("Message is more than 1000 characters")

    # Input error when the message with message_id no longer exists
    if does_message_exist(message_id, data) == False:
        raise InputError('Message not longer exists')

    # Access error when the authorised user is not the owner of the message or channel
    if result[0] == False:
        raise AccessError("The authorised user is not the owner of the message or channel")
    
    message_index = result[1]
    chat_index = result[2]
    chat_type = result[3]
    
    if message == '':
        message_remove_v1(token, message_id)
    else:
        if chat_type == 0: # is channel
            for index in range(len(data['channels'][chat_index]['messages'])):
                if data['channels'][chat_index]['messages'][index]['message_id'] == message_id:
                    data['channels'][chat_index]['messages'][index]['message'] = message
                    break
        elif chat_type == 1: # is dm
            for index in range(len(data['dms'][chat_index]['messages'])):
                if data['dms'][chat_index]['messages'][index]['message_id'] == message_id:
                    data['dms'][chat_index]['messages'][index]['message'] == message
                    break
        data['messages'][message_index]['message'] = message

    save()
    return {}

def message_share_v1(token, og_message_id, message, channel_id, dm_id):
    '''
    Takes the token, og message id, message, channel id and dm id to share a message

    Arguments:
        token              (int)    - token of the authorised user
        og_message_id      (int)    - id of the original message
        message            (string) - message being sent
        channel_id         (int)    - id of channel
        dm_id              (int)    - id of dm

    Exceptions:
        AccessError  - Occurs when auth user is not a member of the channel or dm
        AccessError  - Occurs when the token is invalid
   
    Return Value:
        Returns a dictionary with share message id
    '''
    load_data()
    data = get_data()

    u_id = jwt.decode(token, SECRET, algorithms=['HS256'])['auth_user_id']
    
    #checks if id from token is valid
    if token_valid(token, data) == False:
        raise AccessError("Invalid token")

    # Access error when the authorised user is not a member of the channel or DM
    if is_member(u_id, channel_id, dm_id, data) == False: 
        raise AccessError("The authorised user has not joined the channel or DM they are trying to share the message to")
    
    for index in range(len(data['messages'])):
        if data['messages'][index]['message_id'] == og_message_id:
            og_message = data['messages'][index]['message']
            break

    if len(data['messages']) == 0:
        message_id = 1
    else:
        message_id = data['messages'][0]['message_id'] + 1

    messagesTemplate = {}
    timestamp = int(time.time())

    messagesTemplate.update({'message_id': message_id})
    messagesTemplate.update({'user_id': u_id}) 

    if channel_id == -1: # sent to dm
        messagesTemplate.update({'channel_id': None})
        messagesTemplate.update({'dm_id': dm_id})
    elif dm_id == -1: # sent to channel
        messagesTemplate.update({'channel_id': channel_id})
        messagesTemplate.update({'dm_id': None})

    messagesTemplate.update({'message': og_message + message})
    messagesTemplate.update({'time_created': timestamp})
    messagesTemplate.update({'reacts': []})
    messagesTemplate.update({'is_pinned': False})
    copy = messagesTemplate.copy()

    if channel_id == -1: # sent to dm
        for index in range(len(data['dms'])):
            if data['dms'][index]['dm_id'] == dm_id:
                dm_index = index
                break
        data['dms'][dm_index]['messages'].insert(0, copy)
    elif dm_id == -1: # sent to channel
        for index in range(len(data['channels'])):
            if data['channels'][index]['channel_id'] == channel_id:
                channel_index = index
                break
        data['channels'][channel_index]['messages'].insert(0, copy)

    data['messages'].insert(0, copy)
    analytic_message_user(timestamp, u_id, data)
    analytic_message_server(timestamp, data)
    save()
    return {'shared_message_id': message_id}

def message_sendlater_v1(token, channel_id, message, time_sent):
    '''
    Takes the token, channel id, message, and a specified time to send the message later

    Arguments:
        token              (int)    - token of the authorised user
        channel id         (int)    - id of the channel
        message            (string) - message being sent
        time_sent          (int)    - time to send message later

    Exceptions:
        AccessError  - Occurs when auth user is not a member of the channel 
        InputError   - Occurs when the channel id is invalid
        InputError   - Occurs when the time sent is in the past
        InputError   - Occurs when the message is more than 1000 characters
   
    Return Value:
        Returns a dictionary with message id
    '''
    load_data()
    data = get_data()

    u_id = jwt.decode(token, SECRET, algorithms=['HS256'])['auth_user_id']

    # InputError when channel_id does not refer to a valid channel
    channel_index = valid_channel_id(channel_id, data)
    if channel_index == -1:
        raise InputError("Invalid channel id")

    # InputError when message is more than 1000 characters 
    if len(message) > 1000:
        raise InputError("Message is more than 1000 characters")

    timestamp = int(time.time())
    time_diff = time_sent - timestamp

    # InputError when time sent is a time in the past
    if time_diff < 0:
        raise InputError("Time_sent is a time in the past")

    # AccessError when the authorised user is not a member of the channel
    if member_of_channel(channel_id, u_id, data) == False:
        raise AccessError("Authorised user is not a member of the channel")

    scheduler = sched.scheduler(time.time, time.sleep)
    scheduler.enter(time_diff, 1, send_msg_later_helper, (token, channel_id, message))
    scheduler.run()

    save()
    return {'message_id': msgId}

def message_react_v1(token, message_id, react_id):
    '''
    Takes the token, message id and react id to react a message

    Arguments:
        token              (int)    - token of the authorised user
        message_id         (string) - id of the message
        react_id           (int)    - id of the react

    Exceptions:
        AccessError  - Occurs when auth user is not a member of the channel 
        InputError   - Occurs when the message already contains an active react from the user
        InputError   - Occurs when the react id is invalid
        InputError   - Occurs when the message id is invalid
   
    Return Value:
        Returns an empty dictionary
    '''
    load_data()
    data = get_data()

    u_id = jwt.decode(token, SECRET, algorithms=['HS256'])['auth_user_id']
    chat = is_message_in_channel_or_dm(message_id, u_id, data) #chat[0] = channel_id, chat[1] = dm_id

    # InputError when message_id is not a valid message within a channel or DM that the authorised user has joined
    if does_msg_exist_for_user(message_id, u_id, data) == False:
        raise InputError("Message_id is not a valid message within a channel or DM that the authorised user has joined")
    
    # InputError when react_id is not a valid React ID
    if react_id != 1:
        raise InputError("React_id is not a valid React ID")

    # InputError when message_id already contains an active React of react_id from the authorised user
    if already_reacted(message_id, react_id, u_id, data) == True:
        raise InputError("Message already contains an active React from the authorised user")

    # AcessError when the authorised user is not a member of the channel or DM that the message is within
    if is_member(u_id, chat[0], chat[1], data) == False:
        raise AccessError("The authorised user is not a member of the channel or DM that the message is within")

    reacts_template = {}

    # Update dms    
    if chat[0] == -1: #is dm
        for dm_index in range(len(data['dms'])):
            if data['dms'][dm_index]['dm_id'] == chat[1]:
                for index in range(len(data['dms'][dm_index]['messages'])):
                    if data['dms'][dm_index]['messages'][index]['message_id'] == message_id:
                        if len(data['dms'][dm_index]['messages'][index]['reacts']) == 0:
                            reacts_template.update({'react_id': react_id})
                            reacts_template.update({'u_ids': [u_id]})
                            copy = reacts_template.copy()
                            data['dms'][dm_index]['messages'][index]['reacts'].append(copy)
                            break
                        else:
                            data['dms'][dm_index]['messages'][index]['reacts'][0]['u_ids'].append(u_id)
                            break
    else: #is channel
        # Update channels
        for channel_index in range(len(data['channels'])):
            if data['channels'][channel_index]['channel_id'] == chat[0]:
                for index in range(len(data['channels'][channel_index]['messages'])):
                    if data['channels'][channel_index]['messages'][index]['message_id'] == message_id:
                        if len(data['channels'][channel_index]['messages'][index]['reacts']) == 0:
                            reacts_template.update({'react_id': react_id})
                            reacts_template.update({'u_ids': [u_id]})
                            copy = reacts_template.copy()
                            data['channels'][channel_index]['messages'][index]['reacts'].append(copy)
                            break
                        else:
                            data['channels'][channel_index]['messages'][index]['reacts'][0]['u_ids'].append(u_id)
                            break

    # Update messages
    copy = reacts_template.copy()
    for message_index in range(len(data['messages'])):
        if data['messages'][message_index]['message_id'] == message_id:
            if len(data['messages'][message_index]['reacts']) == 0:
                data['messages'][message_index]['reacts'].append(copy)
                break
            else:
                data['messages'][message_index]['reacts'][0]['u_ids'].append(u_id)

    save()
    return {}

def message_unreact_v1(token, message_id, react_id):
    '''
    Takes the token, message id and react id to unreact a message

    Arguments:
        token              (int)    - token of the authorised user
        message_id         (string) - id of the message
        react_id           (int)    - id of the react

    Exceptions:
        AccessError  - Occurs when auth user is not a member of the channel 
        InputError   - Occurs when the message already contains an active react from the user
        InputError   - Occurs when the react id is invalid
        InputError   - Occurs when the message id is invalid
   
    Return Value:
        Returns an empty dictionary
    '''
    load_data()
    data = get_data()

    u_id = jwt.decode(token, SECRET, algorithms=['HS256'])['auth_user_id']
    chat = is_message_in_channel_or_dm(message_id, u_id, data) #chat[0] = channel_id, chat[1] = dm_id

    # InputError when message_id is not a valid message within a channel or DM that the authorised user has joined
    if does_msg_exist_for_user(message_id, u_id, data) == False:
        raise InputError("Message_id is not a valid message within a channel or DM that the authorised user has joined")

    # InputError when react_id is not a valid React ID
    if react_id != 1:
        raise InputError("React_id is not a valid React ID")

    # InputError when message_id does not contain an active React of react_id from the authorised user
    if already_reacted(message_id, react_id, u_id, data) == False:
        raise InputError("Message already contains an active React from the authorised user")

    # AcessError when the authorised user is not a member of the channel or DM that the message is within
    if is_member(u_id, chat[0], chat[1], data) == False:
        raise AccessError("The authorised user is not a member of the channel or DM that the message is within")

    # Update dms    
    if chat[0] == -1: #is dm
        for dm_index in range(len(data['dms'])):
            if data['dms'][dm_index]['dm_id'] == chat[1]:
                for message_index in range(len(data['dms'][dm_index]['messages'])):
                    for u_ids_index in range(len(data['dms'][dm_index]['messages'][message_index]['reacts'][0]['u_ids'])):
                        if data['dms'][dm_index]['messages'][message_index]['reacts'][0]['react_id'] == react_id and data['dms'][dm_index]['messages'][message_index]['reacts'][0]['u_ids'][u_ids_index] == u_id:
                            data['dms'][dm_index]['messages'][message_index]['reacts'][0]['u_ids'].pop(u_ids_index)
                            break
    else: #is channel
        # Update channels
        for channel_index in range(len(data['channels'])):
            if data['channels'][channel_index]['channel_id'] == chat[0]:
                for message_index in range(len(data['channels'][channel_index]['messages'])):
                    for u_ids_index in range(len(data['channels'][channel_index]['messages'][message_index]['reacts'][0]['u_ids'])):
                        if data['channels'][channel_index]['messages'][message_index]['reacts'][0]['react_id'] == react_id and data['channels'][channel_index]['messages'][message_index]['reacts'][0]['u_ids'][u_ids_index] == u_id:
                            data['channels'][channel_index]['messages'][message_index]['reacts'][0]['u_ids'].pop(u_ids_index)
                            break

    # Update messages
    for message_index in range(len(data['messages'])):
        if data['messages'][message_index]['message_id'] == message_id:
            for u_ids_index in range(len(data['messages'][message_index]['reacts'][0]['u_ids'])):
                if data['messages'][message_index]['reacts'][0]['react_id'] == react_id and data['messages'][message_index]['reacts'][0]['u_ids'][u_ids_index] == u_id:
                    data['messages'][message_index]['reacts'][0]['u_ids'].pop(u_ids_index)
                    break

    save()
    return {}

def message_pin_v1(token, message_id):
    '''
    Takes the token and message id to pin a message

    Arguments:
        token              (int)    - token of the authorised user
        message_id         (string) - id of the message

    Exceptions:
        AccessError  - Occurs when auth user is not a member of the channel or dm
        AccessError  - Occurs when auth user is not the owner of the channel or dm
        InputError   - Occurs when the message is already pinned
        InputError   - Occurs when the message id is invalid
   
    Return Value:
        Returns an empty dictionary
    '''
    load_data()
    data = get_data()

    u_id = jwt.decode(token, SECRET, algorithms=['HS256'])['auth_user_id']
    result = is_owner(u_id, message_id, data)
    chat = is_message_in_channel_or_dm(message_id, u_id, data) #chat[0] = channel_id, chat[1] = dm_id

    # InputError when the message with message_id is not a valid message
    if does_message_exist(message_id, data) == False:
        raise InputError('Message is not a valid message')

    # InputError when message with message_id is already pinned
    if already_pinned(message_id, data) == True:
        raise InputError("Message is already pinned")

    # Access error when the authorised user is not a member of the channel or DM
    if is_member(u_id, chat[0], chat[1], data) == False: 
        raise AccessError("The authorised user is not a member of the channel or dm")

    # Access error when the authorised user is not the owner of the message or channel
    if result[4] == False:
        raise AccessError("The authorised user is not the owner of the channel or dm")

    # Update dms    
    if chat[0] == -1: #is dm
        for dm_index in range(len(data['dms'])):
            if data['dms'][dm_index]['dm_id'] == chat[1]:
                for message_index in range(len(data['dms'][dm_index]['messages'])):
                    if data['dms'][dm_index]['messages'][message_index]['message_id'] == message_id:
                        data['dms'][dm_index]['messages'][message_index]['is_pinned'] = True
                        break
    else: #is channel
        # Update channels
        for channel_index in range(len(data['channels'])):
            if data['channels'][channel_index]['channel_id'] == chat[0]:
                for message_index in range(len(data['channels'][channel_index]['messages'])):
                    if data['channels'][channel_index]['messages'][message_index]['message_id'] == message_id:
                        data['channels'][channel_index]['messages'][message_index]['is_pinned'] = True
                        break

    # Update messages
    for message_index in range(len(data['messages'])):
        if data['messages'][message_index]['message_id'] == message_id:
            data['messages'][message_index]['is_pinned'] = True
            break

    save()
    return {}

def message_unpin_v1(token, message_id):
    '''
    Takes the token and message id to unpin a message

    Arguments:
        token              (int)    - token of the authorised user
        message_id         (string) - id of the message

    Exceptions:
        AccessError  - Occurs when auth user is not a member of the channel or dm
        AccessError  - Occurs when auth user is not the owner of the channel or dm
        InputError   - Occurs when the message is already unpinned
        InputError   - Occurs when the message id is invalid
   
    Return Value:
        Returns an empty dictionary
    '''
    load_data()
    data = get_data()

    u_id = jwt.decode(token, SECRET, algorithms=['HS256'])['auth_user_id']
    result = is_owner(u_id, message_id, data)
    chat = is_message_in_channel_or_dm(message_id, u_id, data) #chat[0] = channel_id, chat[1] = dm_id

    # InputError when the message with message_id is not a valid message
    if does_message_exist(message_id, data) == False:
        raise InputError('Message is not a valid message')

    # InputError when message with message_id is already unpinned
    if already_pinned(message_id, data) == False:
        raise InputError("Message is already unpinned")

    # Access error when the authorised user is not a member of the channel or DM
    if is_member(u_id, chat[0], chat[1], data) == False: 
        raise AccessError("The authorised user is not a member of the channel or dm")

    # Access error when the authorised user is not the owner of the message or channel
    if result[4] == False:
        raise AccessError("The authorised user is not the owner of the channel or dm")

    # Update dms    
    if chat[0] == -1: #is dm
        for dm_index in range(len(data['dms'])):
            if data['dms'][dm_index]['dm_id'] == chat[1]:
                for message_index in range(len(data['dms'][dm_index]['messages'])):
                    if data['dms'][dm_index]['messages'][message_index]['message_id'] == message_id:
                        data['dms'][dm_index]['messages'][message_index]['is_pinned'] = False
                        break
    else: #is channel
        # Update channels
        for channel_index in range(len(data['channels'])):
            if data['channels'][channel_index]['channel_id'] == chat[0]:
                for message_index in range(len(data['channels'][channel_index]['messages'])):
                    if data['channels'][channel_index]['messages'][message_index]['message_id'] == message_id:
                        data['channels'][channel_index]['messages'][message_index]['is_pinned'] = False
                        break

    # Update messages
    for message_index in range(len(data['messages'])):
        if data['messages'][message_index]['message_id'] == message_id:
            data['messages'][message_index]['is_pinned'] = False
            break

    save()
    return {}

# Helper function that returns True if user of 'token' is a member of the channel
# If not, return False
def member_of_channel(channel_id, u_id, data):
    for index in range(len(data['channels'])):
        if data['channels'][index]['channel_id'] == channel_id:
            if u_id in data['channels'][index]['members_id']:
                return True
    return False

# Helper function that returns True if user of 'token' is a member of the dm
# If not, return False
def member_of_dm(dm_id, u_id, data):
    for index in range(len(data['dms'])):
        if data['dms'][index]['dm_id'] == dm_id:
            dm_index = index
    for index in range(len(data['dms'][dm_index]['members_id'])):
        if data['dms'][dm_index]['members_id'][index] == u_id:
            return True
    return False

# Helper function that returns False if the message_id cannot be found
# If not, return True
def does_message_exist(message_id, data):
    found = False
    for index in range(len(data['messages'])):
        if data['messages'][index]['message_id'] == message_id:
            found = True
            break
    return found 

# Helper function that returns False if user of 'token' is not the owner of the message or channel
# If not, return True
# Also returns the message_index, chat_index and chat_type along with the bool value as a tuple return type
# Chat_type is set to 0 if it is for channel, 1 if it is for dm
def is_owner(u_id, message_id, data):
    is_channel = False
    owner_of_msg = False
    owner_of_chat = False
    channel_id = -1
    dm_id = -1
    message_index = -1
    chat_index = -1

    for index in range(len(data['messages'])):
        if data['messages'][index]['message_id'] == message_id:
            message_index = index
            if data['messages'][index]['dm_id'] == None:
                is_channel = True 
                channel_id = data['messages'][index]['channel_id'] 
            else:
                dm_id = data['messages'][index]['dm_id']
            if data['messages'][index]['user_id'] == u_id: 
                owner_of_msg = True
            break


    if is_channel == True:
        chat_type = 0
        for index in range(len(data['channels'])):
            if data['channels'][index]['channel_id'] == channel_id:
                chat_index = index
                for index in range(len(data['channels'][chat_index]['owners_id'])): 
                    if data['channels'][chat_index]['owners_id'][index] == u_id:
                        owner_of_chat = True
                    break
    else:
        chat_type = 1
        for index in range(len(data['dms'])):
            if data['dms'][index]['dm_id'] == dm_id:
                chat_index = index
                for index in range(len(data['dms'][chat_index]['owners_id'])):
                    if data['dms'][chat_index]['owners_id'][index] == u_id:
                        owner_of_chat = True
                    break
    

    if owner_of_msg == False and owner_of_chat == False:
        return False, message_index, chat_index, chat_type, owner_of_chat
    else:
        return True, message_index, chat_index, chat_type, owner_of_chat

# Helper function that returns False if user of 'token' is not a member of the channel or dm
# If not, return True
def is_member(u_id, channel_id, dm_id, data):
    is_member = False
    
    if channel_id == -1: # sent to dm
        for index in range(len(data['dms'])):
            if data['dms'][index]['dm_id'] == dm_id:
                if u_id in data['dms'][index]['members_id']:
                    is_member = True
                    break
    else: # sent to channel
        for index in range(len(data['channels'])):
            if data['channels'][index]['channel_id'] == channel_id:
                if u_id in data['channels'][index]['members_id']:
                    is_member = True
                    break

    return is_member

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

#creates a list of all handles that are part of a channel
def handle_channel_list(channel_id, data):
    member_list = []
    handle_list = []
    user = {'handle': 'hi', 'u_id': 1}
    for index in range(len(data['channels'])):
        if data['channels'][index]['channel_id'] == channel_id:
            member_list = data['channels'][index]['members_id']
    for index in range(len(data['users'])):
        for x in member_list:
            if data['users'][index]['auth_user_id'] == x:
                user = {'handle': data['users'][index]['handle_str'], 'u_id': x}
                handle_list.append(user)
    
    return handle_list

#creates a notification when a user is tagged
def notifications_message(channel_id, message, data, auth_user_id):
    handle_list = handle_channel_list(channel_id, data)
    for index in range(len(handle_list)):
        if ('@' + handle_list[index]['handle']) in message:
            handle = handle_finder(auth_user_id, data)
            channel_name = channel_name_finder(channel_id, data)
            notification = {'user_id': [handle_list[index]['u_id']],
                            'channel_id': channel_id,
                            'dm_id': -1,
                            'message': handle + ' tagged you in ' + channel_name + ': ' + message[:20],
                            }
            data['notifications'].append(notification)

#finds handle of user
def handle_finder(u_id, data):
    for index in range(len(data['users'])):
        if u_id == data['users'][index]['auth_user_id']:
            return data['users'][index]['handle_str']

#finds channel name from channel id
def channel_name_finder(channel_id, data):
    for index in range(len(data['channels'])):
        if data['channels'][index]['channel_id'] == channel_id:
            return data['channels'][index]['name']

#changes user analytics whenever a message is sent
def analytic_message_user(timestamp, u_id, data):
    for index in range(len(data['user_analytics'])):
        if u_id == data['user_analytics'][index]['user_id']:
            data['user_analytics'][index]['messages'].append({'num_messages_sent': (len(data['user_analytics'][index]['messages']) + 1), 'time_stamp': timestamp})

#changes server analytics whenever a message is sent
def analytic_message_server(timestamp, data):
    data['server_analytics']['messages'].append({'num_messages_exist': (len(data['messages'])), 'time_stamp': timestamp})

# Helper function that returns the index when it finds the valid channel
# If not, return -1
def valid_channel_id(channel_id, data):
    for index in range(len(data['channels'])):
        if data['channels'][index]['channel_id'] == channel_id: 
            return index
    return -1

# Helper function that returns channel_id or dm_id that message is in
def is_message_in_channel_or_dm(message_id, u_id, data):
    for index in range(len(data['messages'])):
        if data['messages'][index]['message_id'] == message_id:
            if data['messages'][index]['channel_id'] == None:
                dm_id = data['messages'][index]['dm_id']
                channel_id = -1
            else:
                dm_id = -1
                channel_id = data['messages'][index]['channel_id']
            break
    return channel_id, dm_id

# Helper function that returns True is a message is already reacted by user
# If not return false 
def already_reacted(message_id, react_id, u_id, data):
    for message_index in range(len(data['messages'])):
        if data['messages'][message_index]['message_id'] == message_id:
            for react_index in range(len(data['messages'][message_index]['reacts'])):
                for u_ids_index in range(len(data['messages'][message_index]['reacts'][react_index]['u_ids'])):
                    if data['messages'][message_index]['reacts'][react_index]['u_ids'][u_ids_index] == u_id and data['messages'][message_index]['reacts'][react_index]['react_id'] == react_id:
                        return True
    return False
    
# Helper function that goes through all the channels and dms that user is a part of
# It then returns True if message_id is in one of those channels or dms
# If not return False
def does_msg_exist_for_user(message_id, u_id, data):
    in_channel = False
    in_dm = False
    #search for user channels
    for channel_index in range(len(data['channels'])):
        channel_id = data['channels'][channel_index]['channel_id']
        if member_of_channel(channel_id, u_id, data) == True:
            for message_index in range(len(data['channels'][channel_index]['messages'])):
                if data['channels'][channel_index]['messages'][message_index]['message_id'] == message_id:
                    in_channel = True
                    break

    #search for user dms
    for dm_index in range(len(data['dms'])):
        dm_id = data['dms'][dm_index]['dm_id']
        if member_of_dm(dm_id, u_id, data) == True:
            for message_index in range(len(data['dms'][dm_index]['messages'])):
                if data['dms'][dm_index]['messages'][message_index]['message_id'] == message_id:
                    in_dm = True
                    break

    if in_channel == True or in_dm == True:
        return True
    else:
        return False

# Helper function that returns True if message with message_id is already pinned
# Else returns False
def already_pinned(message_id, data):
    for message_index in range(len(data['messages'])):
        if data['messages'][message_index]['message_id'] == message_id:
            if data['messages'][message_index]['is_pinned'] == True:
                return True
    return False

# Helper function that basically does what message_send does, except instead of returning message_id, it sets it as a global variable msgId
def send_msg_later_helper(token, channel_id, message):
    load_data()
    data = get_data()
    u_id = jwt.decode(token, SECRET, algorithms=['HS256'])['auth_user_id']

    if len(data['messages']) == 0:
        message_id = 1
    else:
        message_id = data['messages'][0]['message_id'] + 1

    timestamp = int(time.time())
    #creates a new message and appends it to data
    message_template.update({'message_id': message_id})
    message_template.update({'user_id': u_id}) 
    message_template.update({'channel_id': channel_id})
    message_template.update({'dm_id': None})
    message_template.update({'message': message})
    message_template.update({'time_created': timestamp})
    message_template.update({'reacts': [] })
    message_template.update({'is_pinned': False})
    copy = message_template.copy()
    data['messages'].insert(0, copy)
        
    for index in range(len(data['channels'])):
        if data['channels'][index]['channel_id'] == channel_id:
            channel_index = index
            break
    data['channels'][channel_index]['messages'].insert(0, copy)
    notifications_message(channel_id, message, data, u_id)

    save()
    global msgId
    msgId = message_id

#checks if standup is active
def is_standup_active(channel_id, data):
    for index in range(len(data['channels'])):
        if data['channels'][index]['channel_id'] == channel_id:
            return data['channels'][index]['is_active']
