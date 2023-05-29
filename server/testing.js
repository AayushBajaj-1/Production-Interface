const { Client } = require("ssh2");
const { spawn } = require("node-pty");
const readline = require("readline");
const express = require("express");
const cors = require("cors");

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

// Start a ssh client
const ssh = new Client();
let sshStream;

const app = express();
app.use(cors());

ssh.on("ready", () => {
    console.log("SSH connection established");
    ssh.shell((err, stream) => {
        if (err) throw err;

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
                promptInput();
            } else {
                // Print data received from the SSH shell
                console.log(`${data}`);
            }
        });

        // Handle SSH shell close event
        stream.on("close", () => {
            console.log("SSH shell closed");
            ssh.end(); // Close the SSH connection
            //process.exit(); // Exit the Node.js process
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

app.get("/client/run", (req, res) => {
    sshStream.write(`sudo python3 ${scriptPath} auto\n`);
    sshStream.write(`temppwd\n`);
    setTimeout(() => {
        sshStream.write(`\n`);
    }, 3000);
    res.send(`Running the script in the background`);
});

app.get("/client/close", (req, res) => {
    ssh.end(); // Close the SSH connection
    res.send({
        message: "Successfully closed the connection",
    });
});

app.get("/client/open", (req, res) => {
    ssh.connect(sshConfig); // Close the SSH connection
    setTimeout(() => {
        res.send({
            message: "Successfully opened the connection",
        });
    }, 2000);
});

app.listen(3000, () => {
    console.log("Server is running on port 3000");
});
