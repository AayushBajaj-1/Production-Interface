import React from "react";
import SendIcon from "@mui/icons-material/Send";
import ReportProblemIcon from "@mui/icons-material/ReportProblem";
import RestartAltIcon from "@mui/icons-material/RestartAlt";
import { LoadingButton } from "@mui/lab";
import { useSocket } from "../context/SocketContext";
import { useMQTT, NetworkProps } from "../context/MqttContext";

const Topbar = () => {
    const {
        triggerEStop,
        testSend,
        releaseEStop,
        sendStart,
        connected,
        scriptRunning,
    } = useSocket();
    const { estop, network } = useMQTT();

    return (
        <>
            <section className="flex justify-between w-full mb-5">
                {connected && (
                    <>
                        <div>
                            <div className="flex">
                                <p className="mr-5">MachineMotion</p>
                                <p>
                                    sw: {network?.sw_version}, hw:{" "}
                                    {network?.hw_version}, serial no:{" "}
                                    {network?.serial_no}
                                </p>
                            </div>
                        </div>
                        <div>
                            <div className="flex justify-center items-center">
                                <p className="mr-5">Estop Status:</p>
                                <svg
                                    height="20"
                                    width="20"
                                    className={`${
                                        estop === "true"
                                            ? "fill-red-500"
                                            : "fill-green-500"
                                    } rounded-full`}
                                >
                                    <circle
                                        cx="10"
                                        cy="10"
                                        r="8"
                                        strokeWidth="1"
                                    />
                                </svg>
                            </div>
                        </div>
                    </>
                )}
            </section>
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
                                disabled={estop === "true"}
                                loading={scriptRunning}
                                className="mx-2 text-white bg-red-500 disabled:bg-gray-800"
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
                                disabled={estop === "false"}
                                loading={scriptRunning}
                                style={{
                                    backgroundColor: "#F4B73A",
                                    color: "white",
                                }}
                                className="mx-2 text-white bg-yellow-500 disabled:bg-gray-800"
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
                    <button onClick={testSend}>Testing</button>
                </div>
            </section>
        </>
    );
};

export default Topbar;
