require("dotenv").config();
const { sendFolderViaSFTP } = require("./util.js");
const { configureScriptHandlers } = require("./scriptHandlers");

const scriptsSent = false;

// Send the scripts to the machine motion
const sendScriptsToMM = async () => {
    const localFilePath = "../production_qa_scripts/"; // Replace with your local file path
    const remoteFilePath = `/var/lib/cloud9/vention-control/tests/production_qa_scripts/`;

    try {
        await sendFolderViaSFTP(localFilePath, remoteFilePath);
    } catch (err) {
        console.error("Error occurred while transferring file:", err);
    }
};

// Handle the shell
const shellHandler = (sshClient, socket) => {
    sshClient.shell(async (err, stream) => {
        // Variable to keep track of the script run status
        let configObject = {
            scriptRun: false,
        };

        socket.emit("connected");

        if (err) {
            stream.end();
            return;
        }

        // If there is no error then send the scripts to the MM
        if (!scriptsSent) {
            try {
                await sendScriptsToMM();
                stream.write(
                    "cd /var/lib/cloud9/vention-control/tests/production_qa_scripts\n"
                );
            } catch (err) {
                console.error("Error occurred while transferring file:", err);
            }
        }

        // Handle the running of the scripts
        configureScriptHandlers(sshClient, socket, stream, configObject);

        // Handle data received from the SSH shell
        stream.on("data", (data) => {
            console.log(data.toString());
            shellDataHandler(socket, stream, data, configObject);
        });

        // Handle SSH shell close event
        stream.on("close", () => {
            shellCloseHandler(socket);
        });

        socket.on("inputReceived", (data) => {
            stream.write(`${data}\n`);
        });

        socket.on("stopScript", () => {
            // Write control + c to the shell
            stream.write("\x03");
        });
    });
};

// Handling the stream received from the SSH shell
const shellDataHandler = (socket, stream, data, configObject) => {
    // If the script is asking for a password enter the password
    if (data.indexOf(`[sudo] password for ${process.env.HOSTNAME}`) !== -1) {
        stream.write(`${process.env.PASSWORD}\n`);
        return;
    }

    // If the script is asking for an input
    if (data.indexOf("Input:") !== -1) {
        socket.emit("input", data);
        return;
    }

    // Get the error of the script
    if (data.indexOf(`FAILED`) !== -1 && configObject.scriptRun) {
        // get the number from the string
        socket.emit("completion", data);
        socket.emit("script:error");
        socket.emit("output", data);
        configObject.scriptRun = false;
        return;
    }

    // Get the success of the script
    if (data.indexOf(`OK`) !== -1 && configObject.scriptRun) {
        // get the number from the string
        socket.emit("completion", data);
        socket.emit("script:success");
        socket.emit("output", data);
        configObject.scriptRun = false;
        return;
    }

    if (
        data.indexOf(`${process.env.HOSTNAME}@MachineMotionV2`) !== -1 &&
        configObject.scriptRun
    ) {
        socket.emit("completion", data);
        socket.emit("output", data);
        configObject.scriptRun = false;
        return;
    }

    socket.emit("output", data);
};

// Handle the shell close event
const shellCloseHandler = () => {
    console.log("SSH shell closed");
    // Send a socket event to the client
    socket.emit("disconnected");
};

module.exports = { shellHandler };
