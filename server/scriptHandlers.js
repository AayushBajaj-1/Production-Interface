const {
    preAssemblyScripts,
    postAssemblyScripts,
    servoMotorBurnInTestScripts,
    eStopEvents,
} = require("../eventData.js");

// Run the script on the SSH shell
const runScript = (stream, script, configObject) => {
    if (!configObject.scriptRun) {
        stream.write(`${script.command} ${script.args}\n`);
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

    // Handle socket events which manipulate the SSH shell
    servoMotorBurnInTestScripts.forEach((script) => {
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
};

module.exports = { configureScriptHandlers };
