import * as React from "react";
import { LoadingButton } from "@mui/lab";
import SendIcon from "@mui/icons-material/Send";
import { useSocket } from "../context/SocketContext";
import { useConsole } from "../context/ConsoleContext";
import Sidebar from "./Sidebar";
import InputLabel from "@mui/material/InputLabel";
import MenuItem from "@mui/material/MenuItem";
import FormControl from "@mui/material/FormControl";
import Select from "@mui/material/Select";
import {
    postAssemblyScripts,
    preAssemblyScripts,
    servoMotorBurnInTestScripts,
    // @ts-ignore
} from "eventData";

type stepType = {
    name: string;
    socketName: string;
    command: string;
};

const ScriptBoard = () => {
    const { socket, scriptRunning, setScriptRunning, setScriptOutput } =
        useSocket();
    const { handleDialogOpen } = useConsole();

    const [activeStep, setActiveStep] = React.useState(0);
    const [scripts, setScripts] = React.useState(preAssemblyScripts);

    const handleChange = (event: any) => {
        if (event.target.value === "pre") {
            setScripts(preAssemblyScripts);
        } else if (event.target.value === "post") {
            setScripts(postAssemblyScripts);
        } else if (event.target.value === "servo") {
            setScripts(servoMotorBurnInTestScripts);
        }
        setActiveStep(0);
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
        handleDialogOpen();
        socket?.emit(scripts[activeStep].socketName);
        setScriptOutput("");
        setScriptRunning(true);
    };

    const startSubScript = async (socketName: string) => {
        console.log("Starting the sub script", socketName);
        handleDialogOpen();
        socket?.emit(socketName);
        setScriptOutput("");
        setScriptRunning(true);
    };

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
                    <MenuItem value={"servo"}>ServoMotor</MenuItem>
                </Select>
            </FormControl>
            <h1 className="text-lg font-bold">
                Scripts To Run during Production
            </h1>
            <div className="flex pt-2">
                <Sidebar
                    scripts={scripts}
                    activeStep={activeStep}
                    handleNext={handleNext}
                    handleBack={handleBack}
                    handleReset={handleReset}
                />
                <div className="flex-1 ml-20">
                    <p className="mb-5">
                        Click the button below to Run all the steps
                    </p>

                    <LoadingButton
                        loadingPosition="start"
                        loading={scriptRunning}
                        startIcon={<SendIcon />}
                        variant="outlined"
                        onClick={startScript}
                    >
                        Run All Tests
                    </LoadingButton>
                    <div className="flex flex-col gap-4 mt-5">
                        {scripts[activeStep]?.steps?.map(
                            (step: stepType, index: number) => (
                                <div>
                                    <div className="flex items-center mb-4">
                                        {/* Make a circle with the index number */}
                                        <div className="flex items-center justify-center w-6 h-6 m-0 mr-4 font-bold text-white bg-[#1976d2] rounded-full">
                                            {index + 1}
                                        </div>
                                        <p className="text-lg font-bold">
                                            {step.name}
                                        </p>
                                    </div>
                                    <LoadingButton
                                        key={index}
                                        loadingPosition="start"
                                        className="max-w-[200px]"
                                        loading={scriptRunning}
                                        startIcon={<SendIcon />}
                                        variant="outlined"
                                        onClick={() => {
                                            startSubScript(step.socketName);
                                        }}
                                    >
                                        Run Script
                                    </LoadingButton>
                                </div>
                            )
                        )}
                    </div>
                </div>
            </div>
        </section>
    );
};

export default ScriptBoard;
