const { createServer } = require("http");
const { Server } = require("socket.io");
const express = require("express");
const { configureIOEventHandlers } = require("./ioHandlers");

const app = express();
const server = createServer(app);
const io = new Server(server, {
    cors: {
        origin: "http://localhost:3001", // Replace with the URL of your React app
        methods: ["GET", "POST"],
    },
});

// All the socket io event handlers
configureIOEventHandlers(io);

// Start the HTTP server
const port = 3000;
server.listen(port, () => {
    console.log(`Server is running on port ${port}`);
});
