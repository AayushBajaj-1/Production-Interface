import React, { useEffect, useState } from "react";
import socketIOClient from "socket.io-client";
import ScriptBoard from "./ScriptBoard";
import Navbar from "./Navbar";
import Topbar from "./Topbar";
import { SocketProvider } from "./SocketContext";

const ab2str = (arrayBuffer) => {
    const decoder = new TextDecoder();
    const decodedString = decoder.decode(arrayBuffer);
    return decodedString;
};

const App = () => {
    const [scriptOutput, setScriptOutput] = useState("");
    const [connected, setConnected] = useState(false);
    const [loading, setLoading] = useState(false);
    const [socket, setSocket] = useState(null);

    const sendStart = () => {
        socket.emit("start");
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

        tempsocket.on("disconnected", (output) => {
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
            setLoading(false);
        });

        setSocket(tempsocket);

        return () => {
            tempsocket.disconnect();
        };
    }, []);

    return (
        <SocketProvider
            value={{
                socket: socket,
                connected: connected,
            }}
        >
            <Navbar />
            <main className="p-10">
                <Topbar sendStart={sendStart} connected={connected} />
                {!!connected && (
                    <ScriptBoard
                        socket={socket}
                        scriptOutput={scriptOutput}
                        loading={loading}
                        setLoading={setLoading}
                        setScriptOutput={setScriptOutput}
                    />
                )}
            </main>
        </SocketProvider>
    );
};

export default App;
