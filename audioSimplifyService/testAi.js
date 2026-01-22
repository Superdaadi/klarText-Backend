import { generateAIResponse, generateAITextFromAudio } from "./services/aiService.js";
import { connectMongo, uploadJson, readJson } from "./services/mongodb.js";

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


async function testUploadJson() {
  try {
    await connectMongo();  // <<< GANZ WICHTIG
    const result = await uploadJson();

    if (result) {
      console.log("success");
    } else {
      console.log("upload failed");
    }

  } catch (error) {
    console.error("Error uploading json:", error);
  }
}


async function testRead() {
  await connectMongo();

  const allDocs = await readJson();
  console.log("All documents:", allDocs);

  const filteredDocs = await readJson({ name: "David" });
  console.log("Filtered documents:", filteredDocs);
}

//testTextToText();

testTextFromAudio();

//testUploadJson();

//testRead();

