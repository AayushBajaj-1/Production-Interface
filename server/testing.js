const { Client } = require("ssh2");
const readline = require("readline");
const { createServer } = require("http");
const { Server } = require("socket.io");
const express = require("express");

const scriptPath =
    "/var/lib/cloud9/vention-control/tests/production_qa_scripts/util/autoSetup.py";

// SSH connection configuration
const sshConfig = {
    host: "192.168.192.51",
    username: "debian",
    password: "temppwd",
};

// Create a readline interface for reading input from the console
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
});

const app = express();
const server = createServer(app);
const io = new Server(server, {
    cors: {
        origin: "http://localhost:3001", // Replace with the URL of your React app
        methods: ["GET", "POST"],
    },
});

let sshStream;

io.on("connection", (socket) => {
    console.log("Client connected");
    // Start a ssh client
    const ssh = new Client();

    ssh.on("ready", () => {
        console.log("SSH connection established");
        ssh.shell((err, stream) => {
            if (err) {
                ssh.end(); // Close the SSH connection
                socket.emit("error", "Error connecting to SSH");
                socket.disconnect();
                return;
            }

            sshStream = stream;
            // Handle data received from the SSH shell
            stream.on("data", (data) => {
                // If it is an input then ask for the input and write it to the shell
                if (
                    data.indexOf("Input:") !== -1 ||
                    data.indexOf("password for debian:") !== -1
                ) {
                    // If the prompt is detected, write the input
                    // Print data received from the SSH shell
                    console.log(`${data}`);
                    socket.emit("input", data);
                    promptInput();
                } else {
                    // Print data received from the SSH shell
                    console.log(`${data}`);
                    socket.emit("output", data);
                }
            });

            // Handle SSH shell close event
            stream.on("close", () => {
                console.log("SSH shell closed");
                ssh.end(); // Close the SSH connection
                socket.emit("error", "Script execution incomplete");
                socket.disconnect();
            });

            // Prompt for input and pass it to the SSH shell
            function promptInput() {
                rl.question("", (input) => {
                    stream.write(`${input}\n`);
                    promptInput();
                });
            }
        });
    });

    socket.on("start", () => {
        console.log("Starting SSH connection...");
        ssh.connect(sshConfig);
    });

    socket.on("runSetup", () => {
        console.log("Running setup script...");
        sshStream.write(`sudo python3 ${scriptPath} auto\n`);
        sshStream.write(`temppwd\n`);

        setTimeout(() => {
            sshStream.write(`\n`);
        }, 3000);
    });

    socket.on("close", () => {
        sshStream.end();
        ssh.end();
        socket.disconnect();
    });

    // Socket disconnect event
    socket.on("disconnect", () => {
        console.log("Client disconnected");
    });
});

// Start the HTTP server
const port = 3000;
server.listen(port, () => {
    console.log(`Server is running on port ${port}`);
});
