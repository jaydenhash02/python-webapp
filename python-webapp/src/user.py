import re
import urllib.request
import sys
import imgspy
from src import config
from PIL import Image
from json import loads, dumps
from src.error import InputError, AccessError
from src.data import user_template, SECRET, load_data, get_data, save
import jwt


def user_profile_v2(token, u_id):
    '''
    For a valid user, returns information about their user_id, email, first name, last name, and handle
    Arguments:
        token        (string)    - token of the authorised user
        u_id         (int)       - id of the user

    Exceptions:
        InputError   - Occurs when u_id is not a valid user
        AccessError  - Occurs when the token passed in is not a valid id
   
    Return Value:
        Dictionary of the user containing u_id, email, name_first, name_last, handle_str
    '''
    load_data()
    data = get_data()

    jwt.decode(token, SECRET, algorithms=['HS256'])
    
    #checks if id from token is valid
    if token_valid(token, data) == False:
        raise AccessError("Invalid token")

    #checks validty of u_id
    if invalid_u_id_deleted(u_id, data) == False:
        raise InputError("Invalid user id")

    #checks if user is deleted
    if user_deleted(u_id, data) == True:
        for index in range(len(data['deleted_users'])):
            if data['deleted_users'][index]['auth_user_id'] == u_id:
                email = data['deleted_users'][index]['email']
                name_first = data['deleted_users'][index]['name_first']
                name_last = data['deleted_users'][index]['name_last']
                handle_str = data['deleted_users'][index]['handle_str']
                profile_img_url = data['deleted_users'][index]['profile_img_url']
                return {
                    'user': {
                        'u_id': u_id,
                        'email': email,
                        'name_first': name_first,
                        'name_last': name_last,
                        'handle_str': handle_str,
                        'profile_img_url': profile_img_url
                    }
                }

    #finds user data and returns it
    for index in range(len(data['users'])):
        if data['users'][index]['auth_user_id'] == u_id:
            email = data['users'][index]['email']
            name_first = data['users'][index]['name_first']
            name_last = data['users'][index]['name_last']
            handle_str = data['users'][index]['handle_str']
            profile_img_url = data['users'][index]['profile_img_url']
            return {
                'user': {
                    'u_id': u_id,
                    'email': email,
                    'name_first': name_first,
                    'name_last': name_last,
                    'handle_str': handle_str,
                    'profile_img_url': profile_img_url
                }
            }

def user_profile_setname_v2(token, name_first, name_last):
    '''
    Update the authorised user's first and last name    
    Arguments:
        token        (string)    - token of the authorised user
        name_first   (string)    - name of new first name
        name_last    (string)    - name of new last name

    Exceptions:
        InputError   - Occurs when name_first is not between 1 and 50 characters inclusively in length
        InputError   - Occurs when name_last is not between 1 and 50 characters inclusively in length
        AccessError  - Occurs when the token passed in is not a valid id

    Return Value:
        None
    '''
    load_data()
    data = get_data()

    u_id = jwt.decode(token, SECRET, algorithms=['HS256'])['auth_user_id']
        
    #checks if id from token is valid
    if token_valid(token, data) == False:
        raise AccessError("Invalid token")

    #checks if first name is shorter than 50 characters or empty
    if len_name(name_first) == False:
        raise InputError("First name needs to be between 1 and 50 characters")
    #checks if first name is shorter than 50 characters or empty
    if len_name(name_last) == False:
        raise InputError("Last name needs to be between 1 and 50 characters")

    #updates name
    for index in range(len(data['users'])):
        if data['users'][index]['auth_user_id'] == u_id:
            data['users'][index]['name_first'] = name_first
            data['users'][index]['name_last'] = name_last

    save()

    return {
    }

def user_profile_setemail_v2(token, email):
    '''
    Update the authorised user's email address
        Arguments:
        token        (string)    - token of the authorised user
        email        (string)    - new email to be updated

    Exceptions:
        InputError   - Occurs when email is invalid
        InputError   - Occurs when email address is already being used by another user
        AccessError  - Occurs when the token passed in is not a valid id

    Return Value:
        None
    '''
    load_data()
    data = get_data()

    u_id = jwt.decode(token, SECRET, algorithms=['HS256'])['auth_user_id']

    #checks if id from token is valid
    if token_valid(token, data) == False:
        raise AccessError("Invalid token")

    #checks validity of email
    if validate_email(email) == False:
        raise InputError("Invalid Email")

    #checks if email already exists in data
    if email_exist(email, data) == True:
        raise InputError("Email is already registered by another user")

    #updates email
    for index in range(len(data['users'])):
        if data['users'][index]['auth_user_id'] == u_id:
            data['users'][index]['email'] = email

    save()
    
    return {
    }

def user_profile_sethandle_v1(token, handle_str):
    '''
    Update the authorised user's handle    
    Arguments:
        token        (string)    - token of the authorised user
        handle_str   (string)    - new handle to be updated

    Exceptions:
        InputError   - Occurs when handle_str is not between 3 and 20 characters inclusive
        InputError   - Occurs when handle is already used by another user
        AccessError  - Occurs when the token passed in is not a valid id

    Return Value:
        None
    '''
    load_data()
    data = get_data()

    u_id = jwt.decode(token, SECRET, algorithms=['HS256'])['auth_user_id']

    #checks if id from token is valid
    if token_valid(token, data) == False:
        raise AccessError("Invalid token")
    
    #checks length of handle
    if len(handle_str) < 3 or len(handle_str) > 20:
        raise InputError("Handle string is less than 3 characters or more than 20 characters")

    #checks if email already exists in data
    if handle_exist(handle_str, data) == True:
        raise InputError("Handle is already used by another user")

    #updates handle
    for index in range(len(data['users'])):
        if data['users'][index]['auth_user_id'] == u_id:
            data['users'][index]['handle_str'] = handle_str

    save()
    
    return {
    }

def user_all_v1(token):
    '''
    Returns a list of all users and their associated details    Arguments:
        token        (string)    - token of the authorised user

    Exceptions:
        AccessError  - Occurs when the token passed in is not a valid id
        
    Return Value:
        List of dictionaries of users containing u_id, email, name_first, name_last, handle_str
    '''
    load_data()
    data = get_data()

    jwt.decode(token, SECRET, algorithms=['HS256'])

    #checks if id from token is valid
    if token_valid(token, data) == False:
        raise AccessError("Invalid token")

    user_list = []

    for index in range(len(data['users'])):
        u_id = data['users'][index]['auth_user_id']
        email = data['users'][index]['email']
        name_first = data['users'][index]['name_first']
        name_last = data['users'][index]['name_last']
        handle_str = data['users'][index]['handle_str']
        profile_img_url = data['users'][index]['profile_img_url']
        user_list.append({
                        'u_id': u_id,
                        'email': email,
                        'name_first': name_first,
                        'name_last': name_last,
                        'handle_str': handle_str,
                        'profile_img_url': profile_img_url,
                        })
    return {'users': user_list}

def user_stats_v1(token):
    '''
    Takes a token and returns the user's stats

    Arguments:
        token (string)    - token of the authorised user
        ...

    Exceptions:
        AccessError  - Occurs when token is invalid

    Return Value:
        Returns the user's stats which includes channels joined, dms joined, messages sent, involvement rate (in a dictionary)
    '''
    load_data()
    data = get_data()

    u_id = jwt.decode(token, SECRET, algorithms=['HS256'])['auth_user_id']

    #checks if id from token is valid
    if token_valid(token, data) == False:
        raise AccessError("Invalid token")

    #finds the stats for each user
    for index in range(len(data['user_analytics'])):
        if u_id == data['user_analytics'][index]['user_id']:
            channels_joined = data['user_analytics'][index]['channels']
            dms_joined = data['user_analytics'][index]['dms']
            messages_sent = data['user_analytics'][index]['messages']
            num_channels_joined = data['user_analytics'][index]['channels'][-1]['num_channels_joined']
            num_dms_joined = data['user_analytics'][index]['dms'][-1]['num_dms_joined']
            num_msgs_sent = data['user_analytics'][index]['messages'][-1]['num_messages_sent']
            num_dreams_channels = data['server_analytics']['channels'][-1]['num_channels_exist']
            num_dreams_dms = data['server_analytics']['dms'][-1]['num_dms_exist']
            num_dreams_msgs = data['server_analytics']['messages'][-1]['num_messages_exist']

    #calculates the involvement rate
    involvement_rate = (num_channels_joined + num_dms_joined + num_msgs_sent)/(num_dreams_channels + num_dreams_dms + num_dreams_msgs)
    return {'user_stats': {'channels_joined': channels_joined, 'dms_joined': dms_joined, 'messages_sent': messages_sent, 'involvement_rate': involvement_rate}}
 
def users_stats_v1(token):
    '''
    Takes a token and returns the stats of UNSW Dreams

    Arguments:
        token (string)    - token of the authorised user
        ...

    Exceptions:
        AccessError  - Occurs when token is invalid

    Return Value:
        Returns deams stats which includes channels, dms, messages and utilization rate (in a dictionary)
    '''
    load_data()
    data = get_data()

    jwt.decode(token, SECRET, algorithms=['HS256'])['auth_user_id']

    #checks if id from token is valid
    if token_valid(token, data) == False:
        raise AccessError("Invalid token")

    #gets the stats of the server
    channels_exist = data['server_analytics']['channels']
    dms_exist = data['server_analytics']['dms']
    messages_exist = data['server_analytics']['messages']
        
    #gets the number of user who have not joined a channel or dm
    users_havent_joined = 0
    for index in range(len(data['user_analytics'])):
        if (len(data['user_analytics'][index]['channels']) == 0) and (len(data['user_analytics'][index]['dms']) == 0):
            users_havent_joined += 1

    total_users = len(data['users'])
    #calculates utilization rate
    utilization_rate = (total_users - users_havent_joined)/total_users

    return {'dreams_stats': {'channels_exist': channels_exist, 'dms_exist': dms_exist, 'messages_exist': messages_exist, 'utilization_rate': utilization_rate}}

def user_profile_uploadphoto_v1(token, img_url, x_start, y_start, x_end, y_end):
    '''
    Takes a token, image url, and image bounds to upload a profile picture

    Arguments:
        token (string)    - token of the authorised user
        img_url (string)  - url of the image 
        x_start (int)     - starting horizontal bound
        y_start (int)     - starting vertical bound
        x_end   (int)     - ending horizontal bound
        y_end   (int)     - ending vertical bound
        ...

    Exceptions:
        AccessError  - Occurs when token is invalid
        InputError   - Occurs when the HTTP status is not 200
        InputError   - Occurs when the cropping is not within the dimensions of the image
        InputError   - Occurs when the image uploaded is not a JPG

    Return Value:
        Returns the user's stats which includes channels joined, dms joined, messages sent, involvement rate (in a dictionary)
    '''
    load_data()
    data = get_data()

    u_id = jwt.decode(token, SECRET, algorithms=['HS256'])['auth_user_id']

    #checks if id from token is valid
    if token_valid(token, data) == False:
        raise AccessError("Invalid token")

    #gets an image from a url
    try:
        urllib.request.urlretrieve(img_url, f'src/static/{u_id}.jpg')
    except Exception as e:
        if isinstance(e, int) != 200:
            raise InputError("HTTP status not 200") from e
        else:
            pass 

    #gets information of image
    image_information = imgspy.info(img_url)
    width = image_information['width']
    height = image_information['height']

    #raises input error if cropping size is invalid
    if x_end > width or y_end > height or x_start >= x_end or y_start >= y_end:
        raise InputError('Cropping is not within the dimensions of the image')

    #raises input error if image is not a jpg
    if image_information['type'] != 'jpg':
        raise InputError('Image uploaded is not a JPG')

    #crops and saves the image
    imageObject = Image.open(f'src/static/{u_id}.jpg')
    cropped = imageObject.crop((x_start, y_start, x_end, y_end))
    cropped.save(f'src/static/{u_id}.jpg')

    #saves the url to profile
    saved_url = f'http://localhost:{config.port}/' + f'static/{u_id}.jpg'

    for index in range(len(data['users'])):
        if data['users'][index]['auth_user_id'] == u_id:
            data['users'][index]['profile_img_url'] = saved_url

    save()
    return {}
    
#checks if u_id is valid
def invalid_u_id(u_id, data):
    #loops through users checking u_id
    for index in range(len(data['users'])):
        if data['users'][index]['auth_user_id'] == u_id:
            return True
    return False

#checks if u_id is valid
def invalid_u_id_deleted(u_id, data):
    #loops through users checking u_id
    user_exist = False
    deleted_user_exist = False
    for index in range(len(data['users'])):
        if data['users'][index]['auth_user_id'] == u_id:
            user_exist = True
    
    for index in range(len(data['deleted_users'])):
        if data['deleted_users'][index]['auth_user_id'] == u_id:
            deleted_user_exist = True

    if (user_exist == False) and (deleted_user_exist == False):
        return False

#checks if a user has been deleted
def user_deleted(u_id, data):
    for index in range(len(data['deleted_users'])):
        if data['deleted_users'][index]['auth_user_id'] == u_id:
            return True
    return False

#checks if name is empty or more than 50 characters
def len_name(name):
    if len(name) < 1 or len(name) > 50:
        return False

#checks validity of email
def validate_email(email):
    recheck = r'^[a-zA-Z0-9]+[\._]?[a-zA-Z0-9]+[@]\w+[.]\w{2,3}$'
    if re.search(recheck, email):
        return True
    return False

#checks if email is in the data
def email_exist(email, data):
    #loops through users checking email
    for index in range(len(data['users'])):
        if data['users'][index]['email'] == email:
            return True
    return False

#checks if handle string is in the data
def handle_exist(handle_str, data):
    #loops through users checking handle string
    for index in range(len(data['users'])):
        if data['users'][index]['handle_str'] == handle_str:
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
