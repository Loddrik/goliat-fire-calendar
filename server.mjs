import express from "express";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.dirname(fileURLToPath(import.meta.url));
const app = express();
const port = process.env.PORT || 3000;

app.get("/health", (_req, res) => res.json({ ok: true, version: process.env.RAILWAY_GIT_COMMIT_SHA ?? "local" }));
// datos pre-agregados por el pipeline (JSON/CSV), con caché larga
app.use("/data", express.static(path.join(root, "web/public/data"), { maxAge: "1h" }));
app.use("/data/detections", express.static(path.join(root, "data/processed/detections_csv"), { maxAge: "1h" }));
app.use(express.static(path.join(root, "web/dist")));
app.get("*", (_req, res) => res.sendFile(path.join(root, "web/dist/index.html")));

app.listen(port, () => console.log(`GOLIAT en :${port}`));
