import "dotenv/config";
import { GoogleGenAI } from "@google/genai";
import { GoogleGenerativeAI } from "@google/generative-ai";
import { exec } from "child_process";
import fs from "fs/promises";
import path from "path";


/*console.log("Starting...")
const test = await simplifyText(
    `
        Düsseldorf. Der US-Elektroautobauer Tesla hat die Batterieproduktion in seiner Gigafabrik in Grünheide wieder aufgenommen. 
        Tesla hatte in Grünheide bereits zuvor Batterien gefertigt. Nach Angaben von Werksleiter Thierig produzierten die Mitarbeiter rund 100.000 Einheiten eines älteren Batterietyps. 
        Anschließend baute der Konzern die Fertigung um und schuf so die Voraussetzungen für einen neuen Batterietyp. Intern firmiert das Vorhaben unter dem Codenamen „Projekt Coyote“.
    `
)
console.log(test)*/



export async function simplifyText(inputText, lang) {
    console.log(inputText);


    // 1: Generate simplified Text
    const simplifiedContext = await justSimplify(inputText, "deutsch");

    console.log(simplifiedContext);

    // 2. Wörter extrahieren
    const rawCsv = await extractWords(inputText, "Deutsch");
    const wordsParsed = parseWordsToArray(rawCsv);

    // 3. Alle Erklärungen in EINEM Request holen
    const explanationsMap = await getBatchWordExpl(wordsParsed, "Deutsch");

    // 4. In finales Array-Format umwandeln
    const wordExpl = wordsParsed.map(word => ({
        word: word,
        explanation: explanationsMap[word] || "Keine Erklärung gefunden."
    }));

    console.log(wordExpl);

    // 5. Finales Objekt gemäß Interface "Text" zurückgeben
    return {
        inputText: inputText,
        simplified: simplifiedContext,
        wordExpl: wordExpl
    };
}





export async function justSimplify(inputText, lang) {
    try {
        const response = await fetch("http://localhost:11434/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                model: "qwen2.5:7b",
                messages: [
                    {
                        role: "system",
                        content: `Du bist ein Experte für Leichte Sprache. 
                        Regeln: 
                        - Max. 15 Wörter pro Satz.
                        - Aktiv statt Passiv.
                        - Keine Fachwörter.
                        - Antworte NUR mit dem Ergebnis-Text, kein Smalltalk.
                        - Sprache: ${lang}`
                    },
                    {
                        role: "user",
                        content: `Vereinfache diesen Text: """${inputText}"""`
                    }
                ],
                stream: false,
                options: {
                    temperature: 0.1,
                    num_predict: 300
                }
            })
        });

        if (!response.ok) {
            throw new Error(`Ollama Error: ${response.statusText}`);
        }

        const data = await response.json();
        
        return data.message.content.trim(); 

    } catch (error) {
        console.error("Fehler beim KI-Aufruf:", error);
        return "Fehler bei der Textverarbeitung.";
    }
}








export async function extractWords(inputText, lang) {
    try {
        const response = await fetch("http://localhost:11434/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                model: "qwen2.5:7b",
                messages: [
                    {
                        role: "system",
                        content: `
                            Du bist ein Extraktions-Algorithmus für linguistische Komplexität.
                            AUFGABE:
                            - Extrahiere Wörter, die schwer verständlich sind:
                                1. Lange zusammengesetzte Wörter (Komposita).
                                2. Fachbegriffe (Terminologie).
                                3. Seltene oder veraltete Ausdrücke.
                            - Extrahiere die Wörter EXAKT in der Form (Kasus/Numerus), wie sie im Text stehen.
                            - Ignoriere Eigennamen von Personen, Firmen oder Orten.

                            FORMAT-REGELN:
                            - Ausgabe NUR als CSV-Liste, getrennt durch Kommata (z.B. Wort1, Wort2, Wort3).
                            - KEINE Einleitung, KEINE Nummerierung, KEIN "Hier sind die Wörter".
                            - KEINE Header-Zeile.
                            - Wenn keine komplexen Wörter gefunden werden, antworte mit einem leeren String.

                            SPRACHE: ${lang}
                        `
                    },
                    {
                        role: "user",
                        content: `Extrahiere die Wörter aus folgendem Text: """${inputText}"""`
                    }
                ],
                stream: false,
                options: {
                    temperature: 0.1,
                    num_predict: 300
                }
            })
        });

        if (!response.ok) {
            throw new Error(`Ollama Error: ${response.statusText}`);
        }

        const data = await response.json();
        
        return data.message.content.trim(); 

    } catch (error) {
        console.error("Fehler beim KI-Aufruf:", error);
        return "Fehler bei der Textverarbeitung.";
    }
}




export function parseWordsToArray(csvString) {
    if (!csvString || typeof csvString !== 'string') return [];

    return csvString
        .split(',')                   // Bei Komma trennen
        .map(word => word.trim())      // Leerzeichen an den Enden entfernen
        .map(word => word.replace(/^["'„“]|["'„“]$/g, '')) // Anführungszeichen (auch deutsche) entfernen
        .filter(word => word.length > 0) // Leere Einträge entfernen
        .filter((word, index, self) => self.indexOf(word) === index); // Duplikate entfernen
}




export async function getBatchWordExpl(wordsArray, lang) {
    if (!wordsArray || wordsArray.length === 0) return [];

    try {
        const response = await fetch("http://localhost:11434/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                model: "qwen2.5:7b",
                format: "json",
                messages: [
                    {
                        role: "system",
                        content: `
                            Du bist ein Wörterbuch für einfache Sprache.
                            AUFGABE: Erkläre jedes Wort in der Liste kurz und simpel (max. 10 Wörter pro Erklärung).
                            FORMAT: Gib ein JSON-Objekt zurück, wobei die Keys die Wörter sind und die Values die Erklärungen.
                            Beispiel: {"Wort1": "Erklärung 1", "Wort2": "Erklärung 2"}
                            SPRACHE: ${lang}
                        `
                    },
                    {
                        role: "user",
                        content: `Erkläre diese Wörter: ${wordsArray.join(", ")}`
                    }
                ],
                stream: false,
                options: { 
                    temperature: 0.4
                }
            })
        });

        const data = await response.json();

        return JSON.parse(data.message.content); 

    } catch (error) {
        console.error("Fehler bei Batch-Erklärung:", error);
        return {};
    }
}





























export async function queryLocalAI(prompt) {
    const response = await fetch("http://localhost:11434/api/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        model: "deepseek-r1:7b",
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


