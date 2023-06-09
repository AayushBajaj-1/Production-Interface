import { createContext, useContext, useState, useEffect } from "react";
import * as React from "react";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogTitle from "@mui/material/DialogTitle";
import { useSocket } from "./SocketContext";
import Convert from "ansi-to-html";
import { LoadingButton } from "@mui/lab";
import CancelIcon from "@mui/icons-material/Cancel";

const convert = new Convert();

type ContextProps = {
    open: boolean;
    handleDialogOpen: () => void;
    handleDialogClose: () => void;
};

const ab2str = (arrayBuffer: ArrayBuffer) => {
    const decoder = new TextDecoder();
    const decodedString = decoder.decode(arrayBuffer);
    return decodedString;
};

const ConsoleDialogContext = createContext<ContextProps>({
    open: false,
    handleDialogOpen: () => {},
    handleDialogClose: () => {},
});

export function ConsoleDialogProvider({
    children,
}: {
    children: React.ReactNode;
}) {
    const [open, setOpen] = React.useState(false);
    const { scriptOutput, socket, setScriptRunning } = useSocket();

    const handleDialogClose = () => {
        setOpen(false);
    };

    const handleDialogOpen = () => {
        setOpen(true);
        getOutput();
    };

    const stopScript = async () => {
        socket?.emit("stopScript");
        setScriptRunning(false);
    };

    const getOutput = () => {
        let text = convert.toHtml(scriptOutput);
        // Remove the ?2004h and ?2004l from the output, cleanup for the data
        text = text.replace(/\?2004h/g, "");
        text = text.replace(/\?2004l/g, "");
        let preElement = document.getElementById("test");
        if (preElement) {
            preElement.innerHTML = text;
            preElement.parentElement?.parentElement?.scrollTo({
                top: preElement.parentElement?.parentElement?.scrollHeight,
                behavior: "smooth",
            });
        }
    };

    React.useEffect(() => {
        getOutput();
    }, [scriptOutput]);

    return (
        <ConsoleDialogContext.Provider
            value={{
                handleDialogOpen,
                handleDialogClose,
                open,
            }}
        >
            {children}
            <Dialog
                keepMounted
                open={open}
                onClose={handleDialogClose}
                PaperProps={{
                    style: {
                        minWidth: "70vw",
                    },
                }}
            >
                <DialogTitle>Console Output</DialogTitle>
                <DialogContent>
                    <DialogContentText></DialogContentText>
                    <pre
                        id="test"
                        className="p-3 my-5 text-white bg-[#3e3e42] rounded-xl whitespace-pre-wrap"
                    ></pre>
                </DialogContent>
                <DialogActions>
                    <LoadingButton
                        loadingPosition="start"
                        startIcon={<CancelIcon />}
                        variant="outlined"
                        onClick={stopScript}
                    >
                        Stop Script
                    </LoadingButton>
                </DialogActions>
            </Dialog>
        </ConsoleDialogContext.Provider>
    );
}

export function useConsole() {
    const context = useContext(ConsoleDialogContext);
    return context;
}
