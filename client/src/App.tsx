import React, { useEffect, useState } from "react";
import ScriptBoard from "./components/ScriptBoard";
import Topbar from "./components/Topbar";
import Navbar from "./layout/Navbar";
import { useSocket } from "./context/SocketContext";
import Services from "./components/Services";

const App = () => {
    const [showServices, setShowServices] = useState(false);
    const { connected } = useSocket();

    const handleShowServices = () => {
        setShowServices(!showServices);
    };

    useEffect(() => {
        document.title = "Vention Production Interface";
    }, []);

    return (
        <>
            <Navbar />
            <main className="p-10">
                <Topbar toggleServices={handleShowServices} />
                {!!connected && !showServices && <ScriptBoard />}
                {!!connected && !!showServices && <Services />}
            </main>
        </>
    );
};

export default App;
