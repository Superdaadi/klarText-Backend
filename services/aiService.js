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







  export async function simplifyText(text) {
    const sentences = splitIntoSentences(text);
    const results = [];

    for (const sentence of sentences) {
      const prompt = buildPrompt(sentence);
      const rawOutput = await queryLocalAI(prompt);

      const parsed = parseJSONOutput(rawOutput);

      // 🔹 Flach machen: parsed kann Array oder Objekt sein
      if (Array.isArray(parsed)) {
        parsed.forEach(item => {
          if (Array.isArray(item)) {
            results.push(...item); // verschachtelte Arrays auspacken
          } else {
            results.push(item);
          }
        });
      } else {
        results.push(parsed);
      }

      console.clear();
      console.log(JSON.stringify(results, null, 2));

      //console.log(results);
    }



    //const rawOutput = await queryLocalAI(prompt);

    //console.log(results);

    return results;
  }




  // 1: Sentence Splitter

  export function splitIntoSentences(text) {
    return text
      .replace(/\n+/g, " ")             // Zeilenumbrüche durch Leerzeichen
      .replace(/["'»«„“]/g, "")         // Anführungszeichen entfernen
      .match(/(?:\d+\.)|\d+(?:,\d+)?|[^.!?]+[.!?]+/g) // Zahlen und Sätze
      ?.map(s => s.trim()) || [];
  }









  export function parseJSONOutput(raw) {
    if (typeof raw !== "string") return raw;

    let clean = raw.trim()
      .replace(/^```(\w*)\s*/, "") // ```json oder ``` am Anfang
      .replace(/```$/, "")         // ``` am Ende
      .trim();

    // 1️⃣ Versuch direkt zu parsen
    try {
      return JSON.parse(clean);
    } catch {
      // 2️⃣ Falls nicht möglich, einzelne Objekte parsen
      const objects = [];
      const regex = /\{[\s\S]*?\}/g; // alle Objekte von { bis } inkl.
      let match;
      while ((match = regex.exec(clean)) !== null) {
        try {
          objects.push(JSON.parse(match[0]));
        } catch (err) {
          console.warn("Ein Objekt konnte nicht geparst werden:", err);
        }
      }

      // 3️⃣ Rückgabe konsistent
      if (objects.length === 1) return objects[0];
      return objects; // mehrere → Array
    }
  }








  export function buildPrompt(inputText) {
    return `
      Du bist ein Assistent für Sprachvereinfachung.

      AUFGABE:
        Verarbeite immer nur EINEN Satz auf einmal.

        Identifiziere schwierige Wörter.

        Schreibe den Satz in einfacher Sprache um.

        Erkläre die schwierigen Wörter kurz und knapp.

      AUSGABEFORMAT:

       JSON SCHEMA:

      [
        {
          "inputText": "Original sentence with **bold** difficult words",
          "simplified": "Simplified version of the sentence",
          "wordExpl": [
            {
              "word": "word",
              "expl": "simple explanation"
            },
            {
              "word": "word2",
              "expl": "simple explanation2"
            }
          ]
        }
      ]

      REGELN:
        Gib UNBEDINGT JSON aus.

        Füge KEINEN zusätzlichen Text oder Smalltalk hinzu.

        Nutze für die gesamte Ausgabe deutsch!

      TEXT: """${inputText}"""
    `;
  }



  // 2: AI-Service

  export async function queryLocalAI(prompt) {
    const response = await fetch("http://localhost:11434/api/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        model: "llama3.2:1b",
        prompt,
        stream: false,
        options: {
          temperature: 0.2,
          num_predict: 300
        }
      })
    });

    if (!response.ok) {
      throw new Error("AI request failed");
    }

    const data = await response.json();
    return data.response;
  }




  



  // 4: Parse LLM Output

  export function parseLLMOutput(raw) {
    console.log(raw);

    // Use optional chaining (?.[1]) and default to empty strings ("")
    const sentence = raw.match(/SENTENCE:\s*([\s\S]*?)\n\n/i)?.[1]?.trim() || "";
    const hardWordsLine = raw.match(/HARD WORDS:\s*(.*)/i)?.[1]?.trim() || "";
    const simplified = raw.match(/SIMPLIFIED:\s*([\s\S]*?)\n\n/i)?.[1]?.trim() || "";
    const explBlock = raw.match(/EXPLANATIONS:\s*([\s\S]*)/i)?.[1] || "";

    const hardWords = hardWordsLine
      ? hardWordsLine.split("|")
          .map(w => w.trim())
          .filter(w => w.length > 0 && !w.includes('*')) // Filter out empty strings and accidental markdown
      : [];

    let highlightedSentence = sentence || "";

    hardWords.forEach(word => {
      if (word && highlightedSentence) {
        // Escape special regex characters in the word to prevent crashes
        const escapedWord = word.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        
        // Use the escaped word in the Regex
        const regex = new RegExp(`\\b${escapedWord}\\b`, "gi");
        highlightedSentence = highlightedSentence.replace(regex, `**${word}**`);
      }
    });

    const wordExpl = [];
    if (explBlock) {
      explBlock.split("\n").forEach(line => {
        const parts = line.split("=");
        if (parts.length >= 2) {
          wordExpl.push({
            word: parts[0].trim(),
            expl: parts[1].trim()
          });
        }
      });
    }

    return {
      splittedSentence: highlightedSentence,
      simplified,
      wordExpl
    };
  }













































/*export const generateSimplifyResponseService = async ({
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


  console.log(prompt);


  const llama3Response = await queryLocalAI(prompt);




  //const geminiResponse = await generateAIResponseService(prompt);

  console.log(llama3Response)

  return llama3Response;
};



export const callGemini = async (prompt) => {
  const model = genAI.getGenerativeModel(
    { model: "gemini-1.5-pro" }
  );

  const result = await model.generateContent(prompt);
  const response = result.response.text();

  // Erwartet wird bereits pures JSON
  return JSON.parse(response);
};*/






















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


