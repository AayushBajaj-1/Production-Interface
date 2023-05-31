import React from "react";
import Box from "@mui/material/Box";
import Stepper from "@mui/material/Stepper";
import Step from "@mui/material/Step";
import StepLabel from "@mui/material/StepLabel";
import StepContent from "@mui/material/StepContent";
import Button from "@mui/material/Button";
import Paper from "@mui/material/Paper";
import Typography from "@mui/material/Typography";
import { postAssemblyScripts, preAssemblyScripts } from "./eventData";

function Sidebar({ activeStep, handleNext, handleBack, handleReset }) {
    return (
        <Box sx={{ maxWidth: 400 }}>
            <Stepper activeStep={activeStep} orientation="vertical">
                {postAssemblyScripts.map((step, index) => (
                    <Step key={step.name}>
                        <StepLabel
                            optional={
                                index === 2 ? (
                                    <Typography variant="caption">
                                        Last step
                                    </Typography>
                                ) : null
                            }
                        >
                            {step.name}
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
                                        {index ===
                                        postAssemblyScripts.length - 1
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
            {activeStep === postAssemblyScripts.length && (
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

export default Sidebar;
