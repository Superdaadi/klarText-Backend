import express from 'express';
import { generateSimplifyResponse } from '../controllers/simplifyController.js';

const router = express.Router();


router.post('/generateSimplifyResponse', generateSimplifyResponse);



export default router;