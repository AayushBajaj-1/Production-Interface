const { Client } = require("ssh2");
const { configureSShHandlers } = require("./sshHandlers");
const { configureMQTTHandlers } = require("./mqttHandlers");
require("dotenv").config();

// SSH connection configuration
const sshConfig = {
    host: process.env.IP,
    username: process.env.HOSTNAME,
    password: process.env.PASSWORD,
};

// Event handlers for the socket io connection
const configureIOEventHandlers = (io) => {
    io.on("connection", (socket) => {
        console.log("Client connected");

        // Start a ssh client
        const sshClient = new Client();

        // Configure SSH Based event handlers
        configureSShHandlers(sshClient, socket);

        // Start a new SSH session on "start" event
        socket.on("start", () => {
            configureMQTTHandlers(socket);
            sshClient.connect(sshConfig);
        });

        // Handle socket close event
        socket.on("close", () => {
            sshClient.end();
            socket.disconnect();
        });

        socket.on("error", (error) => {
            console.log(error);
        });

        // Socket disconnect event
        socket.on("disconnect", () => {
            console.log("Client disconnected");
        });
    });
};

module.exports = { configureIOEventHandlers };
