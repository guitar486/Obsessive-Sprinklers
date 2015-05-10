#! /usr/bin/env python
# -*- coding: utf-8 -*-
####################################################################################################

import plugin
import indigo

class Schedule(object):
    def __init__(self, schedule):
        self.schedule = schedule

        ########////////TESTING////////########
        indigo.server.log('schedule: ' + str(schedule.name))

        ########////////TESTING////////########
