// MyContext.js
import React from "react";
import { createContext, useContext, useState, useEffect } from "react";
//@ts-ignore
import { eStopEvents } from "eventData";
import socketIOClient, { Socket } from "socket.io-client";
import { useToast } from "./SnackbarContext";

type ContextProps = {
    socket: Socket | undefined;
    connected: boolean;
    scriptOutput: string;
    setScriptOutput: React.Dispatch<React.SetStateAction<string>>;
    scriptRunning: boolean;
    setScriptRunning: React.Dispatch<React.SetStateAction<boolean>>;
    sendStart: () => void;
    testSend: () => void;
    triggerEStop: () => void;
    releaseEStop: () => void;
    sendInput: (input: string) => void;
};

const MyContext = createContext<ContextProps>({
    socket: undefined,
    connected: false,
    scriptOutput: "",
    setScriptOutput: () => {},
    scriptRunning: false,
    setScriptRunning: () => {},
    testSend: () => {},
    sendStart: () => {},
    triggerEStop: () => {},
    releaseEStop: () => {},
    sendInput: () => {},
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
    const { handleToastOpen } = useToast();

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

    const testSend = () => {
        socket?.emit("sendScriptToMM");
    };

    const sendInput = (input: string) => {
        socket?.emit("inputReceived", input);
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

        tempsocket.on("script:error", () => {
            console.log("Script error");
            handleToastOpen({
                message: "Script error",
                severity: "error",
            });
        });

        tempsocket.on("script:success", (data) => {
            console.log("Script success");
            handleToastOpen({
                message: "Script success",
                severity: "success",
            });
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
                testSend,
                triggerEStop,
                releaseEStop,
                sendInput,
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
