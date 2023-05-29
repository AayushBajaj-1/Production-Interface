import * as React from "react";
import Box from "@mui/material/Box";
import Stepper from "@mui/material/Stepper";
import Step from "@mui/material/Step";
import StepLabel from "@mui/material/StepLabel";
import StepContent from "@mui/material/StepContent";
import Button from "@mui/material/Button";
import Paper from "@mui/material/Paper";
import Typography from "@mui/material/Typography";

const steps = [
    {
        label: "Run AutoSetup",
        description: `Checking EEPROM etc...`,
    },
    {
        label: "Run Pre Functional ",
        description: `Checking EEPROM etc...`,
    },
    {
        label: "Run the servomotor test",
        description:
            "Connect the MM to the motors and leave it for 45 minutes to make sure.....",
    },
    {
        label: "Run the Functional Script",
        description: `Try out different ad text to see what brings in the most customers,
              and learn how to enhance your ads using features like ad extensions.
              If you run into any problems with your ads, find out how to tell if
              they're running and how to resolve approval issues.`,
    },
];

function VerticalLinearStepper({
    activeStep,
    handleNext,
    handleBack,
    handleReset,
}) {
    return (
        <Box sx={{ maxWidth: 400 }}>
            <Stepper activeStep={activeStep} orientation="vertical">
                {steps.map((step, index) => (
                    <Step key={step.label}>
                        <StepLabel
                            optional={
                                index === 2 ? (
                                    <Typography variant="caption">
                                        Last step
                                    </Typography>
                                ) : null
                            }
                        >
                            {step.label}
                        </StepLabel>
                        <StepContent>
                            <Typography>{step.description}</Typography>
                            <Box sx={{ mb: 2 }}>
                                <div>
                                    <Button
                                        variant="contained"
                                        onClick={handleNext}
                                        sx={{ mt: 1, mr: 1 }}
                                    >
                                        {index === steps.length - 1
                                            ? "Finish"
                                            : "Continue"}
                                    </Button>
                                    <Button
                                        disabled={index === 0}
                                        onClick={handleBack}
                                        sx={{ mt: 1, mr: 1 }}
                                    >
                                        Back
                                    </Button>
                                </div>
                            </Box>
                        </StepContent>
                    </Step>
                ))}
            </Stepper>
            {activeStep === steps.length && (
                <Paper square elevation={0} sx={{ p: 3 }}>
                    <Typography>
                        All steps completed - you&apos;re finished
                    </Typography>
                    <Button onClick={handleReset} sx={{ mt: 1, mr: 1 }}>
                        Reset
                    </Button>
                </Paper>
            )}
        </Box>
    );
}
const ScriptBoard = () => {
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
        try {
            await fetch("http://localhost:3000/client/run", {
                method: "GET",
            });
        } catch (err) {
            console.log(err);
        }
    };

    return (
        <section className="py-10 flex flex-col">
            <h1 className="text-lg font-bold">
                Scripts To Run during Production
            </h1>
            <div className="flex">
                <VerticalLinearStepper
                    activeStep={activeStep}
                    handleNext={handleNext}
                    handleBack={handleBack}
                    handleReset={handleReset}
                />
                <div className="ml-20">
                    <p className="mb-5">
                        Click the button below to start running the script
                    </p>
                    <Button
                        onClick={startScript}
                        className="h-[40px]"
                        variant="contained"
                    >
                        Run the Script
                    </Button>
                </div>
            </div>
        </section>
    );
};

export default ScriptBoard;
