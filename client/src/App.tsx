import React from "react";
import ScriptBoard from "./ScriptBoard";
import Topbar from "./Topbar";
import Navbar from "./Navbar";
import { useSocket } from "./SocketContext";

const App = () => {
    const { connected } = useSocket();

    return (
        <>
            <head>
                <title>Production Interface</title>
            </head>
            <Navbar />
            <main className="p-10">
                <Topbar />
                {!!connected && <ScriptBoard />}
            </main>
        </>
    );
};

export default App;
