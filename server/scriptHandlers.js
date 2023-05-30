const runAutoSetup = (stream) => {
    const scriptPath =
        "/var/lib/cloud9/vention-control/tests/production_qa_scripts/util/autoSetup.py";

    console.log("Running setup script...");
    stream.write(`sudo python3 ${scriptPath} auto\n`);
};

const runFct = (stream) => {
    const scriptPath =
        "/var/lib/cloud9/vention-control/tests/production_qa_scripts/2--fct.py";

    console.log("Running setup script...");
    stream.write(`sudo python3 ${scriptPath}\n`);
};

const configureScriptHandlers = (socket, stream, configObject) => {
    // Handle socket events which manipulate the SSH shell
    socket.on("runSetup", () => {
        runAutoSetup(stream);
        configObject.scriptRun = true;
    });

    // Handle socket events which manipulate the SSH shell
    socket.on("runFct", () => {
        runFct(stream);
        configObject.scriptRun = true;
    });
};

module.exports = { runAutoSetup, runFct, configureScriptHandlers };
