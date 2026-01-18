

import { simplifyText } from '../services/simplifyAiService.js';








export const generateSimplifyResponse = async (req, res) => {
  try {
    const { text, lang } = req.body;

    if (!text) {
      return res.status(400).json({ error: "Text is required" });
    }

    const result = await simplifyText(text, lang);

    res.json(result);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "AI generation failed" });
  }
};

