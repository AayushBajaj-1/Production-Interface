import * as React from "react";
import { LoadingButton } from "@mui/lab";
import SendIcon from "@mui/icons-material/Send";
import CancelIcon from "@mui/icons-material/Cancel";
import Convert from "ansi-to-html";
// @ts-ignore
import { postAssemblyScripts, preAssemblyScripts } from "eventData";
import { useSocket } from "../context/SocketContext";
import Sidebar from "./Sidebar";
import InputLabel from "@mui/material/InputLabel";
import MenuItem from "@mui/material/MenuItem";
import FormControl from "@mui/material/FormControl";
import Select from "@mui/material/Select";

const ScriptBoard = () => {
    const {
        socket,
        scriptRunning,
        setScriptRunning,
        scriptOutput,
        setScriptOutput,
    } = useSocket();

    const [activeStep, setActiveStep] = React.useState(0);
    const [scripts, setScripts] = React.useState(preAssemblyScripts);

    const handleChange = (event: any) => {
        if (event.target.value === "pre") {
            setScripts(preAssemblyScripts);
        } else {
            setScripts(postAssemblyScripts);
        }
    };

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
        socket?.emit(scripts[activeStep].socketName);
        setScriptOutput("");
        setScriptRunning(true);
    };

    const stopScript = async () => {
        socket?.emit("stopScript");
        setScriptRunning(false);
    };

    const convert = new Convert();

    React.useEffect(() => {
        let test = document.getElementById("test") as HTMLPreElement;
        test.innerHTML = convert.toHtml(scriptOutput);
        // Remove the ?2004h and ?2004l from the output, cleanup for the data
        test.innerHTML = test.innerHTML.replace(/\?2004h/g, "");
        test.innerHTML = test.innerHTML.replace(/\?2004l/g, "");
    }, [scriptOutput]);

    return (
        <section className="flex flex-col py-10">
            <FormControl sx={{ m: 1, maxWidth: 320 }} size="small">
                <InputLabel id="demo-select-small-label">Procedure</InputLabel>
                <Select
                    labelId="demo-select-small-label"
                    id="demo-select-small"
                    label="Procedure"
                    defaultValue={"pre"}
                    onChange={handleChange}
                >
                    <MenuItem value={"pre"}>Pre-Assembly</MenuItem>
                    <MenuItem value={"post"}>Post-Assembly</MenuItem>
                </Select>
            </FormControl>
            <h1 className="text-lg font-bold">
                Scripts To Run during Production
            </h1>
            <div className="flex">
                <Sidebar
                    scripts={scripts}
                    activeStep={activeStep}
                    handleNext={handleNext}
                    handleBack={handleBack}
                    handleReset={handleReset}
                />
                <div className="flex-1 ml-20">
                    <p className="mb-5">
                        Click the button below to start running the script
                    </p>
                    <div className="flex gap-3">
                        <LoadingButton
                            loadingPosition="start"
                            loading={scriptRunning}
                            startIcon={<SendIcon />}
                            variant="outlined"
                            onClick={startScript}
                        >
                            Run All Tests
                        </LoadingButton>
                        <LoadingButton
                            loadingPosition="start"
                            startIcon={<CancelIcon />}
                            variant="outlined"
                            onClick={stopScript}
                        >
                            Stop Script
                        </LoadingButton>
                    </div>
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
