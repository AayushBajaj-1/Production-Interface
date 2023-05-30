const { shellHandler } = require("./shellHandlers");

// Main SSH client event handlers
const configureSShHandlers = (sshClient, socket) => {
    sshClient.on("ready", () => {
        console.log("SSH connection established");
        shellHandler(sshClient, socket);
    });
};

module.exports = { configureSShHandlers };
