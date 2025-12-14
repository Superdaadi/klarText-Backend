import "dotenv/config";
import { GoogleGenAI } from "@google/genai";
import { exec } from "child_process";
import fs from "fs/promises";
import path from "path";



const ai = new GoogleGenAI({
  apiKey: process.env.GEMINI_API_KEY,
});


export async function generateAIResponse(prompt) {
  const response = await ai.models.generateContent({
    model: "gemini-2.5-flash",
    contents: prompt,
  });

  return response.text;
}






export async function generateAITextFromAudio(pathToAudio) {
  return new Promise((resolve, reject) => {
    const whisperPath = "/home/david/.venv/bin/whisper";

    // --output_format txt erzeugt Text, wir fangen stdout ab
    const cmd = `${whisperPath} "${pathToAudio}" --model small --output_format txt`;

    exec(cmd, (error, stdout, stderr) => {
      if (error) {
        reject("Whisper failed: " + stderr);
        return;
      }

      try {
        
        // 1. Split the stdout into individual lines
        const lines = stdout.trim().split('\n');

        // 2. Get the last line, which contains the actual transcription and timestamp
        const lastLine = lines[lines.length - 1];

        // 3. Apply the regex to the single line to remove the timestamp
        const finalTranscribedText = lastLine.replace(/^.*\]\s*/, '').trim();


        if (!finalTranscribedText) reject("No transcribed text found in stdout.");
        else resolve(finalTranscribedText);

      } catch (err) {
        reject("Failed to parse Whisper stdout: " + err);
      }
    });
  });
}


