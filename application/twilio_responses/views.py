from application import redis_store

__author__ = 'Daniil Nikulin'
__license__ = "Apache License 2.0"
__email__ = "danil.nikulin@gmail.com"
__date__ = "2018-02-21"
__app__ = "statswebapp"
__status__ = "Development"

from twilio.twiml.voice_response import VoiceResponse

from . import twilio_responses


@twilio_responses.route("/attack", methods=['GET', 'POST'])
def voice_attack():
    """Respond to incoming phone calls with attack message"""
    # Start our TwiML response
    resp = VoiceResponse()


    # Read a message aloud to the caller
    resp.say("Server is calling you.", voice='alice')

    num_of_rigs_under_attack = redis_store.get("main_dashboard:num_of_rigs_under_attack")
    if num_of_rigs_under_attack is None:
        resp.say("Attack has been detected, but now all rigs are working normally.", voice='alice',loop=10)
        resp.hangup()
    elif int(num_of_rigs_under_attack)==0:
        resp.say("Attack has been detected, but now all rigs are working normally.", voice='alice',loop=10)
        resp.hangup()
    elif int(num_of_rigs_under_attack)>0:
        resp.say("Attack has been detected, you have {} machines under attack.".format(num_of_rigs_under_attack), voice='alice',loop=10)
        resp.hangup()
    return str(resp)


@twilio_responses.route("/offline_rigs", methods=['GET', 'POST'])
def voice_offline_rigs():
    # Start our TwiML response
    resp = VoiceResponse()

    # Read a message aloud to the caller
    resp.say("Server is calling you.", voice='alice')
    try:
        num_of_rigs = redis_store.get('main_dashboard:num_of_rigs')
        if num_of_rigs:
            num_of_rigs = int(num_of_rigs)
        num_of_alive_rigs = redis_store.get('main_dashboard:num_of_alive_rigs')
        if num_of_alive_rigs:
            num_of_alive_rigs = int(num_of_alive_rigs)
        if num_of_rigs >0:
            num_of_offline_rigs = num_of_rigs - num_of_alive_rigs
        else:
            num_of_offline_rigs = 0
    except Exception as e:
        num_of_offline_rigs = 0
        print(e)
        print("Failed to receive num of offline rigs")

    if num_of_offline_rigs>0:
        resp.say("You have {} machines  offline.".format(num_of_offline_rigs),
                 voice='alice', loop=10)
        resp.hangup()
    elif num_of_offline_rigs==0:
        resp.say("You have no machines offline. Problem is solved.",
                 voice='alice', loop=10)
        resp.hangup()
    return str(resp)

@twilio_responses.route("/crashed_gpus", methods=['GET', 'POST'])
def voice_crashed_gpus():
    # Start our TwiML response
    resp = VoiceResponse()

    # Read a message aloud to the caller
    resp.say("Server is calling you.", voice='alice')

    num_of_crashed_gpus = redis_store.get("main_dashboard:num_of_crashed_gpus")
    if num_of_crashed_gpus is None:
        resp.say("Problem Occurred",voice='alice', loop=10)
        resp.hangup()
    elif int(num_of_crashed_gpus) == 0:
        resp.say("All gpus are working normally now.", voice='alice', loop=10)
        resp.hangup()
    elif int(num_of_crashed_gpus) > 0:
        resp.say("You have {} GPUs crashed.".format(num_of_crashed_gpus),
                 voice='alice', loop=5)
        resp.hangup()
    return str(resp)