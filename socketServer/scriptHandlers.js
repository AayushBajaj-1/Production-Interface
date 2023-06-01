const {
    preAssemblyScripts,
    postAssemblyScripts,
    eStopEvents,
} = require("../eventData.js");
const { transferFile } = require("./util.js");

const runScript = (stream, script) => {
    console.log(`Running ${script.name} script...`);
    stream.write(`${script.command} ${script.args}\n`);
};

const sendScriptToMM = async (client, path) => {
    const localFilePath = path; // Replace with your local file path
    const fileName = localFilePath.split("/").pop();
    const remoteFilePath = `/var/lib/cloud9/vention-control/${fileName}`;

    try {
        await transferFile(client, localFilePath, remoteFilePath);
    } catch (err) {
        console.error("Error occurred while transferring file:", err);
    }
};

const configureScriptHandlers = (client, socket, stream, configObject) => {
    // Handle socket events which manipulate the SSH shell
    preAssemblyScripts.forEach((script) => {
        socket.on(script.socketName, () => {
            runScript(stream, script);
            configObject.scriptRun = true;
        });
    });

    // Handle socket events which manipulate the SSH shell
    postAssemblyScripts.forEach((script) => {
        socket.on(script.socketName, () => {
            runScript(stream, script);
            configObject.scriptRun = true;
        });
    });

    // Handle all the eStop Events
    eStopEvents.forEach((script) => {
        socket.on(script.socketName, () => {
            runScript(stream, script);
            configObject.scriptRun = true;
        });
    });

    socket.on("sendScriptToMM", async () => {
        const filePath = "../scripts/unittests/syncRTC.py";
        await sendScriptToMM(client, filePath);
        stream.write(
            `sudo python3 /var/lib/cloud9/vention-control/${filePath
                .split("/")
                .pop()}\n`
        );
    });
};

module.exports = { configureScriptHandlers };
