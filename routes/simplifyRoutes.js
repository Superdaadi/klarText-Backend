import express from 'express';
import { generateAIResponse, generateSimplifyResponse } from '../controllers/simplifyController.js';

const router = express.Router();


router.post('/generateAIResponse', generateAIResponse);
router.post('/generateSimplifyResponse', generateSimplifyResponse);



export default router;