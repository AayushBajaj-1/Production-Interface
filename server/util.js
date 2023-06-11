const fs = require("fs");
const SftpClient = require("ssh2-sftp-client");
require("dotenv").config();

const sendFolderViaSFTP = async (localFolderPath, remoteFolderPath) => {
    try {
        const sftp = new SftpClient();
        await sftp.connect({
            host: process.env.IP,
            username: process.env.HOSTNAME,
            password: process.env.PASSWORD,
        });

        await sftp.uploadDir(localFolderPath, remoteFolderPath, {
            sftp,
        });

        sftp.end();
        console.log("SFTP session closed.");
    } catch (err) {
        console.error("Error:", err);
    }
};

module.exports = { sendFolderViaSFTP };
