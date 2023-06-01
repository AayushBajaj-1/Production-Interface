const mqtt = require("mqtt");
const { mqttTopics } = require("../eventData");

const configureMQTTHandlers = (socket) => {
    const brokerUrl = "tcp://192.168.192.51:1883"; // Replace with your MQTT broker's TCP URL
    const client = mqtt.connect(brokerUrl);

    client.on("connect", () => {
        console.log("Connected to MQTT broker");

        // Subscribe to all the topics in the mqttTopics object
        Object.keys(mqttTopics).forEach((key) => {
            // Subscribe to all the topics
            client.subscribe(mqttTopics[key]);
        });
    });

    // Send all the messages to the client
    client.on("message", (topic, message) => {
        // Find the topic name from the topic
        const topicName = Object.keys(mqttTopics).find(
            (key) => mqttTopics[key] === topic
        );
        socket.emit(topicName, {
            message: message.toString(),
        });
    });

    client.on("error", (error) => {
        console.error("Error in the MQTT broker:", error);
    });

    client.on("close", () => {
        console.log("Disconnected from MQTT broker");
    });
};

module.exports = { configureMQTTHandlers };
