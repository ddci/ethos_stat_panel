import os
from random import randint

from celery import Celery
from celery.schedules import crontab

from config import config
from application import create_app, redis_store
from application.celery_tasks.tasks import main_dashboard_update, panel_dashboards_update, sidebar_info_update, \
    panels_info_update, heat_chart_dashboard_update, delete_old_data_from_mongodb, technical_information_update, \
    admin_main_dashboard_update, set_list_of_nanopool_wallets, nanopool_info_update, nanopool_payments_history_update, \
    nanopool_report_update
from application.celery_tasks.calls_sms_tasks import call_if_attack, call_offline_rigs, call_crashed_gpus

if os.path.exists('config.env'):
    print('Importing environment from .env file')
    for line in open('config.env'):
        var = line.strip().split('=')
        if len(var) == 2:
            os.environ[str(var[0])] = str(var[1].replace("\"", ""))


def create_celery(app, config_name):
    celery_app = Celery(app.import_name,
                        backend=app.config['CELERY_RESULT_BACKEND'],
                        broker=app.config['CELERY_BROKER_URL'])
    celery_app.conf.update(app.config)
    celery_app.conf.ONCE = {
        'backend': 'celery_once.backends.Redis',
        'settings': {
            'url': config[config_name].CELERY_ONCE_BROKER_DB_URL,
            'default_timeout': 60 * 35
        }
    }
    TaskBase = celery_app.Task
    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery_app.Task = ContextTask
    # SET IS SYSTEM CALLING TO 0
    redis_store.set("is_system_already_calling", 0)
    print("Set 'is_server_calling_you' value to False")
    return celery_app


flask_app = create_app(os.getenv('FLASK_CONFIG') or 'default')
celery = create_celery(flask_app, os.getenv('FLASK_CONFIG') or 'default')


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls reverse_messages every 10 seconds.
    # sender.add_periodic_task(10.0, reverse_messages, name='reverse every 10')
    # Calls log('Logging Stuff') every 30 seconds

    sender.add_periodic_task(10.0, main_dashboard_update.s(),
                             name='Update Main dashboard every 10 sec', expires=180, countdown=randint(0, 9))

    sender.add_periodic_task(15.0, panel_dashboards_update.s(),
                             name='Update panel_dashboards_update every 15 sec', expires=180, countdown=randint(0, 9))

    sender.add_periodic_task(15.0, sidebar_info_update.s(),
                             name='Update sidebar_info_update every 15 sec', expires=180, countdown=randint(0, 9))

    sender.add_periodic_task(15.0, panels_info_update.s(),
                             name='Update panels_info_update every 15 sec', expires=180, countdown=randint(0, 9))

    sender.add_periodic_task(40.0, heat_chart_dashboard_update.s(),
                             name='Update heat_chart_dashboard_update every 40 sec', countdown=randint(0, 9))

    sender.add_periodic_task(crontab(minute='*/15'), delete_old_data_from_mongodb.s(),
                             name='Delete old date from mongo', expires=30)

    sender.add_periodic_task(30.0, technical_information_update.s(),
                             name='technical_information_update every 30 sec', expires=180, countdown=randint(0, 9))

    sender.add_periodic_task(20.0, admin_main_dashboard_update.s(),
                             name='admin_main_dashboard_update every 15 sec', expires=180, countdown=randint(0, 9))

    sender.add_periodic_task(60.0, set_list_of_nanopool_wallets.s(),
                             name='nanopool_wallets_update every 60 sec', expires=180, countdown=randint(0, 9))

    sender.add_periodic_task(120.0, nanopool_info_update.s(),
                             name='nanopool_info_update every 120 sec', expires=180, countdown=randint(0, 9))

    sender.add_periodic_task(120.0, nanopool_payments_history_update.s(),
                             name='nanopool_payments_history_update every 120 sec', expires=180, countdown=randint(0, 9))

    sender.add_periodic_task(100.0, nanopool_report_update.s(),
                             name='nanopool_report_update every 100 sec', expires=180, countdown=20)

    # sender.add_periodic_task(crontab(minute='*/10'), call_if_attack.s(),
    #                          name='ATTACK DETECTION CALLER every 10 min', expires=60*11, countdown=randint(0, 9)
    #                          , queue="server_calls")
    #
    # sender.add_periodic_task(crontab(minute=30,hour='0,5,10,15,20'), call_offline_rigs.s(),
    #                         name='OFFLINE RIGS CALLER every 5 hours', expires=60*40, countdown=randint(0, 9)
    #                         , queue="server_calls")
    #
    # sender.add_periodic_task(crontab(minute=0,hour='0,5,10,15,20'), call_crashed_gpus.s(),
    #                          name='CRASHED GPUS CALLER every 5 hours', expires=60*40, countdown=randint(0, 9)
    #                          , queue="server_calls")

    # options={"expires": 20.0}
    # Executes every Monday morning at 7:30 a.m.
    # sender.add_periodic_task(
    #     crontab(hour=7, minute=30, day_of_week=1),
    #     log.s('Monday morning log!'),
    # )
