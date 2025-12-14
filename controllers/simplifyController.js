

import { generateAIResponse } from '../services/aiService.js';


export const generateAIResponseController = async (req, res) => {
  try {
    const { prompt } = req.body;

    if (!prompt) {
      return res.status(400).json({ error: 'Prompt is required' });
    }

    const result = await generateAIResponse(prompt);

    res.json({ result });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'AI generation failed' });
  }
};



