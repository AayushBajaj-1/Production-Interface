// MyContext.js
import React from "react";
import { createContext, useContext, useState, useEffect } from "react";
//@ts-ignore
import { eStopEvents } from "eventData";
import socketIOClient, { Socket } from "socket.io-client";

type ContextProps = {
    socket: Socket | undefined;
    connected: boolean;
    scriptOutput: string;
    setScriptOutput: React.Dispatch<React.SetStateAction<string>>;
    scriptRunning: boolean;
    setScriptRunning: React.Dispatch<React.SetStateAction<boolean>>;
    sendStart: () => void;
    triggerEStop: () => void;
    releaseEStop: () => void;
};

const MyContext = createContext<ContextProps>({
    socket: undefined,
    connected: false,
    scriptOutput: "",
    setScriptOutput: () => {},
    scriptRunning: false,
    setScriptRunning: () => {},
    sendStart: () => {},
    triggerEStop: () => {},
    releaseEStop: () => {},
});

const ab2str = (arrayBuffer: ArrayBuffer) => {
    const decoder = new TextDecoder();
    const decodedString = decoder.decode(arrayBuffer);
    return decodedString;
};

export function SocketProvider({ children }: { children: React.ReactNode }) {
    const [socket, setSocket] = useState<Socket>();
    const [connected, setConnected] = useState(false);
    const [scriptOutput, setScriptOutput] = useState("");
    const [scriptRunning, setScriptRunning] = useState(false);

    const sendStart = () => {
        socket?.emit("start");
    };

    const triggerEStop = () => {
        setScriptRunning(true);
        socket?.emit(eStopEvents[0].socketName);
    };

    const releaseEStop = () => {
        setScriptRunning(true);
        socket?.emit(eStopEvents[1].socketName);
    };

    useEffect(() => {
        let tempsocket = socketIOClient("http://localhost:3000");

        tempsocket.on("output", (output) => {
            console.log(ab2str(output));
            setScriptOutput((prevOutput) => prevOutput + ab2str(output));
        });

        tempsocket.on("connected", (output) => {
            setConnected(true);
        });

        tempsocket.on("disconnect", (output) => {
            setConnected(false);
        });

        tempsocket.on("input", (output) => {
            console.log("Received a input now");
            console.log(ab2str(output));

            let input = prompt(ab2str(output));
            tempsocket.emit("inputReceived", input);
        });

        tempsocket.on("error", (error) => {
            console.log(error);
        });

        tempsocket.on("completion", () => {
            setScriptRunning(false);
        });

        setSocket(tempsocket);

        return () => {
            tempsocket.disconnect();
        };
    }, []);

    return (
        <MyContext.Provider
            value={{
                socket,
                connected,
                scriptOutput,
                setScriptOutput,
                scriptRunning,
                setScriptRunning,
                sendStart,
                triggerEStop,
                releaseEStop,
            }}
        >
            {children}
        </MyContext.Provider>
    );
}

export function useSocket() {
    const context = useContext(MyContext);
    return context;
}
