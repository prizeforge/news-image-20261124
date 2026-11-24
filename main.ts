#!/usr/bin/env node
// news-image-20261124: sum up 24 November 2026's world news in one image.
// The image (assets/entry.png, 1024x1024) is drawn at build time by
// scripts/render.py (Python + Pillow, flat editorial front page). This program
// copies it to /output/entry.png, so two runs write byte-identical output.
// Node 22, standard library only, no network.
import { copyFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const src = join(here, "assets", "entry.png");
const outDir = "/output";
const dst = join(outDir, "entry.png");

mkdirSync(outDir, { recursive: true });
copyFileSync(src, dst);
console.log("wrote", dst);
