import express from 'express';
import { generateAIResponseController } from '../controllers/simplifyController.js';

const router = express.Router();


router.post('/generateAIResponse', generateAIResponseController);


export default router;