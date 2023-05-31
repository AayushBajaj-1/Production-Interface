import React, { useState } from "react";
import SendIcon from "@mui/icons-material/Send";
import { LoadingButton } from "@mui/lab";
import { useSocket } from "./SocketContext";

const Topbar = ({ sendStart }) => {
    const { socket, connected } = useSocket();
    const [eStopStatus, setEStopStatus] = useState(false);

    const triggerEStop = () => {
        socket.emit("eStop:trigger");
    };

    const releaseEStop = () => {
        socket.emit("eStop:release");
    };

    return (
        <section className="flex justify-between w-full">
            <div>MachineMotion Connection</div>
            <div className="flex gap-3">
                <LoadingButton
                    loadingPosition="start"
                    startIcon={<SendIcon />}
                    variant="outlined"
                    onClick={triggerEStop}
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
                    startIcon={<SendIcon />}
                    variant="outlined"
                    onClick={triggerEStop}
                    style={{
                        backgroundColor: "yellow",
                        color: "black",
                    }}
                    className="mx-2 text-white bg-yellow-500"
                >
                    Release
                </LoadingButton>
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
