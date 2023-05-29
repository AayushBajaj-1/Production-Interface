import { Button } from "@mui/material";
import React, { useEffect, useState } from "react";
import socketIOClient from "socket.io-client";

const ab2str = (arrayBuffer) => {
    const decoder = new TextDecoder();
    const decodedString = decoder.decode(arrayBuffer);
    return decodedString;
};

const App = () => {
    const [scriptOutput, setScriptOutput] = useState("");
    const [isScriptComplete, setIsScriptComplete] = useState(false);
    const [errorMessage, setErrorMessage] = useState("");
    const [socket, setSocket] = useState(null);

    useEffect(() => {
        let tempsocket = socketIOClient("http://localhost:3000");

        tempsocket.on("output", (output) => {
            console.log(ab2str(output));
            setScriptOutput((prevOutput) => prevOutput + ab2str(output));
        });

        tempsocket.on("input", (output) => {
            console.log("Receiving input now");
            console.log(ab2str(output));
        });

        tempsocket.on("error", (error) => {
            setErrorMessage(error);
            socket.disconnect();
        });

        setSocket(tempsocket);

        return () => {
            tempsocket.disconnect();
        };
    }, []);

    return (
        <div>
            <h1>Script Output</h1>
            <pre>{scriptOutput}</pre>

            {isScriptComplete && <p>Script execution complete.</p>}
            {errorMessage && <p>Error: {errorMessage}</p>}
            <Button
                onClick={() => {
                    socket.emit("start");
                }}
                variant="contained"
            >
                Connect
            </Button>
            <Button
                onClick={() => {
                    socket.emit("runSetup");
                }}
                variant="contained"
            >
                Run Script
            </Button>
        </div>
    );
};

export default App;
