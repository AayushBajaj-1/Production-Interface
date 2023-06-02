import React, { useEffect } from "react";
import ScriptBoard from "./components/ScriptBoard";
import Topbar from "./components/Topbar";
import Navbar from "./layout/Navbar";
import { useSocket } from "./context/SocketContext";

const App = () => {
    const { connected } = useSocket();

    useEffect(() => {
        document.title = "Vention Production Interface";
    }, []);

    return (
        <>
            <Navbar />
            <main className="p-10">
                <Topbar />
                {!!connected && <ScriptBoard />}
            </main>
        </>
    );
};

export default App;
