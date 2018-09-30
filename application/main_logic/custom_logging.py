from datetime import datetime

__author__ = 'Daniil Nikulin'
__license__ = "Apache License 2.0"
__email__ = "danil.nikulin@gmail.com"
__date__ = "2018-02-16"
__app__ = "statswebapp"
__status__ = "Development"


def save_accessing(current_user, request):
    dt_obj = datetime.now()
    if not current_user.is_anonymous:
        with open("log/pow_log.txt", "a+") as custom_log:
            print(str(dt_obj) + " : " + current_user.username + " : " + str(request.path))
            custom_log.write(str(dt_obj) + " : " + current_user.username + " : " + str(request.path) + "\n")
    else:
        with open("log/pow_log.txt", "a+") as custom_log:
            print(str(dt_obj) + " : " + "unauthenticated user" + " : " + str(request.url_rule))
            custom_log.write(str(dt_obj) + " : " + "unauthenticated user" + " : " + str(request.path) + "\n")


def save_action(current_user, request, action):
    dt_obj = datetime.now()
    if not current_user.is_anonymous:
        with open("log/pow_log.txt", "a+") as custom_log:
            print(str(dt_obj) + " : " + current_user.username + " : " + str(request.path) + " : " + action)
            custom_log.write(
                str(dt_obj) + " : " + current_user.username + " : " + str(request.path) + " : " + action + "\n")
    else:
        with open("log/pow_log.txt", "a+") as custom_log:
            print(str(dt_obj) + " : " + "unauthenticated user" + " : " + str(request.path) + " : " + action)
            custom_log.write(
                str(dt_obj) + " : " + "unauthenticated user" + " : " + str(request.path) + " : " + action + "\n")


def save_simple_action(action):
    dt_obj = datetime.now()
    with open("log/pow_log.txt", "a+") as custom_log:
        print(str(dt_obj) + " : " + action)
        custom_log.write(str(dt_obj) + " : " + action + "\n")
