require("dotenv").config();

const { configureScriptHandlers } = require("./scriptHandlers");

// Handle the shell
const shellHandler = (sshClient, socket) => {
    sshClient.shell((err, stream) => {
        // Variable to keep track of the script run status
        let configObject = {
            scriptRun: false,
        };

        socket.emit("connected");

        if (err) {
            stream.end();
            return;
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

        stream.write("cd /var/lib/cloud9/vention-control\n");
    });
};

// Handling the stream received from the SSH shell
const shellDataHandler = (socket, stream, data, configObject) => {
    // If the script is asking for an input
    if (data.indexOf("Input:") !== -1) {
        socket.emit("input", data);
        return;
    }

    // Get the success or error of the script
    if (data.indexOf(`AssertionError:`) !== -1) {
        // get the number from the string
        socket.emit("script:error");
        socket.emit("output", data);
        return;
    }

    // Get the success or error of the script
    if (data.indexOf(`OK`) !== -1) {
        // get the number from the string
        socket.emit("script:success");
        socket.emit("output", data);
        return;
    }

    // If the script is finished running ( when finished the shell will print "debian@MachineMotionV2" )
    if (
        data.indexOf(`${process.env.HOSTNAME}@MachineMotionV2`) !== -1 &&
        configObject.scriptRun
    ) {
        socket.emit("completion", data);
        socket.emit("output", data);
        configObject.scriptRun = false;
        return;
    }

    // If the script is asking for a password enter the password
    if (data.indexOf(`[sudo] password for ${process.env.HOSTNAME}`) !== -1) {
        stream.write(`${process.env.PASSWORD}\n`);
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
