from datadog import initialize, api
import json
import configparser
import os

api_key = ''
app_key = ''


class DDManager():
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')

        self.api_key = os.getenv('dd_api_key', default='')
        self.app_key = os.getenv('dd_app_key', default='')

        if self.api_key == '':
            print("Datadog dd_api_key is not defined as environment variable")
            exit(1)

        if self.app_key == '':
            print("Datadog dd_app_key is not defined as environment variable")
            exit(1)

        pass

    def returnDatadogStatus(self):
        print("Checking datadog status")

        # Check if the count file exists if not create a default one
        try:
            f = open("alert_count.json")
        except IOError:
            counts_json = '{"warn_count": 0, "alert_count": 0}'
            f = open("alert_count.json", "w")
            f.write(counts_json)
            f.close()

        dd_options = {
            'api_key': self.api_key,
            'app_key': self.app_key
        }

        initialize(**dd_options)

        monitors = api.Monitor.get_all()

        alert_count = 0
        warn_count = 0
        ok_count = 0

        for monitor in monitors:
            monitorName = monitor['name']
            monitorStatus = monitor['overall_state']
            if monitorStatus == 'OK':
                ok_count += 1
            elif monitorStatus == 'Alert':
                alert_count += 1
            elif monitorStatus == 'Warn':
                warn_count += 1

            print('Monitor Name: ' + monitorName + " Status: " + monitorStatus)

        print("OK Count: " + str(ok_count))
        print("Warn Count: " + str(warn_count))
        print("Alert Count: " + str(alert_count))

        return {
            'ok_count': ok_count,
            'warn_count': warn_count,
            'alert_count': alert_count
        }

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
                    were_lights_updated = self.ha_manager.flash_lights(entity=self.entities, color="RED")
                elif warn_count > 0:
                    # Need to flash the lights orange
                    print("Flashing philips hue to be orange")
                    were_lights_updated = self.ha_manager.flash_lights(entity=self.entities, color="ORANGE")
            elif file_warn_counts > 0 or file_alert_counts > 0:
                if file_alert_counts > 0 and alert_count == 0 and warn_count > 0:
                    # If here, then previously alerted red but red alert recovered and now on warning
                    # so flash philips hue orange instead
                    print("alert recovered so flashing orange instead")
                    were_lights_updated = self.ha_manager.flash_lights(entity=self.entities, color="ORANGE")
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
                were_lights_updated = self.ha_manager.flash_lights(entity=self.entities, color="GREEN")