#! /usr/bin/env python
# -*- coding: utf-8 -*-
####################################################################################################

import plugin
import indigo

class RealSprinkler(object):
    def __init__(self, sprinkler):
        self.sprinkler = sprinkler

        ########////////TESTING////////########

        # indigo.server.log(str(sprinkler.name))
        #
        # for i in xrange(len(sprinkler.zoneEnableList)):
        #     if sprinkler.zoneEnableList[i] == True:
        #         indigo.server.log(str(sprinkler.zoneNames[i]), str(sprinkler.name))
        # indigo.server.log('', ' ')

        #### 'Zone ' + str(i) + ': ' +

        ########////////TESTING////////########
