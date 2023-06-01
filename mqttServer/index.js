const mqtt = require("mqtt");
const socketIOClient = require("socket.io-client");

const brokerUrl = "tcp://192.168.192.51:1883"; // Replace with your MQTT broker's TCP URL

const client = mqtt.connect(brokerUrl);

const socketUrl = "http://localhost:3000"; // Replace with the URL of your Socket.IO server
const socket = socketIOClient(socketUrl);

socket.on("connect", () => {
    client.on("connect", () => {
        console.log("Connected to MQTT broker");

        // Subscribe to a topic after connecting
        client.subscribe("estop/status");
    });

    client.on("message", (topic, message) => {
        console.log(
            `Received message on topic '${topic}': ${message.toString()}`
        );

        console.log("Sending message to Socket.IO server");
        console.log(socket);
        socket.emit("test", message.toString());
        console.log("Sent message to Socket.IO server");
    });

    client.on("error", (error) => {
        console.error("Error:", error);
    });

    client.on("close", () => {
        console.log("Disconnected from MQTT broker");
    });
});

socket.on("completion", () => {
    console.log("Disconnected from Socket.IO server");
});
