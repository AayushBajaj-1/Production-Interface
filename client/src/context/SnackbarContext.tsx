// MyContext.js
import Snackbar from "@mui/material/Snackbar";
import Slide, { SlideProps } from "@mui/material/Slide";
import React from "react";
import { createContext, useContext, useState, useEffect } from "react";
import Alert, { AlertColor } from "@mui/material/Alert";

function SlideTransition(props: SlideProps) {
    return <Slide {...props} direction="down" />;
}

type MessageProps = {
    severity: AlertColor | undefined;
    message: string;
};

type ContextProps = {
    open: boolean;
    handleToastOpen: (input: MessageProps) => void;
    handleToastClose: () => void;
};

const SnackBarContext = createContext<ContextProps>({
    open: false,
    handleToastOpen: () => {},
    handleToastClose: () => {},
});

export function SnackBarProvider({ children }: { children: React.ReactNode }) {
    const [open, setOpen] = useState(false);
    const [message, setMessage] = useState<MessageProps>({
        severity: "success",
        message: "",
    });

    const handleToastOpen = (message: MessageProps) => {
        setOpen(true);
        setMessage(message as any);
    };

    const handleToastClose = () => {
        setOpen(false);
    };

    return (
        <SnackBarContext.Provider
            value={{
                handleToastClose,
                handleToastOpen,
                open,
            }}
        >
            {children}
            <Snackbar
                anchorOrigin={{ vertical: "top", horizontal: "center" }}
                open={open}
                onClose={handleToastClose}
                autoHideDuration={6000}
                TransitionComponent={SlideTransition}
            >
                <Alert
                    onClose={handleToastClose}
                    severity={message.severity}
                    sx={{ width: "100%" }}
                >
                    {message.message}
                </Alert>
            </Snackbar>
        </SnackBarContext.Provider>
    );
}

export function useToast() {
    const context = useContext(SnackBarContext);
    return context;
}
