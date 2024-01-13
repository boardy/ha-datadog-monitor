# Introduction
This Python Script allows you to access your Datadog Monitors and flash your lights 
within your Home Assistant setup. This is deployed as docker container

I've mostly built this for myself so set up with some assumptions but thought this
might be useful to some people as well so open sourced. 

# Setting up Home Assistant
One of the assumptions is, you want to flash one or more lights when the Datadog monitor
status changes. I've done this by creating Helpers within home assistant 
(Settings > Devices > Helpers).

Within home assistant create a light group and assign all the lights you want to control within
this script to the group. Then add this entity as environment variable 
called `ha_entity_to_update`. More info on the environment variables below. 

Then in home assistant you need a long-lived token. This can be done by clicking
on your name in the bottom left corner sidebar, scrolldown to long-lived token 
and create a new token. Create a new token and copy it as environment 
variable called `ha_auth_token`.

# Set up Datadog
Log in to your Datadog account, go to the bottom left where your email is displayed
and go to Organisation Settings. On the left side bar go to API keys and create a new
API key and copy the value as environment variable called `dd_api_key`

Then in the sidebar go to Application Keys and create a new app key and paste the 
value as an environment variable called `dd_app_key`. 

# Getting the Docker Image
It needs to run from somewhere where docker is supported. Run the command
`docker pull chrisfromdevso/ha-datadog-monitor:latest`

You can also use this from Unraid servers. Ensure that community apps 
is installed and then search for ha-datadog-monitor, nothing will come back but there
will be a link to say, look in the docker hub registry. Click that and select install. 

# Environment Variables
**The following environment variables need to be injected in to your docker image**

* **alert_active_hours_only:** Should the lights only flash during active hours
* **alert_start_active_hours:** The start of active hours when the lights flash if
alert_active_hours_only is true. Defaults to 09:00, should be in 24 hour format
such as HH:mm
* **alert_end_active_hours:** The end of active hours when the lights flash if 
alert_active_hours_only is true. Defaults to 09:00, should be in 24 hour format
such as HH:mm
* **alert_cycle_time:** How often the datadog monitors should be checked. Defaults to 60 seconds
* **dd_api_key:** Your API key from your Datadog account
* **dd_app_key:** Your App Key from your Datadog account
* **ha_auth_token:** The long-lived token created in your Home Assistant Instance
* **ha_base_url:** The base URL to your home assistant instance, should include /api
such as http://localhost:8123/api
* **ha_entity_to_update:** The entity light group to update (created as a helper device) 

## Note about active hours
If active hours is enabled, the lights only flash during the active hours,
so you don't get woken up at 3am. 

If an alert happens during the night, the lights will flash at the next cycle when 
active hours starts. 

*Chris Board or Devso can take no responsibility for any unexpected or unintended 
additional costs from your Datadog Account or any unexpected or unintended 
damage to your devices or property.* 

*This is provided as is and there are no guarantees or warranties associated 
with this project*
