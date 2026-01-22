import fs from "fs";
import path from "path";
import { MongoClient } from "mongodb";



const client = new MongoClient("mongodb://localhost:27017");
let collection = null;


export async function connectMongo() {
  await client.connect();
  const db = client.db("myDatabase");
  collection = db.collection("myCollection");
  console.log("MongoDB connected");
}




export async function uploadJson() {
  try {
    if (!collection) {
      throw new Error("Mongo connection not initialized. Call connectMongo() first.");
    }

    const jsonData = JSON.parse(fs.readFileSync("data.json", "utf8"));

    if (Array.isArray(jsonData)) {
      await collection.insertMany(jsonData);
    } else {
      await collection.insertOne(jsonData);
    }

    console.log("JSON stored successfully");
    return true;

  } catch (error) {
    console.error("JSON Upload Error:", error);
    return false;
  }
}


export async function readJson(filter = {}) {
  try {
    if (!collection) {
      throw new Error("Mongo connection not initialized. Call connectMongo() first.");
    }

    // filter = {} → alle Dokumente lesen
    const results = await collection.find(filter).toArray();
    console.log(`Found ${results.length} document(s)`);
    return results;

  } catch (error) {
    console.error("MongoDB Read Error:", error);
    return [];
  }
}


export async function readJsonPath(folderPath) {
    try {
        const files = fs.readdirSync(folderPath);   // Dateinamen
        const resolved = files.map(file =>
            path.join(folderPath, file)
        );

        console.log("Gefundene Dateien:", resolved);
        return resolved;

    } catch(error) {
        console.error("JSON Read Error:", error);
        return false;
    }
}


