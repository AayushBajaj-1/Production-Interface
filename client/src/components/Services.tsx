import React from "react";
import {
    services,
    // @ts-ignore
} from "eventData";
import { Button } from "@mui/material";
import { useSocket } from "../context/SocketContext";

const Services = () => {
    const { sendService } = useSocket();

    return (
        <div>
            <p className="my-5 text-xl font-bold">Services</p>
            <div>
                {services.map((service: any) => (
                    <div className="flex items-center justify-between p-2 mb-2 bg-gray-100 rounded-md">
                        <p className="text-lg font-bold">{service.name}</p>
                        <Button
                            onClick={() => {
                                sendService(service.socketName, "start");
                            }}
                        >
                            Start
                        </Button>
                        <Button
                            onClick={() => {
                                sendService(service.socketName, "stop");
                            }}
                        >
                            Stop
                        </Button>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default Services;
