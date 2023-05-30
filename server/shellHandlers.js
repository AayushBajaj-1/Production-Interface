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
        configureScriptHandlers(socket, stream, configObject);

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
    });
};

// Handling the stream received from the SSH shell
const shellDataHandler = (socket, stream, data, configObject) => {
    // If the script is asking for an input
    if (data.indexOf("Input:") !== -1) {
        socket.emit("input", data);
        return;
    }

    // If the script is finished running ( when finished the shell will print "debian@MachineMotionV2" )
    if (
        data.indexOf(`${process.env.HOSTNAME}@MachineMotionV2`) !== -1 &&
        configObject.scriptRun
    ) {
        socket.emit("completion", data);
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
