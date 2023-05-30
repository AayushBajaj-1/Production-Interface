const scripts = [
    {
        name: "Auto Setup",
        socketName: "runSetup",
        path: "/var/lib/cloud9/vention-control/tests/production_qa_scripts/util/autoSetup.py",
        args: "auto",
    },
    {
        name: "Fct",
        socketName: "runFct",
        path: "/var/lib/cloud9/vention-control/tests/production_qa_scripts/2--fct.py",
        args: "",
    },
];

const runScript = (stream, script) => {
    console.log(`Running ${script.name} script...`);
    stream.write(`sudo python3 ${script.path} ${script.args}\n`);
};

const configureScriptHandlers = (socket, stream, configObject) => {
    // Handle socket events which manipulate the SSH shell
    scripts.forEach((script) => {
        socket.on(script.socketName, () => {
            runScript(stream, script);
            configObject.scriptRun = true;
        });
    });
};

module.exports = { configureScriptHandlers };
