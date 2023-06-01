import React from "react";
import SendIcon from "@mui/icons-material/Send";
import ReportProblemIcon from "@mui/icons-material/ReportProblem";
import RestartAltIcon from "@mui/icons-material/RestartAlt";
import { LoadingButton } from "@mui/lab";
import { useSocket } from "./SocketContext";

const Topbar = () => {
    const { triggerEStop, releaseEStop, sendStart, connected, scriptRunning } =
        useSocket();

    return (
        <section className="flex justify-between w-full">
            <div>MachineMotion Connection</div>
            <div className="flex gap-3">
                {connected && (
                    <>
                        <LoadingButton
                            loadingPosition="start"
                            startIcon={<ReportProblemIcon />}
                            variant="outlined"
                            onClick={triggerEStop}
                            disabled={scriptRunning}
                            loading={scriptRunning}
                            className="mx-2 text-white bg-red-500"
                            style={{
                                backgroundColor: "red",
                                color: "#fff",
                            }}
                        >
                            Estop
                        </LoadingButton>
                        <LoadingButton
                            loadingPosition="start"
                            startIcon={<RestartAltIcon />}
                            variant="outlined"
                            onClick={releaseEStop}
                            disabled={scriptRunning}
                            loading={scriptRunning}
                            style={{
                                backgroundColor: "#F4B73A",
                                color: "white",
                            }}
                            className="mx-2 text-white bg-yellow-500"
                        >
                            Release
                        </LoadingButton>
                    </>
                )}

                <LoadingButton
                    loadingPosition="start"
                    startIcon={<SendIcon />}
                    variant="outlined"
                    onClick={sendStart}
                    disabled={connected}
                    style={{
                        backgroundColor: connected ? "#4caf50" : "#f44336",
                        color: "#fff",
                        borderColor: connected ? "#4caf50" : "#f44336",
                    }}
                >
                    Connect to MachineMotion
                </LoadingButton>
            </div>
        </section>
    );
};

export default Topbar;
