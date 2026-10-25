import { Router, type IRouter } from "express";
import healthRouter from "./health";
import partnerAgentRouter from "./partner-agent";

const router: IRouter = Router();

router.use(healthRouter);
router.use(partnerAgentRouter);

export default router;
