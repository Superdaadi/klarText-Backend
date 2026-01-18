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


//connectMongo();


// ------------------------------
// Server starten
// ------------------------------
app.listen(3000, () => {
  console.log("Server running on http://localhost:3000");
});
