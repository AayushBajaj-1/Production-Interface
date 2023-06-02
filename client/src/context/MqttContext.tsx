// MyContext.js
import React from "react";
import { createContext, useContext, useState, useEffect } from "react";
//@ts-ignore
import { mqttTopics } from "eventData";
import { useSocket } from "./SocketContext";

export type NetworkProps = {
    dev: number;
    hw_version: string;
    id: string;
    ip: string;
    serial_no: string;
    sw_version: string;
};

type ContextProps = {
    estop: string | undefined;
    network: NetworkProps | undefined;
};

const MqttContext = createContext<ContextProps>({
    estop: undefined,
    network: undefined,
});

const ab2str = (arrayBuffer: ArrayBuffer) => {
    const decoder = new TextDecoder();
    const decodedString = decoder.decode(arrayBuffer);
    return decodedString;
};

export function MQTTProvider({ children }: { children: React.ReactNode }) {
    const { socket } = useSocket();
    const [estop, setEstop] = useState();
    const [network, setNetwork] = useState();

    useEffect(() => {
        // Loop over all the mqttTopics and subscribe to each one of them
        Object.keys(mqttTopics).forEach((key) => {
            socket?.on(key, (data: any) => {
                if (key === "estop") {
                    setEstop(data.message);
                } else if (key === "network") {
                    let temp = JSON.parse(data.message);
                    setNetwork(temp[0]);
                }
            });
        });

        // Cleanup for unmount
        return () => {
            Object.keys(mqttTopics).forEach((key) => {
                socket?.off(key);
            });
        };
    }, [socket, mqttTopics]);

    return (
        <MqttContext.Provider
            value={{
                estop: estop,
                network: network,
            }}
        >
            {children}
        </MqttContext.Provider>
    );
}

export function useMQTT() {
    const context = useContext(MqttContext);
    return context;
}
