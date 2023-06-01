# Kill the machine-cloud service
sudo python3 $DIR_UTIL/kill_service.py 'start-machine-cloud-client-daemon-on-machine-motion\|main.js'

# Remove the log files for machine-cloud
find $DIR_LOGS | grep machine-cloud-machine-motion-client | sudo xargs rm -fr