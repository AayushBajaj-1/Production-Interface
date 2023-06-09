import { createContext, useContext, useState, useEffect } from "react";
import * as React from "react";
import Button from "@mui/material/Button";
import TextField from "@mui/material/TextField";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogTitle from "@mui/material/DialogTitle";
import { useSocket } from "./SocketContext";

type ContextProps = {
    open: boolean;
    handleDialogOpen: (input: string) => void;
    handleDialogClose: () => void;
};

const ab2str = (arrayBuffer: ArrayBuffer) => {
    const decoder = new TextDecoder();
    const decodedString = decoder.decode(arrayBuffer);
    return decodedString;
};

const DialogContext = createContext<ContextProps>({
    open: false,
    handleDialogOpen: () => {},
    handleDialogClose: () => {},
});

export function DialogProvider({ children }: { children: React.ReactNode }) {
    const [open, setOpen] = useState(false);
    const [input, setInput] = useState("");
    const [message, setMessage] = useState("");
    const { sendInput, socket } = useSocket();

    const handleDialogOpen = (message: string) => {
        setOpen(true);
        setMessage(message as any);
    };

    const handleDialogClose = () => {
        sendInput("");
        setOpen(false);
        setInput("");
    };

    const handleSend = () => {
        console.log("Sending input: ", input);
        sendInput(input);
        setOpen(false);
        setInput("");
    };

    useEffect(() => {
        socket?.on("input", (output) => {
            handleDialogOpen(ab2str(output));
        });

        return () => {
            socket?.off("input");
        };
    }, [socket]);

    return (
        <DialogContext.Provider
            value={{
                handleDialogOpen,
                handleDialogClose,
                open,
            }}
        >
            {children}
            <Dialog open={open} onClose={handleDialogClose}>
                <DialogTitle>Input Requested</DialogTitle>
                <DialogContent>
                    <DialogContentText>{message}</DialogContentText>
                    <TextField
                        autoFocus
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        margin="dense"
                        id="name"
                        label="Input"
                        type="email"
                        fullWidth
                        variant="standard"
                    />
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleDialogClose}>Cancel</Button>
                    <Button onClick={handleSend}>Send</Button>
                </DialogActions>
            </Dialog>
        </DialogContext.Provider>
    );
}

export function useDialog() {
    const context = useContext(DialogContext);
    return context;
}
