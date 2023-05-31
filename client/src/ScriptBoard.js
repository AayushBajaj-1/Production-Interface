import * as React from "react";
import { LoadingButton } from "@mui/lab";
import SendIcon from "@mui/icons-material/Send";
import Convert from "ansi-to-html";
import Sidebar from "./Sidebar";
import { postAssemblyScripts, preAssemblyScripts } from "./eventData";

const ScriptBoard = ({
    socket,
    loading,
    setLoading,
    scriptOutput,
    setScriptOutput,
}) => {
    var convert = new Convert();
    const [activeStep, setActiveStep] = React.useState(0);

    const handleNext = () => {
        setActiveStep((prevActiveStep) => prevActiveStep + 1);
    };

    const handleBack = () => {
        setActiveStep((prevActiveStep) => prevActiveStep - 1);
    };

    const handleReset = () => {
        setActiveStep(0);
    };

    const startScript = async () => {
        socket.emit(postAssemblyScripts[activeStep].socketName);
        setScriptOutput("");
        setLoading(true);
    };

    React.useEffect(() => {
        let test = document.getElementById("test");
        test.innerHTML = convert.toHtml(scriptOutput);
    }, [scriptOutput]);

    return (
        <section className="flex flex-col py-10">
            <h1 className="text-lg font-bold">
                Scripts To Run during Production
            </h1>
            <div className="flex">
                <Sidebar
                    activeStep={activeStep}
                    handleNext={handleNext}
                    handleBack={handleBack}
                    handleReset={handleReset}
                />
                <div className="flex-1 ml-20">
                    <p className="mb-5">
                        Click the button below to start running the script
                    </p>
                    <LoadingButton
                        loadingPosition="start"
                        loading={loading}
                        startIcon={<SendIcon />}
                        variant="outlined"
                        onClick={startScript}
                    >
                        Run Script
                    </LoadingButton>
                    <pre
                        id="test"
                        className="p-3 my-5 text-white bg-[#3e3e42] rounded-xl whitespace-pre-wrap"
                    ></pre>
                </div>
            </div>
        </section>
    );
};

export default ScriptBoard;
