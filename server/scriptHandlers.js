const {
    preAssemblyScripts,
    postAssemblyScripts,
    eStopEvents,
} = require("../eventData.js");
const { transferFile } = require("./util.js");

const runScript = (stream, script, configObject) => {
    if (!configObject.scriptRun) {
        stream.write(`${script.command} ${script.args}\n`);
    }
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
            runScript(stream, script, configObject);
            configObject.scriptRun = true;
        });

        // Add event handlers for the steps in the script
        script.steps.forEach((step) => {
            socket.on(step.socketName, () => {
                step.args = "";
                runScript(stream, step, configObject);
                configObject.scriptRun = true;
            });
        });
    });

    // Handle socket events which manipulate the SSH shell
    postAssemblyScripts.forEach((script) => {
        socket.on(script.socketName, () => {
            runScript(stream, script, configObject);
            configObject.scriptRun = true;
        });

        // Add event handlers for the steps in the script
        script.steps.forEach((step) => {
            socket.on(step.socketName, () => {
                step.args = "";
                runScript(stream, step, configObject);
                configObject.scriptRun = true;
            });
        });
    });

    // Handle all the eStop Events
    eStopEvents.forEach((script) => {
        socket.on(script.socketName, () => {
            runScript(stream, script, configObject);
            configObject.scriptRun = true;
        });
    });

    // Send the script to the MachineMotion and then run it
    socket.on("sendScriptToMM", async (script) => {
        const filePath = "../scripts/unittests/syncRTC.py";

        try {
            await sendScriptToMM(client, filePath);
            stream.write(
                `sudo python3 /var/lib/cloud9/vention-control/${filePath
                    .split("/")
                    .pop()}\n`
            );
        } catch (err) {
            console.error("Error occurred while transferring file:", err);
        }
    });
};

module.exports = { configureScriptHandlers };
