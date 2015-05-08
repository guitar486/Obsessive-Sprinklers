#! /usr/bin/env python
# -*- coding: utf-8 -*-
####################################################################################################

import indigo
from applescript import asrun, asquote

####################################################################################################
# Plugin
####################################################################################################
class Plugin(indigo.PluginBase):
    def __init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs):
        indigo.PluginBase.__init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs)

        self.device_dict = {}

    def __del__(self):
        indigo.PluginBase.__del__(self)

    def startup(self):
        indigo.server.log('Obsessive Sprinklers started.')
    ####################################################################################################
	# Actions here execute every time communication is enabled to a device
	####################################################################################################
    def deviceStartComm(self, device):

        if str(device.id) not in self.device_dict.keys():
            self.device_dict[str(device.id)] = device

        # Create dict of start time variables as selected in device setup
        self.start_time_vars = {}
        for deviceId, device in self.device_dict.items():
            self.start_time_vars[str(device.pluginProps.get('start_time_variable', ''))] = device

    ####################################################################################################
    # Update device in our device_dict if anything changes
    ####################################################################################################
    def deviceUpdated(self, origDev, newDev):
        self.device_dict[str(newDev.id)] = newDev

    ####################################################################################################
    # Remove device from our device_dict if it is deleted in Indigo
    ####################################################################################################
    def deviceDeleted(self, device):
        if str(device.id) in self.device_dict.keys():
            indigo.server.log('Deleted device: ' + str(device.name))
            del self.device_dict[str(device.id)]

    ####################################################################################################
    # Set Schedule Action
    # Here we modify the self.scheduled_days variable and the day states of the device in order to later
    # actually modify the Indigo schedule (via applescript)
    ####################################################################################################
    def set_scheduled_days(self, pluginAction):

        deviceId = pluginAction.deviceId
        device = self.device_dict.get(str(deviceId))

        ####################################################################################################
        # Set a default value for state > scheduled_days < if this is a new device
        ####################################################################################################
        if device.states.get('scheduled_days', '') == '':
            device.updateStateOnServer('scheduled_days', value='0000000')

        action = pluginAction.pluginTypeId
        dayList = list(device.states.get('scheduled_days', ''))

        # Monday
        if pluginAction.props['action'] == 'monday_true':
            device.updateStateOnServer('monday', value='True')
            dayList[1] = '1'
        elif pluginAction.props['action'] == 'monday_false':
            device.updateStateOnServer('monday', value='False')
            dayList[1] = '0'
        elif pluginAction.props['action'] == 'monday_toggle':
            device.updateStateOnServer('monday', value= not device.states.get('monday', ''))
            if dayList[1] == '1':
                dayList[1] = '0'
            else:
                dayList[1] = '1'
        # Tuesday
        elif pluginAction.props['action'] == 'tuesday_true':
            device.updateStateOnServer('tuesday', value='True')
            dayList[2] = '1'
        elif pluginAction.props['action'] == 'tuesday_false':
            device.updateStateOnServer('tuesday', value='False')
            dayList[2] = '0'
        elif pluginAction.props['action'] == 'tuesday_toggle':
            device.updateStateOnServer('tuesday', value= not device.states.get('tuesday', ''))
            if dayList[2] == '1':
                dayList[2] = '0'
            else:
                dayList[2] = '1'
        # Wednesday
        elif pluginAction.props['action'] == 'wednesday_true':
            device.updateStateOnServer('wednesday', value='True')
            dayList[3] = '1'
        elif pluginAction.props['action'] == 'wednesday_false':
            device.updateStateOnServer('wednesday', value='False')
            dayList[3] = '0'
        elif pluginAction.props['action'] == 'wednesday_toggle':
            device.updateStateOnServer('wednesday', value= not device.states.get('wednesday', ''))
            if dayList[3] == '1':
                dayList[3] = '0'
            else:
                dayList[3] = '1'
        # Thursday
        elif pluginAction.props['action'] == 'thursday_true':
            device.updateStateOnServer('thursday', value='True')
            dayList[4] = '1'
        elif pluginAction.props['action'] == 'thursday_false':
            device.updateStateOnServer('thursday', value='False')
            dayList[4] = '0'
        elif pluginAction.props['action'] == 'thursday_toggle':
            device.updateStateOnServer('thursday', value= not device.states.get('thursday', ''))
            if dayList[4] == '1':
                dayList[4] = '0'
            else:
                dayList[4] = '1'
        # Friday
        elif pluginAction.props['action'] == 'friday_true':
            device.updateStateOnServer('friday', value='True')
            dayList[5] = '1'
        elif pluginAction.props['action'] == 'friday_false':
            device.updateStateOnServer('friday', value='False')
            dayList[5] = '0'
        elif pluginAction.props['action'] == 'friday_toggle':
            device.updateStateOnServer('friday', value= not device.states.get('friday', ''))
            if dayList[5] == '1':
                dayList[5] = '0'
            else:
                dayList[5] = '1'
        # Saturday
        elif pluginAction.props['action'] == 'saturday_true':
            device.updateStateOnServer('saturday', value='True')
            dayList[6] = '1'
        elif pluginAction.props['action'] == 'saturday_false':
            device.updateStateOnServer('saturday', value='False')
            dayList[6] = '0'
        elif pluginAction.props['action'] == 'saturday_toggle':
            device.updateStateOnServer('saturday', value= not device.states.get('saturday', ''))
            if dayList[6] == '1':
                dayList[6] = '0'
            else:
                dayList[6] = '1'
        # Sunday
        elif pluginAction.props['action'] == 'sunday_true':
            device.updateStateOnServer('sunday', value='True')
            dayList[0] = '1'
        elif pluginAction.props['action'] == 'sunday_false':
            device.updateStateOnServer('sunday', value='False')
            dayList[0] = '0'
        elif pluginAction.props['action'] == 'sunday_toggle':
            device.updateStateOnServer('sunday', value= not device.states.get('sunday', ''))
            if dayList[0] == '1':
                dayList[0] = '0'
            else:
                dayList[0] = '1'

        # Update scheduled_days variable
        newDays = ''.join(dayList)
        device.updateStateOnServer('scheduled_days', value=newDays)

        ####
        indigo.server.log(str(device.name))

        self.sleep(.1)

        ####
        indigo.server.log(device.states.get('scheduled_days', ''))
        ####
        for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
            state = device.states.get(day, '')
            indigo.server.log(day + ': ' + str(state))

        ####################################################################################################
        # Update the actual Indigo schedule via Applescript
        ####################################################################################################
        ascript = '''
        tell application "IndigoServer"

        	set theSchedule to time date action named {schedule_name}
        	set date trigger type of theSchedule to specificDays
        	set days of week of theSchedule to {schedule_days}

        end tell
        '''.format(schedule_name = asquote(device.name), schedule_days = asquote(newDays))
        asrun(ascript)

    ####################################################################################################
    # Subscribe to all changes in any Indigo variable value
    ####################################################################################################
    indigo.variables.subscribeToChanges()
    def variableUpdated(self, origVar, newVar):

        # If start Time var changed, run set_scheduled_start_time() to update the actual Indigo schedule
        for var, device in self.start_time_vars.items():
            if var == str(origVar.id):
                self.set_scheduled_start_time(device, device.id)

    ####################################################################################################
    # Set the schedule start time
    ####################################################################################################
    def set_scheduled_start_time(self, device, deviceId):

        scheduleName = indigo.schedules[int(device.pluginProps.get('real_schedule', ''))].name

        newStartTime = indigo.variables[int(device.pluginProps.get('start_time_variable', ''))].value

        timeAddSeconds = list(newStartTime)
        timeAddSeconds.insert(-3, ':00')
        newStartTime = ''.join(timeAddSeconds)

        device.updateStateOnServer('scheduled_start_time', value=newStartTime)

        ascript = '''
        tell application "IndigoServer"

        	set theSchedule to time date action named {schedule_name}
        	set absolute trigger time of theSchedule to date {schedule_start_time}

        end tell
        '''.format(schedule_name = asquote(scheduleName), schedule_start_time = asquote('Thursday, January 1, 2015 at {time}'.format(time=newStartTime)))

        asrun(ascript)

    ####################################################################################################
    # Run Schedule
    ####################################################################################################
    def run_schedule(self, pluginAction):

        deviceId = pluginAction.deviceId
        device = self.device_dict.get(str(deviceId))
        realDevice = int(device.pluginProps.get('realIrrDevice', ''))

        zoneTimesVar = device.pluginProps.get('zone_times_variable', '')
        zoneTimes = indigo.variables[int(zoneTimesVar)].value
        device.updateStateOnServer('zone_times', value=str(zoneTimes))

        zoneTimes = zoneTimes.split(',')

        indigo.server.log(str(device.states.get('zone_times', '')))

        indigo.sprinkler.run(realDevice, schedule=[zoneTimes[0], zoneTimes[1], zoneTimes[2], zoneTimes[3], zoneTimes[4], zoneTimes[5], zoneTimes[6], zoneTimes[7]])

    # def run_single_zone(self, pluginAction):
    #
    #     deviceId = pluginAction.deviceId
    #     device = self.device_dict.get(str(deviceId))
    #     realDevice = int(device.pluginProps.get('realIrrDevice', ''))
