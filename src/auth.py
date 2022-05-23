import re
import random
from json import loads, dumps
from src.error import InputError, AccessError
from src import config
from src.data import user_template, SECRET, load_data, get_data, save, user_analytics_template
import hashlib
import jwt

def auth_login_v2(email, password):
    '''
    Takes an email and password and compares it to the data to see if
    the password matches the corrosponding email

    Arguments:
        email (string)       - email of user
        password (string)    - password of user

    Exceptions:
        InputError  - Occurs when email entered is not a valid email
        InputError  - Occurs when email entered does not belong to a user
        InputError  - Occurs when password is not correct
   
    Return Value:
        Returns auth_user_id if password matches corrosponding email
    '''
    load_data()
    data = get_data()

    #hashes the password
    hash_password = hashlib.sha256(password.encode()).hexdigest()

    #checks validity of email
    if validate_email(email) == False:
        raise InputError("Invalid Email")
    #checks if email is in the data
    if email_exist(email, data) == False:
        raise InputError("Email doesn't exist")
    #checks if password matches email
    if password_check(email, hash_password, data) == False:
        raise InputError("Password is Incorrect")
    #finds auth_user_id and token and logins a session
    for index in range(len(data['users'])):
        if data['users'][index]['email'] == email:
            auth_user_id = data['users'][index]['auth_user_id']
            session_id = (total_sessions_id(data) + 1)
            data['users'][index]['session_id'].append(session_id)
            token = jwt.encode({'session_id': session_id, 'auth_user_id': auth_user_id}, SECRET, algorithm='HS256')
            save()
            #returns auth_user_id and token
            return {'token': token, 'auth_user_id': auth_user_id}

def auth_register_v2(email, password, name_first, name_last):
    '''
    Takes inputs and creates a new dictionary storing them in the data and creates 
    and returns a auth_user_id

    Arguments:
        email (string)          - email of user
        password (string)       - password of user
        name_first (string)     - first name of user
        name_last (string)      - last name of user
    Exceptions:
        InputError  - Occurs when email entered is not a valid email
        InputError  - Occurs when password entered is less that 6 digits
        InputError  - Occurs when first or last name is longer than 50 characters or empty
        Input Error - Occurs when email input is already registered
   
    Return Value:
        Returns auth_user_id of new user if successfully registered
    '''
    load_data()
    data = get_data()

    #hashes the password
    hash_password = hashlib.sha256(password.encode()).hexdigest()

    #checks validity of email
    if validate_email(email) == False:
        raise InputError("Invalid Email")
    #checks if the length of the password is shorter than 6 characters
    if len(password) < 6:
        raise InputError("Password is less than 6 characters long")
    #checks if first name is shorter than 50 characters or empty
    if len_name(name_first) == False:
        raise InputError("First name needs to be between 1 and 50 characters")
    #checks if first name is shorter than 50 characters or empty
    if len_name(name_last) == False:
        raise InputError("Last name needs to be between 1 and 50 characters")
    #checks if email already exists in data
    if email_exist(email, data) == True:
        raise InputError("Email is already registered by another user")

    #creates a user_id 
    if len(data['users']) == 0:
        u_id = 1
    else:
        u_id = len(data['users']) + len(data['deleted_users']) + 1
    
    #if user is first to register they are the global owner
    if u_id > 1:
        permission_id = 2
    else:
        permission_id = 1

    #creates a session_id and token
    session_id = (total_sessions_id(data) + 1)
    token = jwt.encode({'session_id': session_id, 'auth_user_id': u_id}, SECRET, algorithm='HS256')
    #changes the values in the template to the inputs  
    user_template.update({'email': email})
    user_template.update({'password': hash_password})
    user_template.update({'name_first': name_first})
    user_template.update({'name_last': name_last})
    user_template.update({'handle_str': generate_handle(name_first, name_last, data)})
    user_template.update({'auth_user_id': u_id})
    user_template.update({'permission_id': permission_id})
    user_template.update({'session_id': [session_id]})
    user_template.update({'profile_img_url': f'http://localhost:{config.port}/static/default.jpg'})
    user_template.update({'reset_code': 'no_code'})

    #appends the dictionary to the list of users
    dictionary_copy = user_template.copy()
    data['users'].append(dictionary_copy)

    user_analytics_template.update({'user_id': u_id})
    analytic_copy = user_analytics_template.copy()
    data['user_analytics'].append(analytic_copy)

    save()

    #returns the user id and token
    return {'token': token, 'auth_user_id': u_id}

def auth_logout_v1(token):
    '''
    Takes a token and if it is valid, logs out that session id

    Arguments:
        token(string) - token of session

    Exceptions:
        None
   
    Return Value:
        Returns a boolean depending if logout is successful or not
        
    '''
    load_data()
    data = get_data()

    decoded_token = (jwt.decode(token, SECRET, algorithms=['HS256']))

    #searches session ids of users for the session_id from the decoded_token and removes it
    for index in range(len(data['users'])):
        for x in data['users'][index]['session_id']:
            if x == decoded_token['session_id']:
                data['users'][index]['session_id'].remove(decoded_token['session_id'])
                save()
                #if session_id found return true
                return {'is_success': True}

    #if token is invalid raise access error
    raise AccessError("Invalid token")

def auth_passwordreset_request_v1(email):
    '''
    Given an email address, if the user is a registered user, sends them an email containing a specific secret code 
    that lets them reset their password

    Arguments:
        email(string) - email of user

    Exceptions:
        None
   
    Return Value:
        Nothing
        
    '''
    load_data()
    data = get_data()

    #creates a random reset code
    reset_code = random.randint(10000, 99999)

    #checks if email exists
    if email_exist(email, data) == False:
        return 0
    
    #changes reset code in data 
    for index in range(len(data['users'])):
        if data['users'][index]['email'] == email:
            data['users'][index]['reset_code'] = reset_code

    save()

    return reset_code
    
def auth_passwordreset_reset_v1(reset_code, new_password):
    '''
    Given a reset code for a user, set that user's new password to the password provided

    Arguments:
        reset_code (int)         - reset code for user
        new_password (string)    - new password of user

    Exceptions:
        InputError  - Occurs when reset_code is not a valid reset code
        InputError  - Occurs when password entered is less that 6 digits
   
    Return Value:
        Nothing
    '''
    load_data()
    data = get_data()
    
    #checks if the length of the password is shorter than 6 characters
    if len(new_password) < 6:
        raise InputError("Password is less than 6 characters long")

    #if reset code is valid changes password and resets code
    for index in range(len(data['users'])):
        if data['users'][index]['reset_code'] == reset_code and reset_code != 'no_code':
            data['users'][index]['password'] = hashlib.sha256(new_password.encode()).hexdigest()
            data['users'][index]['reset_code'] = 'no_code'
        #if reset code invalid raise input error
        else: 
            raise InputError("Reset code is invalid")

    save()

    return {}

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

    for index in range(len(data['deleted_users'])):
        if data['users'][index]['deleted_email'] == email:
            return True
            
    return False

#checks if password matches email
def password_check(email, hash_password, data):
    #loops through users checking email and password
    for index in range(len(data['users'])):
        if data['users'][index]['email'] == email:
            if data['users'][index]['password'] == hash_password:
                return True
    
    return False

#checks if name is empty or more than 50 characters
def len_name(name):
    if len(name) < 1 or len(name) > 50:
        return False

#generates a handle based on first and last name
def generate_handle(name_first, name_last, data):
    #removes spaces, @ and converts upper case characters to lower case
    handle = name_first + name_last
    handle = handle.replace(' ', '',)
    handle = handle.replace('@', '',)
    handle = handle.lower()

    #if handle is longer than 20 characters only takes the first 20 characters
    if len(handle) > 20:
        tmp = ''
        char = 0
        while char < 20:
            tmp += handle[char]
            char += 1
        handle = tmp

    #if handle already exists adds a number to the end of handle
    #total starts at -1 as 0 is the first number added
    total = -1
    for index in range(len(data['users'])):
        if name_first == data['users'][index]['name_first'] and name_last == data['users'][index]['name_last']:
            total += 1
    if total >= 0:
        handle = handle + str(total)
    return handle

#counts the total amount of session_ids
def total_sessions_id(data):
    total_length = 0
    for index in range(len(data['users'])):
        total_length += len(data['users'][index]['session_id'])
    return total_length
