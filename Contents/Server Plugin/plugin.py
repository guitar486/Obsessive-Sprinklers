#! /usr/bin/env python
# -*- coding: utf-8 -*-
####################################################################################################

import indigo
import SprinklerDevice
import ScheduleDevice
from applescript import asrun, asquote

####################################################################################################
# Plugin
####################################################################################################
class Plugin(indigo.PluginBase):
    def __init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs):
        indigo.PluginBase.__init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs)

        # Dict's for storing devices
        self.schedule_device_dict = {}
        self.device_dict = {}
        self.real_device_dict = {}
        self.active_sprinkler = {}

    def __del__(self):
        indigo.PluginBase.__del__(self)

    def startup(self):
        indigo.server.log('Obsessive Sprinklers started.')

        self.debugging = False
    ####################################################################################################
	# Actions here execute every time communication is enabled to a device
	####################################################################################################
    def deviceStartComm(self, device):

        # Listen for any/all Indigo varible changes
        indigo.variables.subscribeToChanges()
        indigo.devices.subscribeToChanges()

        if device.model == 'Sprinkler Group':
            self.sprinkler_group = device

        # Store schedule device in dict
        # if device.model == 'Sprinkler Schedule Device':
        #     if str(device.id) not in self.device_dict.keys():
        #         self.device_dict[str(device.id)] = ScheduleDevice.Schedule(device)

        # Get list of user-selected real Indigo sprinkler devices and create objects from them
        items = device.pluginProps.get('indigo_sprinklers', '')
        for i in items:
            real_device = indigo.devices[int(i)]

            # Create virtual sprinkler devices
            if (str(real_device.name)) not in self.real_device_dict.keys():
                self.real_device_dict[str(real_device.id)] = SprinklerDevice.RealSprinkler(real_device)

        # Check states on startup
        self.get_state()

    ####################################################################################################
    # Update device in our device_dict if anything changes
    ####################################################################################################
    def deviceUpdated(self, origDev, newDev):

        # Update plugin device
        if str(origDev.pluginId) == 'com.perceptiveautomation.indigoplugin.obsessive-sprinklers':
            self.device_dict[str(newDev.id)] = newDev

        # Update state of Sprinkler Group device if one of the real irrigation devices changes state
        if str(newDev.id) in self.real_device_dict.keys():
            self.get_state()

    ####################################################################################################
    # Remove device from our device_dict if it is deleted in Indigo
    ####################################################################################################
    def deviceDeleted(self, device):
        if str(device.id) in self.device_dict.keys():
            del self.device_dict[str(device.id)]

        #>>>>>>>>>>DEBUGGING<<<<<<<<<<#
        if self.debugging == True:
            indigo.server.log('Deleted device: ' + str(device.name))
        #>>>>>>>>>>DEBUGGING<<<<<<<<<<#

    ####################################################################################################
    # Toggle Debugging
    ####################################################################################################
    def toggle_debugging(self):
        self.debugging = not self.debugging

        #>>>>>>>>>>DEBUGGING<<<<<<<<<<#
        if self.debugging == True:
            indigo.server.log(str(self.device_dict.keys()))
            indigo.server.log(str(self.real_device_dict.keys()))
        #>>>>>>>>>>DEBUGGING<<<<<<<<<<#

    ####################################################################################################
    # Get state of sprinklers
    ####################################################################################################
    # Update state of Sprinkler Group device if one of the real irrigation devices changes state
    def get_state(self):
        running_list = []
        for k, v in self.real_device_dict.iteritems():
            paused = str(self.sprinkler_group.states.get('paused', ''))
            if paused == 'False':
                sprinkler = indigo.devices[int(k)]
                if sprinkler.activeZone == None:
                    running_list.append('off')
                    self.active_sprinkler = {}
                    if len(running_list) == len(self.real_device_dict.keys()):
                        self.sprinkler_group.updateStateOnServer('active_zone', value='Off')
                        self.sprinkler_group.updateStateOnServer('is_running', value='False')

                elif sprinkler.activeZone != None:
                    self.active_sprinkler[str(k)] = sprinkler.activeZone
                    curZone = sprinkler.states.get('activeZone.ui', '')
                    self.sprinkler_group.updateStateOnServer('active_zone', value=str(curZone))
                    self.sprinkler_group.updateStateOnServer('is_running', value='True')
                    break

    ####################################################################################################
    # Run Schedule
    ####################################################################################################
    def run_schedule(self, pluginAction):
        pass

    ####################################################################################################
    # Execute Smart Zone Action
    ####################################################################################################
    def smart_zone_action(self, pluginAction):
        is_running = self.sprinkler_group.states.get('is_running', '')
        sprinkID = str(pluginAction.props['zone'].split(':')[0])
        zone = str(pluginAction.props['zone'].split(':')[1].strip())
        zoneCount = indigo.devices[int(sprinkID)].zoneCount
        smartSchedule = []

        ####################################################################################################
        # If nothing is running, run single selected zone
        ####################################################################################################
        if is_running == 'False':
            for z in xrange(zoneCount+1):
                if z != 0:
                    if z != int(zone):
                        smartSchedule.append(0)
                    elif z == int(zone):
                        #########################################################################################
                        # Change to get proper zone time later when implemented!!!!!!
                        smartSchedule.append(5)
                        #########################################################################################

            # Run single zone
            indigo.sprinkler.run(int(sprinkID), schedule=smartSchedule)
            # indigo.sprinkler.setActiveZone(int(sprinkID), index=int(zone))

        ####################################################################################################
        # Else if ANY sprinklers are already running
        ####################################################################################################
        elif is_running == 'True':
            for k, v in self.real_device_dict.iteritems():
                sprinkler = indigo.devices[int(k)]
                if sprinkler.activeZone != None:
                    running_sprinkler = sprinkler

            ####################################################################################################
            # If this zone was running, next_zone (stops all if no other zones scheduled)
            ####################################################################################################
            if running_sprinkler.activeZone == int(zone):
                indigo.sprinkler.nextZone(int(sprinkID))

    def pause_toggle(self, pluginAction):
        paused = str(self.sprinkler_group.states.get('paused', ''))

        if paused == 'False':
            self.paused_zone = self.sprinkler_group.states.get('active_zone', '')
            indigo.sprinkler.pause(int(self.active_sprinkler.keys()[0]))
            self.sprinkler_group.updateStateOnServer('active_zone', value='Paused')
            self.sprinkler_group.updateStateOnServer('is_running', value='False')
            self.sprinkler_group.updateStateOnServer('paused', value='True')

        else:
            indigo.sprinkler.resume(int(self.active_sprinkler.keys()[0]))
            self.sprinkler_group.updateStateOnServer('active_zone', value=self.paused_zone)
            self.sprinkler_group.updateStateOnServer('is_running', value='True')
            self.sprinkler_group.updateStateOnServer('paused', value='False')

    ####################################################################################################
    # Generate list of enabled zones
    ####################################################################################################
    def myListGenerator(self, filter="", valuesDict=None, typeId="", targetId=0):
        myArray = []
        for k, v in self.real_device_dict.iteritems():
            # real_device = indigo.devices[int(device)]

            for i in xrange(len(v.sprinkler.zoneEnableList)):
                if v.sprinkler.zoneEnableList[i] == True:
                    myArray.append([str(v.sprinkler.id) + ':' + str(i+1), str(v.sprinkler.zoneNames[i])])

    	return myArray

    # ####################################################################################################
    # # Set Schedule Action
    # # Here we modify the self.scheduled_days variable and the day states of the device in order to later
    # # actually modify the Indigo schedule (via applescript)
    # ####################################################################################################
    # def set_scheduled_days(self, pluginAction):
    #
    #     deviceId = pluginAction.deviceId
    #     device = self.device_dict.get(str(deviceId))
    #     action = pluginAction.pluginTypeId
    #     scheduleName = indigo.schedules[int(device.pluginProps.get('real_schedule', ''))].name
    #
    #     # Set a default value for state >>scheduled_days<< if this is a new device
    #     if device.states.get('scheduled_days', '') == '':
    #         device.updateStateOnServer('scheduled_days', value='0000000')
    #
    #         #>>>>>>>>>>DEBUGGING<<<<<<<<<<#
    #         if self.debugging == True:
    #             indigo.server.log('New device, initializing "scheduled_days" variable to "00000000"')
    #         #>>>>>>>>>>DEBUGGING<<<<<<<<<<#
    #
    #     dayList = list(device.states.get('scheduled_days', ''))
    #
    #     # Monday
    #     if pluginAction.props['action'] == 'monday_true':
    #         device.updateStateOnServer('monday', value='True')
    #         dayList[1] = '1'
    #     elif pluginAction.props['action'] == 'monday_false':
    #         device.updateStateOnServer('monday', value='False')
    #         dayList[1] = '0'
    #     elif pluginAction.props['action'] == 'monday_toggle':
    #         device.updateStateOnServer('monday', value= not device.states.get('monday', ''))
    #         if dayList[1] == '1':
    #             dayList[1] = '0'
    #         else:
    #             dayList[1] = '1'
    #     # Tuesday
    #     elif pluginAction.props['action'] == 'tuesday_true':
    #         device.updateStateOnServer('tuesday', value='True')
    #         dayList[2] = '1'
    #     elif pluginAction.props['action'] == 'tuesday_false':
    #         device.updateStateOnServer('tuesday', value='False')
    #         dayList[2] = '0'
    #     elif pluginAction.props['action'] == 'tuesday_toggle':
    #         device.updateStateOnServer('tuesday', value= not device.states.get('tuesday', ''))
    #         if dayList[2] == '1':
    #             dayList[2] = '0'
    #         else:
    #             dayList[2] = '1'
    #     # Wednesday
    #     elif pluginAction.props['action'] == 'wednesday_true':
    #         device.updateStateOnServer('wednesday', value='True')
    #         dayList[3] = '1'
    #     elif pluginAction.props['action'] == 'wednesday_false':
    #         device.updateStateOnServer('wednesday', value='False')
    #         dayList[3] = '0'
    #     elif pluginAction.props['action'] == 'wednesday_toggle':
    #         device.updateStateOnServer('wednesday', value= not device.states.get('wednesday', ''))
    #         if dayList[3] == '1':
    #             dayList[3] = '0'
    #         else:
    #             dayList[3] = '1'
    #     # Thursday
    #     elif pluginAction.props['action'] == 'thursday_true':
    #         device.updateStateOnServer('thursday', value='True')
    #         dayList[4] = '1'
    #     elif pluginAction.props['action'] == 'thursday_false':
    #         device.updateStateOnServer('thursday', value='False')
    #         dayList[4] = '0'
    #     elif pluginAction.props['action'] == 'thursday_toggle':
    #         device.updateStateOnServer('thursday', value= not device.states.get('thursday', ''))
    #         if dayList[4] == '1':
    #             dayList[4] = '0'
    #         else:
    #             dayList[4] = '1'
    #     # Friday
    #     elif pluginAction.props['action'] == 'friday_true':
    #         device.updateStateOnServer('friday', value='True')
    #         dayList[5] = '1'
    #     elif pluginAction.props['action'] == 'friday_false':
    #         device.updateStateOnServer('friday', value='False')
    #         dayList[5] = '0'
    #     elif pluginAction.props['action'] == 'friday_toggle':
    #         device.updateStateOnServer('friday', value= not device.states.get('friday', ''))
    #         if dayList[5] == '1':
    #             dayList[5] = '0'
    #         else:
    #             dayList[5] = '1'
    #     # Saturday
    #     elif pluginAction.props['action'] == 'saturday_true':
    #         device.updateStateOnServer('saturday', value='True')
    #         dayList[6] = '1'
    #     elif pluginAction.props['action'] == 'saturday_false':
    #         device.updateStateOnServer('saturday', value='False')
    #         dayList[6] = '0'
    #     elif pluginAction.props['action'] == 'saturday_toggle':
    #         device.updateStateOnServer('saturday', value= not device.states.get('saturday', ''))
    #         if dayList[6] == '1':
    #             dayList[6] = '0'
    #         else:
    #             dayList[6] = '1'
    #     # Sunday
    #     elif pluginAction.props['action'] == 'sunday_true':
    #         device.updateStateOnServer('sunday', value='True')
    #         dayList[0] = '1'
    #     elif pluginAction.props['action'] == 'sunday_false':
    #         device.updateStateOnServer('sunday', value='False')
    #         dayList[0] = '0'
    #     elif pluginAction.props['action'] == 'sunday_toggle':
    #         device.updateStateOnServer('sunday', value= not device.states.get('sunday', ''))
    #         if dayList[0] == '1':
    #             dayList[0] = '0'
    #         else:
    #             dayList[0] = '1'
    #
    #     # Update scheduled_days variable
    #     newDays = ''.join(dayList)
    #     device.updateStateOnServer('scheduled_days', value=newDays)
    #
    #     ####################################################################################################
    #     # Update the actual Indigo schedule via Applescript
    #     ####################################################################################################
    #     ascript = '''
    #     tell application "IndigoServer"
    #
    #     	set theSchedule to time date action named {schedule_name}
    #     	set date trigger type of theSchedule to specificDays
    #     	set days of week of theSchedule to {schedule_days}
    #
    #     end tell
    #     '''.format(schedule_name = asquote(scheduleName), schedule_days = asquote(newDays))
    #
    #     #>>>>>>>>>>DEBUGGING<<<<<<<<<<#
    #     if self.debugging == True:
    #         indigo.server.log(str(device.name))
    #         indigo.server.log(device.states.get('scheduled_days', ''))
    #         for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
    #             state = device.states.get(day, '')
    #             indigo.server.log(day + ': ' + str(state))
    #         indigo.server.log('Attempting applescript...')
    #         indigo.server.log(ascript)
    #     #>>>>>>>>>>DEBUGGING<<<<<<<<<<#
    #
    #     asrun(ascript)
    #
    # ####################################################################################################
    # # Subscribe to all changes in any Indigo variable value
    # ####################################################################################################
    # def variableUpdated(self, origVar, newVar):
    #
    #     # Create dict of start time variables as selected in device setup
    #     start_time_vars = {}
    #     for deviceId, device in self.device_dict.items():
    #         start_time_vars[str(device.schedule.pluginProps.get('start_time_variable', ''))] = device
    #
    #     # If start Time var changed, run set_scheduled_start_time() to update the actual Indigo schedule
    #     for var, device in start_time_vars.items():
    #         if var == str(origVar.id):
    #             self.set_scheduled_start_time(device, device.schedule.id)
    #
    # ####################################################################################################
    # # Set the schedule start time
    # ####################################################################################################
    # def set_scheduled_start_time(self, device, deviceId):
    #
    #     scheduleName = indigo.schedules[int(device.schedule.pluginProps.get('real_schedule', ''))].name
    #
    #     #>>>>>>>>>>DEBUGGING<<<<<<<<<<#
    #     if self.debugging == True:
    #         indigo.server.log('Schedule Name: ' + scheduleName)
    #     #>>>>>>>>>>DEBUGGING<<<<<<<<<<#
    #
    #     newStartTime = indigo.variables[int(device.schedule.pluginProps.get('start_time_variable', ''))].value
    #
    #     timeAddSeconds = list(newStartTime)
    #     timeAddSeconds.insert(-3, ':00')
    #     newStartTime = ''.join(timeAddSeconds)
    #
    #     device.schedule.updateStateOnServer('scheduled_start_time', value=newStartTime)
    #
    #     ascript = '''
    #     tell application "IndigoServer"
    #
    #     	set theSchedule to time date action named {schedule_name}
    #     	set absolute trigger time of theSchedule to date {schedule_start_time}
    #
    #     end tell
    #     '''.format(schedule_name = asquote(scheduleName), schedule_start_time = asquote('Thursday, January 1, 2015 at {time}'.format(time=newStartTime)))
    #
    #     #>>>>>>>>>>DEBUGGING<<<<<<<<<<#
    #     if self.debugging == True:
    #         indigo.server.log('Attempting applescript...')
    #         indigo.server.log(ascript)
    #     #>>>>>>>>>>DEBUGGING<<<<<<<<<<#
    #
    #     asrun(ascript)
    #
    # ####################################################################################################
    # # Run Schedule
    # ####################################################################################################
    # def run_schedule(self, pluginAction):
    #
    #     deviceId = pluginAction.deviceId
    #     device = self.device_dict.get(str(deviceId))
    #     realDevice = int(device.pluginProps.get('realIrrDevice', ''))
    #
    #     zoneTimesVar = device.pluginProps.get('zone_times_variable', '')
    #     zoneTimes = indigo.variables[int(zoneTimesVar)].value
    #     device.updateStateOnServer('zone_times', value=str(zoneTimes))
    #
    #     zoneTimes = zoneTimes.split(',')
    #
    #     #>>>>>>>>>>DEBUGGING<<<<<<<<<<#
    #     if self.debugging == True:
    #         indigo.server.log(str(device.name))
    #         indigo.server.log(str(device.states.get('zone_times', '')))
    #     #>>>>>>>>>>DEBUGGING<<<<<<<<<<#
    #
    #     indigo.sprinkler.run(realDevice, schedule=[zoneTimes[0], zoneTimes[1], zoneTimes[2], zoneTimes[3], zoneTimes[4], zoneTimes[5], zoneTimes[6], zoneTimes[7]])
