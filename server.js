import express from "express";
import { generateAIResponse } from "./aiService.js";

const app = express();
app.use(express.json());

app.post("/api/ai", async (req, res) => {
  try {
    const { prompt } = req.body;
    const result = await generateAIResponse(prompt);
    res.json({ result });
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: "AI request failed" });
  }
});

app.listen(3000, () => {
  console.log("Server running on http://localhost:3000");
});
