const fs = require("fs");

function transferFile(client, localFilePath, remoteFilePath) {
    return new Promise((resolve, reject) => {
        client.sftp((err, sftp) => {
            if (err) {
                console.error(
                    "Error occurred while creating SFTP session:",
                    err
                );
                reject(err);
                return;
            }

            const readStream = fs.createReadStream(localFilePath);
            const writeStream = sftp.createWriteStream(remoteFilePath);

            writeStream.on("close", () => {
                console.log("File transferred successfully");
                resolve();
            });

            writeStream.on("end", () => {
                console.log("SFTP connection closed");
                resolve();
            });

            readStream.pipe(writeStream);
        });
    });
}

module.exports = { transferFile };
