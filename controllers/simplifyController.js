

import { generateAIResponseService, generateSimplifyResponseService } from '../services/aiService.js';


export const generateAIResponse = async (req, res) => {
  try {
    const { prompt } = req.body;

    if (!prompt) {
      return res.status(400).json({ error: 'Prompt is required' });
    }

    const result = await generateAIResponseService(prompt);

    res.json({ result });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'AI generation failed' });
  }
};






export const generateSimplifyResponse = async (req, res) => {
  try {
    const { text, simplified, keypoints, language } = req.body;

    if (!text) {
      return res.status(400).json({ error: "Text is required" });
    }

    const result = await generateSimplifyResponseService({
      text,
      simplified,
      keypoints,
      language
    });

    // Ergebnis 1:1 weiterreichen
    res.json(result);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "AI generation failed" });
  }
};



