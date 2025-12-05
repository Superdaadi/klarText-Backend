import { generateAIResponse, generateAITextFromAudio } from "./aiService.js";

async function testTextToText() {
  try {
    const input = "Warum ist Jugend-forscht so toll?"
    const result = await generateAIResponse(input);
    console.log(input)
    console.log("AI says:", result);
  } catch (error) {
    console.error("Error calling AI:", error);
  }
}


async function testTextFromAudio() {
  try {
    const pathToAudio = "/home/david/Dokumente/JUFO2026/klarText-Backend/audioFiles/Test1.mp3";
    const result = await generateAITextFromAudio(pathToAudio);
    console.log("Transcribed text:", result);
  } catch (error) {
    console.error("Error transcribing audio:", error);
  }
}

//testTextToText();
testTextFromAudio();
