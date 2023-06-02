# Get the latest log file for machineMotion
LOGFILE=$(ls -t /var/lib/cloud9/vention-control/machineMotion/logs | grep machine-cloud-machine-motion-client | head -n 1)

# Get the time at which the program was run
echo "Time at which the client was run:" $(date +"%T")
var1=$(date +"%T")
var2=""

# Check 3 times as machineCloud might take some time to connect to the server
for i in {1..3}
do
    # Get the latest log file for machineMotion
    echo -e "Checking the latest log file:" $LOGFILE "\n"

    # Search the last 1000 lines of the log file and find if there is a connection established
    RESULT=$(tail -n 1000 /var/lib/cloud9/vention-control/machineMotion/logs/$LOGFILE | grep "Client registered on cloud server" | tail -n 1)

    # Convert to array, delimited by space
    TIME=(${RESULT})

    # Get the time
    var2=${TIME[1]}

    # If a time was found then break
    if [[ $var2 != "" ]]; then
        echo -e "Time found!"
        break
    fi

    # Wait 5 seconds before every try
    sleep 5
done

# If no time was found then that means there was no connection to the server
if [[ $var2 == "" ]]; then
    exit 1
fi

# Convert to epoch time and calculate difference.
difference=$(( $(date -d "$var1" "+%s") - $(date -d "$var2" "+%s") ))

# Divide the difference by 60 to calculate minutes.
TIME_DIFF=$(( $difference/60 ))

# If the time difference is greater than 5 minutes
if (( $TIME_DIFF > 5 )); then
    echo -e "A recent connection to machineCloud was not found! \n"
    exit 1
fi

echo -e "Connection to the server is established! \n"
exit 0