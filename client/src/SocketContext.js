// MyContext.js
import { createContext, useContext } from "react";

const MyContext = createContext();

export function SocketProvider({ children, value }) {
    return <MyContext.Provider value={value}>{children}</MyContext.Provider>;
}

export function useSocket() {
    const context = useContext(MyContext);
    return context;
}
