# -*- coding: utf-8 -*-
from apscheduler.schedulers.blocking import BlockingScheduler
import logging

scheduler = BlockingScheduler()


@scheduler.scheduled_job('interval', seconds=5)
def generate_screenshot():
    logging.debug('Watch out!')
    print('This job is run every three minutes.')

scheduler.start()
