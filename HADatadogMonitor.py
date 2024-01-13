import time
import os
from HAManager import HAManager
from DDManager import DDManager
import configparser
import json

config = configparser.ConfigParser()
config.read('config.ini')

entities = os.getenv('ha_entity_to_update', default='')
cycle_time = os.getenv('alerting_cycle_time', default=60)

if entities == '':
    print("entity_to_update not configured as environment variable")


while True:
    ha_manager = HAManager()
    dd_manager = DDManager()

    # Will perform check with Datadog here, first just try flashing the lights and restore state
    monitor_status = dd_manager.returnDatadogStatus()

    ok_count = monitor_status["ok_count"]
    warn_count = monitor_status["warn_count"]
    alert_count = monitor_status["alert_count"]

    with open('alert_count.json') as json_file:
        counts_json = json.load(json_file)

    file_warn_counts = counts_json['warn_count']
    file_alert_counts = counts_json['alert_count']

    were_lights_updated = False

    if warn_count > 0 or alert_count > 0:
        # Check the alert_count.json file, if the counts in the file are 0, not previously alerted so flash the lights

        if file_warn_counts == 0 and file_alert_counts == 0:
            # Need to flash the lights - check what the wost alert level is
            if alert_count > 0:
                # Need to flash the lights red
                print("Flashing philips hue to be red")
                were_lights_updated = ha_manager.flash_lights(entity=entities, color="RED")
            elif warn_count > 0:
                # Need to flash the lights orange
                print("Flashing philips hue to be orange")
                were_lights_updated = ha_manager.flash_lights(entity=entities, color="YELLOW")
        elif file_warn_counts > 0 or file_alert_counts > 0:
            if file_alert_counts > 0 and alert_count == 0 and warn_count > 0:
                # If here, then previously alerted red but red alert recovered and now on warning
                # so flash philips hue orange instead
                print("alert recovered so flashing orange instead")
                were_lights_updated = ha_manager.flash_lights(entity=entities, color="ORANGE")
            elif (file_alert_counts > 0 or file_warn_counts) and (alert_count > 0 or warn_count > 0):
                # The file has some alerts and warning counts and there are still current alert and warning
                # counts so don't do anything with the lights
                print("no alerts and warnings recovered so not flashing the lights")
        else:
            print("Previously alerted and alerts are still happening so don't do anything with lights")

    else:
        # There are no warnings and no errors check the file counts, if any are over 0, the monitors are therefore
        # recovered so flash green
        if file_alert_counts > 0 or file_warn_counts > 0:
            # The file did have an alert count the last time it run, so flash the lights green
            print("Everything recovered so flash lights green")
            were_lights_updated = ha_manager.flash_lights(entity=entities, color="GREEN")

    if were_lights_updated:
        # Save a JSON file of the current counts. This will be used so that if the file already shows the counts for non OK
        # are > 1 so don't inadvertently keep flashing the users lights
        counts_json = '{"warn_count": ' + str(warn_count) + ', "alert_count":' + str(alert_count) + '}'
        f = open("alert_count.json", "w")
        f.write(counts_json)
        f.close()

    time.sleep(cycle_time)

exit(0)