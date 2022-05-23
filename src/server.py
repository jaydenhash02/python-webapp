import sys
from json import dumps
from flask import Flask, request, send_from_directory
from flask_mail import Mail, Message
from flask_cors import CORS
from src import config
from src.error import InputError
from src.auth import auth_login_v2, auth_register_v2, auth_logout_v1, auth_passwordreset_request_v1, auth_passwordreset_reset_v1
from src.channel import channel_invite_v2, channel_details_v2, channel_messages_v2, channel_leave_v1, channel_join_v2, channel_addowner_v1, channel_removeowner_v1
from src.channels import channels_create_v2, channels_list_v2, channels_listall_v2
from src.message import message_send_v2, message_edit_v2, message_remove_v1, message_share_v1, message_sendlater_v1, message_react_v1, message_unreact_v1, message_pin_v1, message_unpin_v1
from src.dm import dm_details_v1, dm_list_v1, dm_create_v1, dm_remove_v1, dm_invite_v1, dm_leave_v1, dm_messages_v1, message_senddm_v1
from src.user import user_profile_sethandle_v1, user_profile_setemail_v2, user_profile_setname_v2, user_profile_v2, user_all_v1, user_stats_v1, users_stats_v1, user_profile_uploadphoto_v1
from src.other import search_v1, admin_user_permission_change_v1, admin_user_remove_v1, notifications_get_v1, clear_v1
from src.standup import standup_start_v1, standup_send_v1, standup_active_v1

def defaultHandler(err):
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response

APP = Flask(__name__, static_url_path='/static/')

APP.config['MAIL_SERVER']='smtp.gmail.com'
APP.config['MAIL_PORT'] = 465
APP.config['MAIL_USERNAME'] = 'comp1531assignment@gmail.com'
APP.config['MAIL_PASSWORD'] = 'henrylei1234'
APP.config['MAIL_USE_TLS'] = False
APP.config['MAIL_USE_SSL'] = True
mail = Mail(APP)

CORS(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)

# Example
@APP.route("/echo", methods=['GET'])
def echo():
    data = request.args.get('data')
    if data == 'echo':
   	    raise InputError(description='Cannot echo "echo"')
    return dumps({
        'data': data
    })

# auth/login/v2
@APP.route("/auth/login/v2", methods=['POST'])
def auth_login(): 
    data = request.get_json()
    email = data['email']
    password = data['password']
    output = auth_login_v2(email, password)
    return dumps(output)

# auth/register/v2
@APP.route("/auth/register/v2", methods=['POST'])
def auth_register():
    data = request.get_json()
    email = data['email']
    password = data['password']
    name_first = data['name_first']
    name_last = data['name_last']
    output = auth_register_v2(email, password, name_first, name_last)
    return dumps(output)

# auth/logout/v1
@APP.route("/auth/logout/v1", methods=['POST'])
def auth_logout():
    data = request.get_json()
    token = data['token']
    output = auth_logout_v1(token)
    return dumps(output)

# channel/invite/v2
@APP.route("/channel/invite/v2", methods=['POST'])
def channel_invite():
    data = request.get_json()
    token = data['token']
    channel_id = data['channel_id']
    user_id = data['u_id']
    channel_invite_v2(token, channel_id, user_id)
    return dumps({})

# channel/details/v2
@APP.route("/channel/details/v2", methods=['GET'])
def channel_details():
    token = request.args.get('token')
    channel_id = request.args.get('channel_id')
    details = channel_details_v2(token, int(channel_id))
    return dumps(details)

# channel/messages/v2
@APP.route("/channel/messages/v2", methods=['GET'])
def channel_messages():
    token = request.args.get('token')
    channel_id = request.args.get('channel_id')
    start = request.args.get('start')
    messages = channel_messages_v2(token, int(channel_id), int(start))
    return dumps(messages)

# channel/join/v2
@APP.route("/channel/join/v2", methods=['POST'])
def channel_join():
    data = request.get_json()
    token = data['token']
    channel_id = data['channel_id']
    channel_join_v2(token, channel_id)
    return dumps({})

# channel/addowner/v1
@APP.route("/channel/addowner/v1", methods=['POST'])
def channel_addowner():
    data = request.get_json()
    token = data['token']
    channel_id = data['channel_id']
    u_id = data['u_id']
    channel_addowner_v1(token, channel_id, u_id)
    return dumps({})

# channel/removeowner/v1
@APP.route("/channel/removeowner/v1", methods=['POST'])
def channel_removeowner():
    data = request.get_json()
    token = data['token']
    channel_id = data['channel_id']
    u_id = data['u_id']
    channel_removeowner_v1(token, channel_id, u_id)
    return dumps({})
    
# channel/leave/v1
@APP.route("/channel/leave/v1", methods=['POST'])
def channel_leave():
    data = request.get_json()
    token = data['token']
    channel_id = data['channel_id']
    channel_leave_v1(token, channel_id)
    return dumps({})

# channels/list/v2
@APP.route("/channels/list/v2", methods=['GET'])
def channels_list():
    token = request.args.get('token')
    channels = channels_list_v2(token)
    return dumps(channels)

# channels/listall/v2
@APP.route("/channels/listall/v2", methods=['GET'])
def channels_listall():
    token = request.args.get('token')
    channels = channels_listall_v2(token)
    return dumps(channels)

# channels/create/v2
@APP.route("/channels/create/v2", methods=['POST'])
def channels_create():
    data = request.get_json()
    token = data['token']
    name = data['name']
    is_public = data['is_public']
    channel = channels_create_v2(token, name, is_public)
    return dumps(channel)

# message/send/v2
@APP.route("/message/send/v2", methods=['POST'])
def message_send():
    data = request.get_json()
    token = data['token']
    channel_id = data['channel_id']
    message = data['message']
    output = message_send_v2(token, channel_id, message)
    return dumps(output)

# message/edit/v2
@APP.route("/message/edit/v2", methods=['PUT'])
def message_edit():
    data = request.get_json()
    token = data['token']
    message_id = data['message_id']
    message = data['message']
    message_edit_v2(token, message_id, message)
    return dumps({})

# message/remove/v1
@APP.route("/message/remove/v1", methods=['DELETE'])
def message_remove():
    data = request.get_json()
    token = data['token']
    message_id = data['message_id']
    message_remove_v1(token, message_id)
    return dumps({})

# message/share/v1
@APP.route("/message/share/v1", methods=['POST'])
def message_share():
    data = request.get_json()
    token = data['token']
    og_message_id = data['og_message_id']
    message = data['message']
    channel_id = data['channel_id']
    dm_id = data['dm_id']
    output = message_share_v1(token, og_message_id, message, channel_id, dm_id)
    return dumps(output)

# message/sendlater/v1
@APP.route("/message/sendlater/v1", methods=['POST'])
def message_sendlater():
    data = request.get_json()
    token = data['token']
    channel_id = data['channel_id']
    message = data['message']
    time_sent = data['time_sent']
    output = message_sendlater_v1(token, channel_id, message, time_sent)
    return dumps(output)

# message/react/v1
@APP.route("/message/react/v1", methods=['POST'])
def message_react():
    data = request.get_json()
    token = data['token']
    message_id = data['message_id']
    react_id = data['react_id']
    message_react_v1(token, message_id, react_id)
    return dumps({})

# message/unreact/v1
@APP.route("/message/unreact/v1", methods=['POST'])
def message_unreact():
    data = request.get_json()
    token = data['token']
    message_id = data['message_id']
    react_id = data['react_id']
    message_unreact_v1(token, message_id, react_id)
    return dumps({})

# message/pin/v1
@APP.route("/message/pin/v1", methods=['POST'])
def message_pin():
    data = request.get_json()
    token = data['token']
    message_id = data['message_id']
    message_pin_v1(token, message_id)
    return dumps({})

# message/unpin/v1
@APP.route("/message/unpin/v1", methods=['POST'])
def message_unpin():
    data = request.get_json()
    token = data['token']
    message_id = data['message_id']
    message_unpin_v1(token, message_id)
    return dumps({})

# dm/details/v1
@APP.route("/dm/details/v1", methods=['GET'])
def dm_details():
    token = request.args.get('token')
    dm_id = request.args.get('dm_id')
    output = dm_details_v1(token, int(dm_id))
    return dumps(output)

# dm/list/v1
@APP.route("/dm/list/v1", methods=['GET'])
def dm_list():
    token = request.args.get('token')
    output = dm_list_v1(token)
    return dumps(output)

# dm/create/v1
@APP.route("/dm/create/v1", methods=['POST'])
def dm_create():
    data = request.get_json()
    token = data['token']
    u_ids = data['u_ids']
    output = dm_create_v1(token, u_ids)
    return dumps(output)

# dm/remove/v1
@APP.route("/dm/remove/v1", methods=['DELETE'])
def dm_remove():
    data = request.get_json()
    token = data['token']
    dm_id = data['dm_id']
    dm_remove_v1(token, dm_id)
    return dumps({})

# dm/invite/v1
@APP.route("/dm/invite/v1", methods=['POST'])
def dm_invite():
    data = request.get_json()
    token = data['token']
    dm_id = data['dm_id']
    u_id = data['u_id']
    dm_invite_v1(token, dm_id, u_id)
    return dumps({})

# dm/leave/v1
@APP.route("/dm/leave/v1", methods=['POST'])
def dm_leave():
    data = request.get_json()
    token = data['token']
    dm_id = data['dm_id']
    dm_leave_v1(token, dm_id)
    return dumps({})

# dm/messages/v1
@APP.route("/dm/messages/v1", methods=['GET'])
def dm_messages():
    token = request.args.get('token')
    dm_id = request.args.get('dm_id')
    start = request.args.get('start')
    output = dm_messages_v1(token, int(dm_id), int(start))
    return dumps(output)

# message/senddm/v1
@APP.route("/message/senddm/v1", methods=['POST'])
def message_senddm():
    data = request.get_json()
    token = data['token']
    dm_id = data['dm_id']
    message = data['message']
    output = message_senddm_v1(token, dm_id, message)
    return dumps(output)

# user/profile/v2
@APP.route("/user/profile/v2", methods=['GET'])
def user_profile():
    token = request.args.get('token')
    u_id = request.args.get('u_id')
    output = user_profile_v2(token, int(u_id))
    return dumps(output)

# user/profile/setname/v2
@APP.route("/user/profile/setname/v2", methods=['PUT'])
def user_profile_setname():
    data = request.get_json()
    token = data['token']
    name_first = data['name_first']
    name_last = data['name_last']
    user_profile_setname_v2(token, name_first, name_last)
    return dumps({})

# user/profile/setemailv2
@APP.route("/user/profile/setemail/v2", methods=['PUT'])
def user_profile_setemail():
    data = request.get_json()
    token = data['token']
    email = data['email']
    user_profile_setemail_v2(token, email)
    return dumps({})

# user/profile/sethandle/v1
@APP.route("/user/profile/sethandle/v1", methods=['PUT'])
def user_profile_sethandle():
    data = request.get_json()
    token = data['token']
    handle_str = data['handle_str']
    user_profile_sethandle_v1(token, handle_str)
    return dumps({})

# users/all/v1
@APP.route("/users/all/v1", methods=['GET'])
def users_all():
    token = request.args.get('token')
    output = user_all_v1(token)
    return dumps(output)

# search/v2
@APP.route("/search/v2", methods=['GET'])
def search():
    token = request.args.get('token')
    query_str = request.args.get('query_str')
    output = search_v1(token, query_str)
    return dumps(output)

# admin/user/remove/v1
@APP.route("/admin/user/remove/v1", methods=['DELETE'])
def admin_user_remove():
    data = request.get_json()
    token = data['token']
    u_id = data['u_id']
    admin_user_remove_v1(token, u_id)
    return dumps({})

# admin/userpermission/change/v1
@APP.route("/admin/userpermission/change/v1", methods=['POST'])
def admin_userpermission_change():
    data = request.get_json()
    token = data['token']
    u_id = data['u_id']
    permission_id = data['permission_id']
    admin_user_permission_change_v1(token, u_id, permission_id)
    return dumps({})

# notifications/get/v1
@APP.route("/notifications/get/v1", methods=['GET'])
def notifications_get():
    token = request.args.get('token')
    output = notifications_get_v1(token)
    return dumps(output)
    
# clear/v1
@APP.route("/clear/v1", methods=['DELETE'])
def clear():
    clear_v1()
    return dumps({})

# auth/passwordreset/request/v1
@APP.route("/auth/passwordreset/request/v1", methods=['POST'])
def auth_passwordreset_request():
    data = request.get_json()
    email = data['email']
    reset_code = auth_passwordreset_request_v1(email)
    if reset_code == 0:
        return dumps({})
    else:
        msg = Message(f"Password Reset",
                    sender="comp1531assignment@gmail.com",
                    recipients=[f"{email}"])

        msg.body = f"Hello, your password reset code is {reset_code}"
        mail.send(msg)
        return dumps({})

# auth/passwordreset/reset/v1
@APP.route("/auth/passwordreset/reset/v1", methods=['POST'])
def auth_passwordreset_reset():
    data = request.get_json()
    reset_code = data['reset_code']
    new_password = data['new_password']
    auth_passwordreset_reset_v1(reset_code, new_password)
    return dumps({})

# /user/stats/v1
@APP.route("/user/stats/v1", methods=['GET'])
def user_stats():
    token = request.args.get('token')
    output = user_stats_v1(token)
    return dumps(output)

# /users/stats/v1
@APP.route("/users/stats/v1", methods=['GET'])
def users_stats():
    token = request.args.get('token')
    output = users_stats_v1(token)
    return dumps(output)

# /users/stats/v1
@APP.route("/user/profile/uploadphoto/v1", methods=['POST'])
def user_profile_uploadphoto():
    data = request.get_json()
    token = data['token']
    img_url = data['img_url']
    x_start = data['x_start']
    y_start = data['y_start']
    x_end = data['x_end']
    y_end = data['y_end']
    user_profile_uploadphoto_v1(token, img_url, x_start, y_start, x_end, y_end)
    return dumps({})

#returns file
@APP.route('/static/<path:path>')
def send_js(path):
    return send_from_directory('', path)

# standup/start/v1
@APP.route("/standup/start/v1", methods=['POST'])
def standup_start():
    data = request.get_json()
    token = data['token']
    channel_id = data['channel_id']
    length = data['length']
    output = standup_start_v1(token, channel_id, length)
    return dumps(output)

# standup/active/v1
@APP.route("/standup/active/v1", methods=['GET'])
def standup_active():
    token = request.args.get('token')
    channel_id = request.args.get('channel_id')
    output = standup_active_v1(token, int(channel_id))
    return dumps(output)

# standup/send/v1
@APP.route("/standup/send/v1", methods=['POST'])
def standup_send():
    data = request.get_json()
    token = data['token']
    channel_id = data['channel_id']
    message = data['message']
    standup_send_v1(token, channel_id, message)
    return {}

if __name__ == "__main__":
    APP.run(port=config.port) # Do not edit this port
