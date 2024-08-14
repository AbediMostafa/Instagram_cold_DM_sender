import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from peewee import fn, SQL

# # import utc
# # from apscheduler.schedulers.background import BackgroundScheduler
# # from apscheduler.jobstores.mongodb import MongoDBJobStore
# # from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
# # from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
# # import time
# #
# #
# import sys
# import os
#
# # Add the parent directory of `script` to sys.path
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# # jobstores = {
# #     'mongo': MongoDBJobStore(),
# #     'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
# # }
# # executors = {
# #     'default': ThreadPoolExecutor(20),
# #     'processpool': ProcessPoolExecutor(5)
# # }
# # job_defaults = {
# #     'coalesce': False,
# #     'max_instances': 3
# # }
# #
# # def d1():
# #     f = open('d1.txt', "a")
# #     f.write(str(time.time()))
# #     f.close()
# #
# #
# # def d2():
# #     f = open(str(time.time()), "a")
# #     f.write("salam")
# #     f.close()
# #
# #
# # scheduler = BackgroundScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults)
# # scheduler.add_job(d1, 'interval', seconds=1)
# # scheduler.add_job(d2, 'interval', seconds=3)
# # scheduler.start()
# #
# # time.sleep(10)
#
# import instagrapi.exceptions
# import requests
# import urllib3.connection
# import urllib3
# from requests.adapters import HTTPAdapter
# from script.models.AccountHelper import *
#
# from datetime import datetime, timedelta
# from spintax import spintax
#
# #
# from script.extra.process.Process import Process
# # #
# # # while True:
# # Process().start()
# # #
# #
#
#
# igMobile.login()
# igMobile.client.set_proxy()
# #
# # print(igMobile.client.direct_threads())
# #
# # import requests
# #
# from script.extra.instagram.InstagramMobile import InstagramMobile
# from script.extra.events.ChangeNameEvent import ChangeNameEvent
# from script.extra.events.FollowEvent import FollowEvent
# from script.extra.events.PostVideoEvent import PostVideoEvent
# from script.extra.events.LoomFollowUpEvent import LoomFollowUpEvent
# from script.extra.events.DmEvent import DmEvent
# from script.extra.events.DmFollowUpEvent import DmFollowUpEvent
# from script.extra.hooks.CheckNewMessageHooks import CheckNewMessageHooks
#
# # from instagrapi.exceptions import ProxyAddressIsBlocked
# #
# # ChangeNameEvent(account, ig).fire()
# ChangeUsernameEvent(account, ig).fire()
# ChangeBioEvent(account, ig).fire()
# # ChangeAvatarEvent(account, ig).fire()
# # ChangeAvatarEvent(account, ig).fire()
# # PostVideoEvent(account, ig).fire()
# FollowEvent(account, ig).fire()
# DmEvent(account, ig).fire()
# DmFollowUpEvent(account, ig).fire()
# LoomFollowUpEvent(account, ig).fire()
#
from script.extra.process.Process import Process
from script.extra.instagram.Instagram import Instagram
from script.extra.instagram.InstagramMobile import InstagramMobile
from script.models.Account import Account

process = Process()
while True:
    process.start()

