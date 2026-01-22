import express from "express";
import cors from 'cors';
import fs from "fs";

import { connectMongo } from "./middleware/db.js";

import simplifyRouter from './routes/simplifyRoutes.js';



const app = express();


app.use(cors({
  origin: 'http://localhost:4200', // Allow only your frontend
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));
app.use(express.json());


app.use('/simplify', simplifyRouter);




async function preloadModel() {
    console.log("🚀 Lade KI-Modell in den RAM...");
    try {
        const response = await fetch("http://localhost:11434/api/generate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                model: "qwen2.5:7b",
                keep_alive: -1 // -1 sorgt dafür, dass das Modell unendlich lange im RAM bleibt
            })
        });

        if (response.ok) {
            console.log("✅ Modell erfolgreich geladen.");
        } else {
            console.warn("⚠️ Modell-Preload fehlgeschlagen:", response.statusText);
        }
    } catch (error) {
        console.error("❌ Fehler beim Verbindungsaufbau zu Ollama:", error.message);
    }
}







// ------------------------------
// Server starten
// ------------------------------
app.listen(3000, async () => {
  console.log("Server running on http://localhost:3000");
  
  await preloadModel(); 
});






