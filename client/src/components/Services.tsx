import React from "react";
import {
    services,
    // @ts-ignore
} from "eventData";
import StopIcon from "@mui/icons-material/Stop";
import PlayCircleFilledWhiteIcon from "@mui/icons-material/PlayCircleFilledWhite";
import { useSocket } from "../context/SocketContext";
import { LoadingButton } from "@mui/lab";

const Services = () => {
    const { sendService, scriptRunning } = useSocket();

    return (
        <div>
            <p className="my-5 text-xl font-bold">Services</p>
            <div>
                {services.map((service: any) => (
                    <div className="flex items-center p-2 mb-2 rounded-md">
                        <p className="text-lg font-bold">{service.name}</p>
                        <div className="flex gap-3 mx-5 my-3">
                            <LoadingButton
                                loadingPosition="start"
                                startIcon={<PlayCircleFilledWhiteIcon />}
                                variant="outlined"
                                loading={scriptRunning}
                                onClick={() => {
                                    sendService(service.socketName, "start");
                                }}
                            >
                                Start
                            </LoadingButton>
                            <LoadingButton
                                loadingPosition="start"
                                startIcon={<StopIcon />}
                                variant="outlined"
                                loading={scriptRunning}
                                onClick={() => {
                                    sendService(service.socketName, "stop");
                                }}
                            >
                                Stop
                            </LoadingButton>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default Services;
