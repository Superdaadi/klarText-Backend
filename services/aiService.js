import "dotenv/config";
import { GoogleGenAI } from "@google/genai";
import { GoogleGenerativeAI } from "@google/generative-ai";
import { exec } from "child_process";
import fs from "fs/promises";
import path from "path";



const ai = new GoogleGenAI({
  apiKey: process.env.GEMINI_API_KEY,
});
const genAI = new GoogleGenerativeAI(
  process.env.GEMINI_API_KEY
);




export async function generateAIResponseService(prompt) {
  const response = await ai.models.generateContent({
    model: "gemini-2.5-flash",
    contents: prompt,
  });

  return response.text;
}





export const generateSimplifyResponseService = async ({
  text,
  simplified = "leicht",
  keypoints = "true",
  language = "detect"
}) => {

  const languageInstruction =
    language === "detect"
      ? "Detect the language automatically and respond in that language."
      : `Respond ONLY in this language: ${language}.`;

  const simplifyLevelMap = {
    leicht: "Use very simple language, short sentences, easy words.",
    mittel: "Use simplified but still natural language.",
    stark: "Rewrite the text in very easy language for children or beginners."
  };

  const prompt = `
    You are a language simplification AI.

    TASK:
    - Split the input text into logical sentences.
    - Highlight difficult words in the original sentence using **bold markdown**.
    - Rewrite each sentence in simplified language.
    - Explain the highlighted words in simple terms.

    SIMPLIFICATION LEVEL:
    ${simplifyLevelMap[simplified]}

    WORD EXPLANATIONS:
    ${keypoints ? "Provide word explanations." : "Do NOT provide word explanations. Use empty arrays."}

    LANGUAGE:
    ${languageInstruction}

    OUTPUT FORMAT (JSON ONLY):
    Return ONLY valid JSON.
    Do NOT add explanations.
    Do NOT wrap in markdown.
    Do NOT add extra text.

    IMPORTANT:
    If you output anything other than valid JSON, the response is considered invalid.
    The first character of your response MUST be '[' and the last character MUST be ']'.

    JSON SCHEMA:
    [
      {
        "splittedSentence": "Original sentence with **bold** difficult words",
        "simplified": "Simplified version of the sentence",
        "wordExpl": [
          {
            "word": "word",
            "expl": "simple explanation"
          }
        ]
      }
    ]

    INPUT TEXT:
    """${text}"""
  `;

  //const geminiResponse = await callGemini(prompt);

  const geminiResponse = await generateAIResponseService(prompt);

  /**
   * Wichtig:
   * Gemini MUSS bereits reines JSON zurückgeben.
   * Kein Parsing erzwingen, einfach durchreichen.
   */
  return geminiResponse;
};



export const callGemini = async (prompt) => {
  const model = genAI.getGenerativeModel(
    { model: "gemini-1.5-pro" }
  );

  const result = await model.generateContent(prompt);
  const response = result.response.text();

  // Erwartet wird bereits pures JSON
  return JSON.parse(response);
};






















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


