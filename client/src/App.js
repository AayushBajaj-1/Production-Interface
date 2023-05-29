import { useState } from "react";
import { LoadingButton } from "@mui/lab";
import SendIcon from "@mui/icons-material/Send";
import ScriptBoard from "./ScriptBoard";

function App() {
    const [connected, setConnected] = useState(false);
    const [loading, setLoading] = useState(false);

    const startConnection = async () => {
        setLoading(true);
        try {
            const response = await fetch("http://localhost:3000/client/open", {
                method: "GET",
            });
            const data = await response.json();
            setConnected(true);
        } catch (error) {
            console.log(error);
            setConnected(false);
        }

        setLoading(false);
    };

    return (
        <>
            <nav className="px-5 flex items-center justify-between flex-wrap bg-primary h-[70px] text-white">
                <svg
                    viewBox="0 0 227 157"
                    fill="#fff"
                    version="1.1"
                    xmlns="http://www.w3.org/2000/svg"
                    className="w-[60px]"
                >
                    <title>Vention Production Interface</title>
                    <g
                        id="Page-1"
                        stroke="#fff"
                        strokewidth="1"
                        fillrule="evenodd"
                    >
                        <path
                            color="#fff"
                            d="M199.6512,38.0331 C193.3532,38.0331 188.2422,32.9221 188.2422,26.6211 C188.2422,20.3191 193.3532,15.2121 199.6512,15.2121 C205.9512,15.2121 211.0602,20.3191 211.0602,26.6211 C211.0602,32.9221 205.9512,38.0331 199.6512,38.0331 M112.9132,136.4061 C106.6122,136.4061 101.5032,131.2991 101.5032,124.9981 C101.5032,118.6971 106.6122,113.5891 112.9132,113.5891 C119.2132,113.5891 124.3212,118.6971 124.3212,124.9981 C124.3212,131.2991 119.2132,136.4061 112.9132,136.4061 M27.2312,38.0331 C20.9292,38.0331 15.8212,32.9221 15.8212,26.6211 C15.8212,20.3191 20.9292,15.2121 27.2312,15.2121 C33.5322,15.2121 38.6392,20.3191 38.6392,26.6211 C38.6392,32.9221 33.5322,38.0331 27.2312,38.0331 M217.2032,6.3451 L216.8302,6.0401 C212.1182,2.1451 206.1662,0.0021 200.0642,0.0021 C192.1812,0.0021 184.7842,3.4811 179.7632,9.5491 L113.3802,89.8241 L46.9912,9.5491 C41.9722,3.4791 34.5752,0.0001 26.6922,0.0001 C20.5902,0.0001 14.6372,2.1451 9.9312,6.0341 L9.5512,6.3481 C4.1322,10.8301 0.7832,17.1551 0.1202,24.1551 C-0.5438,31.1551 1.5592,37.9931 6.0422,43.4151 L91.9682,147.3161 C96.9842,153.3841 104.3842,156.8631 112.2672,156.8631 C112.6352,156.8631 113.0022,156.8301 113.3682,156.8141 C113.7422,156.8301 114.1152,156.8651 114.4932,156.8651 C122.3702,156.8651 129.7712,153.3841 134.7902,147.3161 L220.7132,43.4151 C229.9652,32.2291 228.3912,15.6021 217.2032,6.3451"
                        ></path>
                    </g>
                </svg>
                <h1>Vention Production Interface</h1>
            </nav>
            <main className="p-10">
                <section className="w-full flex justify-between">
                    <div>MachineMotion Connection</div>
                    <LoadingButton
                        loadingPosition="start"
                        loading={loading}
                        startIcon={<SendIcon />}
                        variant="outlined"
                        onClick={startConnection}
                        disabled={connected}
                        style={{
                            backgroundColor: connected ? "#4caf50" : "#f44336",
                            color: "#fff",
                            borderColor: connected ? "#4caf50" : "#f44336",
                        }}
                    >
                        Connect to MachineMotion
                    </LoadingButton>
                </section>
                {!!connected && <ScriptBoard />}
            </main>
        </>
    );
}

export default App;
