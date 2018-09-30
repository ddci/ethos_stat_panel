from celery_once import QueueOnce

from twilio.rest import Client

from application.main_logic.custom_logging import save_simple_action
from config import Config
import time

__author__ = 'Daniil Nikulin'
__license__ = "Apache License 2.0"
__email__ = "danil.nikulin@gmail.com"
__date__ = "2018-02-20"
__app__ = "statswebapp"
__status__ = "Development"

from application import celery, redis_store, mongo


# @celery.task(base=QueueOnce, once={'timeout': 60 * 60 * 10})
#
# @celery.task(base=QueueOnce)
# def slow_task():
#     time.sleep(30)
#     return "Done!"


@celery.task(base=QueueOnce, autoretry_for=(Exception,), max_retries=0, default_retry_delay=3, soft_time_limit=3330)
def call_if_attack():
    is_system_calling = redis_store.get("is_system_already_calling")
    if is_system_calling is None:
        redis_store.set("is_system_already_calling", 0)
    is_system_calling = bool(int(redis_store.get("is_system_already_calling")))
    num_of_rigs_under_attack = redis_store.get("main_dashboard:num_of_rigs_under_attack")
    if num_of_rigs_under_attack is None:
        num_of_rigs_under_attack = 0
    else:
        num_of_rigs_under_attack = int(num_of_rigs_under_attack)
    try:
        client_twilio = Client(str(Config.TWILIO_ACCOUNT_SID), str(Config.TWILIO_AUTH_TOKEN))
        is_notified = False
        try_num = 1
        url_with_attack_response = "https://powmining.com/twilio_responses/attack"
        if num_of_rigs_under_attack > 0 and is_system_calling is False:
            while try_num <= 10 and bool(
                    int(redis_store.get("is_system_already_calling"))) is False and is_notified is False:
                redis_store.set("is_system_already_calling", 1)
                save_simple_action("Attempt to notify about attack. \nTry № {} \nRigs under attack {}".format(try_num,
                                                                                                 num_of_rigs_under_attack))
                try_num += 1
                if Config.TWILIO_PHONE_NUMBER_1:
                    call_num_1 = client_twilio.calls.create(
                        to=str(Config.TWILIO_PHONE_NUMBER_1),
                        from_=str(Config.TWILIO_PHONE_NUMBER_SERVER),
                        url=url_with_attack_response
                    )
                    time.sleep(40)
                    call_num_1 = client_twilio.calls(call_num_1.sid).fetch()
                    if not (call_num_1.status == "busy" or call_num_1.status == "failed"):
                        call_num_1 = client_twilio.calls(call_num_1.sid).update(status="completed")
                    call_num_1 = client_twilio.calls(call_num_1.sid).fetch()
                    save_simple_action("Call to {} ended with status {}".format(call_num_1.to, call_num_1.status))
                    if call_num_1.status == "busy" or call_num_1.status == "completed" \
                            or call_num_1.status == "in-progress":
                        is_notified = True
                        save_simple_action("{} has been notified about attack.".format(call_num_1.to))
                    else:
                        save_simple_action("Failed to notify {} about attack.".format(call_num_1.to))

                if Config.TWILIO_PHONE_NUMBER_2 and not is_notified:
                    call_num_2 = client_twilio.calls.create(
                        to=str(Config.TWILIO_PHONE_NUMBER_2),
                        from_=str(Config.TWILIO_PHONE_NUMBER_SERVER),
                        url=url_with_attack_response
                    )
                    time.sleep(40)
                    call_num_2 = client_twilio.calls(call_num_2.sid).fetch()
                    if not (call_num_2.status == "busy" or call_num_2.status == "failed"):
                        call_num_2 = client_twilio.calls(call_num_2.sid).update(status="completed")
                    call_num_2 = client_twilio.calls(call_num_2.sid).fetch()
                    save_simple_action("Call to {} ended with status {}".format(call_num_2.to, call_num_2.status))
                    if call_num_2.status == "busy" or call_num_2.status == "completed" \
                            or call_num_2.status == "in-progress":
                        is_notified = True
                        save_simple_action("{} has been notified about attack.".format(call_num_2.to))
                    else:
                        save_simple_action(" Failed to notify {} about attack.".format(call_num_2.to))

                if Config.TWILIO_PHONE_NUMBER_3 and not is_notified:
                    call_num_3 = client_twilio.calls.create(
                        to=str(Config.TWILIO_PHONE_NUMBER_3),
                        from_=str(Config.TWILIO_PHONE_NUMBER_SERVER),
                        url=url_with_attack_response
                    )
                    time.sleep(40)
                    call_num_3 = client_twilio.calls(call_num_3.sid).fetch()
                    if not (call_num_3.status == "busy" or call_num_3.status == "failed"):
                        call_num_3 = client_twilio.calls(call_num_3.sid).update(status="completed")
                    call_num_3 = client_twilio.calls(call_num_3.sid).fetch()
                    save_simple_action("Call to {} ended with status {}".format(call_num_3.to, call_num_3.status))
                    if call_num_3.status == "busy" or call_num_3.status == "completed" \
                            or call_num_3.status == "in-progress":
                        is_notified = True
                        save_simple_action("{} has been notified about attack.".format(call_num_3.to))
                    else:
                        save_simple_action(" Failed to notify {} about attack.".format(call_num_3.to))

                if Config.TWILIO_PHONE_NUMBER_4 and not is_notified:
                    call_num_4 = client_twilio.calls.create(
                        to=str(Config.TWILIO_PHONE_NUMBER_4),
                        from_=str(Config.TWILIO_PHONE_NUMBER_SERVER),
                        url=url_with_attack_response
                    )
                    time.sleep(40)
                    call_num_4 = client_twilio.calls(call_num_4.sid).fetch()
                    if not (call_num_4.status == 'busy' or call_num_4.status == 'failed'):
                        call_num_4 = client_twilio.calls(call_num_4.sid).update(status="completed")
                    call_num_4 = client_twilio.calls(call_num_4.sid).fetch()
                    save_simple_action("Call to {} ended with status {}".format(call_num_4.to, call_num_4.status))
                    if call_num_4.status == "busy" or call_num_4.status == "completed" \
                            or call_num_4.status == "in-progress":
                        is_notified = True
                        save_simple_action("{} has been notified about attack.".format(call_num_4.to))
                    else:
                        save_simple_action(" Failed to notify {} about attack.".format(call_num_4.to))

                if Config.TWILIO_PHONE_NUMBER_5 and not is_notified:
                    call_num_5 = client_twilio.calls.create(
                        to=str(Config.TWILIO_PHONE_NUMBER_5),
                        from_=str(Config.TWILIO_PHONE_NUMBER_SERVER),
                        url=url_with_attack_response
                    )
                    time.sleep(40)
                    call_num_5 = client_twilio.calls(call_num_5.sid).fetch()
                    if not (call_num_5.status == "busy" or call_num_5=="failed"):
                        call_num_5 = client_twilio.calls(call_num_5.sid).update(status="completed")
                    call_num_5 = client_twilio.calls(call_num_5.sid).fetch()
                    save_simple_action("Call to {} ended with status {}".format(call_num_5.to, call_num_5.status))
                    if call_num_5.status == "busy" or call_num_5.status == "completed" \
                            or call_num_5.status == "in-progress":
                        is_notified = True
                        save_simple_action("{} has been notified about attack.".format(call_num_5.to))
                    else:
                        save_simple_action(" Failed to notify {} about attack.".format(call_num_5.to))

                redis_store.set("is_system_already_calling", 0)
        else:
            print("No attack detected all OK.")
    except Exception as e:
        redis_store.set("is_system_already_calling", 0)
        print(e)
        print("Exception occurred while trying to notify about attack.")
        pass


@celery.task(base=QueueOnce, autoretry_for=(Exception,), max_retries=0, default_retry_delay=3, soft_time_limit=3330)
def call_offline_rigs():
    is_system_calling = redis_store.get("is_system_already_calling")
    if is_system_calling is None:
        redis_store.set("is_system_already_calling", 0)
    is_system_calling = bool(int(redis_store.get("is_system_already_calling")))
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
        pass
    try:
        client_twilio = Client(str(Config.TWILIO_ACCOUNT_SID), str(Config.TWILIO_AUTH_TOKEN))
        is_notified = False
        try_num = 1
        url_with_attack_response = "https://powmining.com/twilio_responses/offline_rigs"
        if num_of_offline_rigs > 0 and is_system_calling is False:
            while try_num <= 10 and bool(
                    int(redis_store.get("is_system_already_calling"))) is False and is_notified is False:
                redis_store.set("is_system_already_calling", 1)
                save_simple_action("Attempt to notify about offline rigs. \nTry № {} \nRigs offline {}".format(try_num,
                                                                                                 num_of_offline_rigs))
                try_num += 1
                if Config.TWILIO_PHONE_NUMBER_1:
                    call_num_1 = client_twilio.calls.create(
                        to=str(Config.TWILIO_PHONE_NUMBER_1),
                        from_=str(Config.TWILIO_PHONE_NUMBER_SERVER),
                        url=url_with_attack_response
                    )
                    time.sleep(40)
                    call_num_1 = client_twilio.calls(call_num_1.sid).fetch()
                    if not (call_num_1.status == "busy" or call_num_1.status == "failed"):
                        call_num_1 = client_twilio.calls(call_num_1.sid).update(status="completed")
                    call_num_1 = client_twilio.calls(call_num_1.sid).fetch()
                    save_simple_action("Call to {} ended with status {}".format(call_num_1.to, call_num_1.status))
                    if call_num_1.status == "busy" or call_num_1.status == "completed" \
                            or call_num_1.status == "in-progress":
                        is_notified = True
                        save_simple_action("{} has been notified about offline rigs.".format(call_num_1.to))
                    else:
                        save_simple_action("Failed to notify {} about offline rigs.".format(call_num_1.to))

                if Config.TWILIO_PHONE_NUMBER_2 and not is_notified:
                    call_num_2 = client_twilio.calls.create(
                        to=str(Config.TWILIO_PHONE_NUMBER_2),
                        from_=str(Config.TWILIO_PHONE_NUMBER_SERVER),
                        url=url_with_attack_response
                    )
                    time.sleep(40)
                    call_num_2 = client_twilio.calls(call_num_2.sid).fetch()
                    if not (call_num_2.status == "busy" or call_num_2.status == "failed"):
                        call_num_2 = client_twilio.calls(call_num_2.sid).update(status="completed")
                    call_num_2 = client_twilio.calls(call_num_2.sid).fetch()
                    save_simple_action("Call to {} ended with status {}".format(call_num_2.to, call_num_2.status))
                    if call_num_2.status == "busy" or call_num_2.status == "completed" \
                            or call_num_2.status == "in-progress":
                        is_notified = True
                        save_simple_action("{} has been notified about offline rigs.".format(call_num_2.to))
                    else:
                        save_simple_action(" Failed to notify {} about offline rigs.".format(call_num_2.to))

                if Config.TWILIO_PHONE_NUMBER_3 and not is_notified:
                    call_num_3 = client_twilio.calls.create(
                        to=str(Config.TWILIO_PHONE_NUMBER_3),
                        from_=str(Config.TWILIO_PHONE_NUMBER_SERVER),
                        url=url_with_attack_response
                    )
                    time.sleep(40)
                    call_num_3 = client_twilio.calls(call_num_3.sid).fetch()
                    if not (call_num_3.status == "busy" or call_num_3.status == "failed"):
                        call_num_3 = client_twilio.calls(call_num_3.sid).update(status="completed")
                    call_num_3 = client_twilio.calls(call_num_3.sid).fetch()
                    save_simple_action("Call to {} ended with status {}".format(call_num_3.to, call_num_3.status))
                    if call_num_3.status == "busy" or call_num_3.status == "completed" \
                            or call_num_3.status == "in-progress":
                        is_notified = True
                        save_simple_action("{} has been notified about offline rigs.".format(call_num_3.to))
                    else:
                        save_simple_action(" Failed to notify {} about offline rigs.".format(call_num_3.to))

                if Config.TWILIO_PHONE_NUMBER_4 and not is_notified:
                    call_num_4 = client_twilio.calls.create(
                        to=str(Config.TWILIO_PHONE_NUMBER_4),
                        from_=str(Config.TWILIO_PHONE_NUMBER_SERVER),
                        url=url_with_attack_response
                    )
                    time.sleep(40)
                    call_num_4 = client_twilio.calls(call_num_4.sid).fetch()
                    if not (call_num_4.status == 'busy' or call_num_4.status == 'failed'):
                        call_num_4 = client_twilio.calls(call_num_4.sid).update(status="completed")
                    call_num_4 = client_twilio.calls(call_num_4.sid).fetch()
                    save_simple_action("Call to {} ended with status {}".format(call_num_4.to, call_num_4.status))
                    if call_num_4.status == "busy" or call_num_4.status == "completed" \
                            or call_num_4.status == "in-progress":
                        is_notified = True
                        save_simple_action("{} has been notified about offline rigs.".format(call_num_4.to))
                    else:
                        save_simple_action(" Failed to notify {} about offline rigs.".format(call_num_4.to))

                if Config.TWILIO_PHONE_NUMBER_5 and not is_notified:
                    call_num_5 = client_twilio.calls.create(
                        to=str(Config.TWILIO_PHONE_NUMBER_5),
                        from_=str(Config.TWILIO_PHONE_NUMBER_SERVER),
                        url=url_with_attack_response
                    )
                    time.sleep(40)
                    call_num_5 = client_twilio.calls(call_num_5.sid).fetch()
                    if not (call_num_5.status == "busy" or call_num_5 == "failed"):
                        call_num_5 = client_twilio.calls(call_num_5.sid).update(status="completed")
                    call_num_5 = client_twilio.calls(call_num_5.sid).fetch()
                    save_simple_action("Call to {} ended with status {}".format(call_num_5.to, call_num_5.status))
                    if call_num_5.status == "busy" or call_num_5.status == "completed" \
                            or call_num_5.status == "in-progress":
                        is_notified = True
                        save_simple_action("{} has been notified about offline rigs.".format(call_num_5.to))
                    else:
                        save_simple_action(" Failed to notify {} about offline rigs.".format(call_num_5.to))

                redis_store.set("is_system_already_calling", 0)
        else:
            print("All machines are working. No offline rigs. All OK.")
    except Exception as e:
        redis_store.set("is_system_already_calling", 0)
        print(e)
        print("Exception occurred while trying to notify about offline rigs.")
        pass

@celery.task(base=QueueOnce, autoretry_for=(Exception,), max_retries=0, default_retry_delay=3, soft_time_limit=3330)
def call_crashed_gpus():
    is_system_calling = redis_store.get("is_system_already_calling")
    if is_system_calling is None:
        redis_store.set("is_system_already_calling", 0)
    is_system_calling = bool(int(redis_store.get("is_system_already_calling")))
    num_of_crashed_gpus = redis_store.get("main_dashboard:num_of_crashed_gpus")
    if num_of_crashed_gpus is None:
        num_of_crashed_gpus = 0
    else:
        num_of_crashed_gpus = int(num_of_crashed_gpus)
    try:
        client_twilio = Client(str(Config.TWILIO_ACCOUNT_SID), str(Config.TWILIO_AUTH_TOKEN))
        is_notified = False
        try_num = 1
        url_with_attack_response = "https://powmining.com/twilio_responses/crashed_gpus"
        if num_of_crashed_gpus > 0 and is_system_calling is False:
            while try_num <= 10 and bool(
                    int(redis_store.get("is_system_already_calling"))) is False and is_notified is False:
                redis_store.set("is_system_already_calling", 1)
                save_simple_action("Attempt to notify about crashed gpus. \nTry № {} \nGPUs crashed {}".format(try_num, num_of_crashed_gpus))
                try_num += 1
                if Config.TWILIO_PHONE_NUMBER_1:
                    call_num_1 = client_twilio.calls.create(
                        to=str(Config.TWILIO_PHONE_NUMBER_1),
                        from_=str(Config.TWILIO_PHONE_NUMBER_SERVER),
                        url=url_with_attack_response
                    )
                    time.sleep(40)
                    call_num_1 = client_twilio.calls(call_num_1.sid).fetch()
                    if not (call_num_1.status == "busy" or call_num_1.status == "failed"):
                        call_num_1 = client_twilio.calls(call_num_1.sid).update(status="completed")
                    call_num_1 = client_twilio.calls(call_num_1.sid).fetch()
                    save_simple_action("Call to {} ended with status {}".format(call_num_1.to, call_num_1.status))
                    if call_num_1.status == "busy" or call_num_1.status == "completed" \
                            or call_num_1.status == "in-progress":
                        is_notified = True
                        save_simple_action("{} has been notified about crashed gpus.".format(call_num_1.to))
                    else:
                        save_simple_action("Failed to notify {} about crashed gpus.".format(call_num_1.to))

                if Config.TWILIO_PHONE_NUMBER_2 and not is_notified:
                    call_num_2 = client_twilio.calls.create(
                        to=str(Config.TWILIO_PHONE_NUMBER_2),
                        from_=str(Config.TWILIO_PHONE_NUMBER_SERVER),
                        url=url_with_attack_response
                    )
                    time.sleep(40)
                    call_num_2 = client_twilio.calls(call_num_2.sid).fetch()
                    if not (call_num_2.status == "busy" or call_num_2.status == "failed"):
                        call_num_2 = client_twilio.calls(call_num_2.sid).update(status="completed")
                    call_num_2 = client_twilio.calls(call_num_2.sid).fetch()
                    save_simple_action("Call to {} ended with status {}".format(call_num_2.to, call_num_2.status))
                    if call_num_2.status == "busy" or call_num_2.status == "completed" \
                            or call_num_2.status == "in-progress":
                        is_notified = True
                        save_simple_action("{} has been notified about crashed gpus.".format(call_num_2.to))
                    else:
                        save_simple_action(" Failed to notify {} about crashed gpus.".format(call_num_2.to))

                if Config.TWILIO_PHONE_NUMBER_3 and not is_notified:
                    call_num_3 = client_twilio.calls.create(
                        to=str(Config.TWILIO_PHONE_NUMBER_3),
                        from_=str(Config.TWILIO_PHONE_NUMBER_SERVER),
                        url=url_with_attack_response
                    )
                    time.sleep(40)
                    call_num_3 = client_twilio.calls(call_num_3.sid).fetch()
                    if not (call_num_3.status == "busy" or call_num_3.status == "failed"):
                        call_num_3 = client_twilio.calls(call_num_3.sid).update(status="completed")
                    call_num_3 = client_twilio.calls(call_num_3.sid).fetch()
                    save_simple_action("Call to {} ended with status {}".format(call_num_3.to, call_num_3.status))
                    if call_num_3.status == "busy" or call_num_3.status == "completed" \
                            or call_num_3.status == "in-progress":
                        is_notified = True
                        save_simple_action("{} has been notified about crashed gpus.".format(call_num_3.to))
                    else:
                        save_simple_action(" Failed to notify {} about crashed gpus.".format(call_num_3.to))

                if Config.TWILIO_PHONE_NUMBER_4 and not is_notified:
                    call_num_4 = client_twilio.calls.create(
                        to=str(Config.TWILIO_PHONE_NUMBER_4),
                        from_=str(Config.TWILIO_PHONE_NUMBER_SERVER),
                        url=url_with_attack_response
                    )
                    time.sleep(40)
                    call_num_4 = client_twilio.calls(call_num_4.sid).fetch()
                    if not (call_num_4.status == 'busy' or call_num_4.status == 'failed'):
                        call_num_4 = client_twilio.calls(call_num_4.sid).update(status="completed")
                    call_num_4 = client_twilio.calls(call_num_4.sid).fetch()
                    save_simple_action("Call to {} ended with status {}".format(call_num_4.to, call_num_4.status))
                    if call_num_4.status == "busy" or call_num_4.status == "completed" \
                            or call_num_4.status == "in-progress":
                        is_notified = True
                        save_simple_action("{} has been notified about crashed gpus.".format(call_num_4.to))
                    else:
                        save_simple_action(" Failed to notify {} about crashed gpus.".format(call_num_4.to))

                if Config.TWILIO_PHONE_NUMBER_5 and not is_notified:
                    call_num_5 = client_twilio.calls.create(
                        to=str(Config.TWILIO_PHONE_NUMBER_5),
                        from_=str(Config.TWILIO_PHONE_NUMBER_SERVER),
                        url=url_with_attack_response
                    )
                    time.sleep(40)
                    call_num_5 = client_twilio.calls(call_num_5.sid).fetch()
                    if not (call_num_5.status == "busy" or call_num_5=="failed"):
                        call_num_5 = client_twilio.calls(call_num_5.sid).update(status="completed")
                    call_num_5 = client_twilio.calls(call_num_5.sid).fetch()
                    save_simple_action("Call to {} ended with status {}".format(call_num_5.to, call_num_5.status))
                    if call_num_5.status == "busy" or call_num_5.status == "completed" \
                            or call_num_5.status == "in-progress":
                        is_notified = True
                        save_simple_action("{} has been notified about crashed gpus.".format(call_num_5.to))
                    else:
                        save_simple_action(" Failed to notify {} about crashed gpus.".format(call_num_5.to))

                redis_store.set("is_system_already_calling", 0)
        else:
            print("No GPUs crashed.all OK.")
    except Exception as e:
        redis_store.set("is_system_already_calling", 0)
        print(e)
        print("Exception occurred while trying to notify about crashed gpus.")
        pass