import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./global.css";
import "@fontsource/roboto/300.css";
import "@fontsource/roboto/400.css";
import "@fontsource/roboto/500.css";
import "@fontsource/roboto/700.css";
import { SocketProvider } from "./context/SocketContext";
import { MQTTProvider } from "./context/MqttContext";
import { SnackBarProvider } from "./context/SnackbarContext";
import { DialogProvider } from "./context/DialogContext";

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
    <React.StrictMode>
        <SnackBarProvider>
            <SocketProvider>
                <DialogProvider>
                    <MQTTProvider>
                        <App />
                    </MQTTProvider>
                </DialogProvider>
            </SocketProvider>
        </SnackBarProvider>
    </React.StrictMode>
);
