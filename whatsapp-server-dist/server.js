const express = require("express");
const cors = require("cors");
const qrcode = require("qrcode-terminal");
const { Client, LocalAuth, MessageMedia } = require("whatsapp-web.js");
const mime = require("mime-types");
const fs = require("fs");

const app = express();
const PORT = 3000;

app.use(cors());
app.use(express.json());

// ==========================
// Cliente de WhatsApp
// ==========================
const client = new Client({
    authStrategy: new LocalAuth({
        clientId: "jarvis"
    })
});

// ==========================
// Eventos
// ==========================
client.on("qr", (qr) => {

    console.clear();

    console.log("==================================");
    console.log(" ESCANEA ESTE QR CON WHATSAPP");
    console.log("==================================");

    qrcode.generate(qr, {
        small: true
    });

});

client.on("authenticated", () => {
    console.log("✅ WhatsApp autenticado.");
});

client.on("ready", () => {
    console.log("✅ WhatsApp conectado correctamente.");
});

client.on("auth_failure", (msg) => {
    console.log(msg);
});

client.on("disconnected", (reason) => {
    console.log(reason);
});

client.initialize();

// ==========================
// Estado
// ==========================
const VERSION_SERVIDOR = "1.1.0";

app.get("/status", (req, res) => {

    res.json({
        success: true,
        version: VERSION_SERVIDOR,
        message: "Servidor funcionando."
    });

});

// ==========================
// Enviar mensaje
// ==========================
app.post("/send-message", async (req, res) => {

    try {

        const { telefono, mensaje } = req.body;

        if (!telefono || !mensaje) {

            return res.status(400).json({
                success: false,
                message: "Datos incompletos."
            });

        }

        await client.sendMessage(
            `${telefono}@c.us`,
            mensaje
        );

        res.json({
            success: true
        });

    } catch (e) {

        console.log(e);

        res.status(500).json({
            success: false,
            error: e.message
        });

    }

});

// ==========================
// Enviar cualquier archivo
// ==========================
app.post("/send-file", async (req, res) => {

    try {

        console.log("========== NODE ==========");
        console.log(req.body);

        const {
            telefono,
            ruta,
            mensaje
        } = req.body;

        if (!telefono || !ruta) {

            return res.status(400).json({
                success: false,
                message: "Faltan datos."
            });

        }

        if (!fs.existsSync(ruta)) {

            return res.status(404).json({
                success: false,
                message: "El archivo no existe."
            });

        }

        console.log("Ruta:", ruta);
        console.log("Existe:", fs.existsSync(ruta));

        const media = MessageMedia.fromFilePath(ruta);

        await client.sendMessage(
            `${telefono}@c.us`,
            media,
            {
                caption: mensaje || ""
            }
        );

        res.json({
            success: true,
            message: "Archivo enviado correctamente."
        });

    } catch (e) {

        console.log(e);

        res.status(500).json({
            success: false,
            error: e.message
        });

    }

});

// ==========================

app.listen(PORT, () => {

    console.log(
        `🚀 Servidor iniciado en http://localhost:${PORT}`
    );

});