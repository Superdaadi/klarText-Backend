
import { MongoClient } from "mongodb";


// ------------------------------
// MongoDB Setup
// ------------------------------
const client = new MongoClient("mongodb://localhost:27017");


export async function connectMongo() {
  await client.connect();
  const db = client.db("myDatabase");
  collection = db.collection("myCollection");
  console.log("MongoDB connected");
}




