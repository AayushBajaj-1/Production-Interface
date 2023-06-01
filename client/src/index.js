import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./global.css";
import "@fontsource/roboto/300.css";
import "@fontsource/roboto/400.css";
import "@fontsource/roboto/500.css";
import "@fontsource/roboto/700.css";
import { SocketProvider } from "./SocketContext";

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
    <React.StrictMode>
        <SocketProvider>
            <App />
        </SocketProvider>
    </React.StrictMode>
);
