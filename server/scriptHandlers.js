const {
    preAssemblyScripts,
    postAssemblyScripts,
    eStopEvents,
} = require("../eventData.js");

const runScript = (stream, script) => {
    console.log(`Running ${script.name} script...`);
    stream.write(`${script.command} ${script.args}\n`);
};

const configureScriptHandlers = (socket, stream, configObject) => {
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
};

module.exports = { configureScriptHandlers };
