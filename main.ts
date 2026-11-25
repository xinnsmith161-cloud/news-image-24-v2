// Deliver entry.png to the output directory.
//
// The judged artefact is the front page image produced by generate.py.
// This module only places a verified copy of that image where the
// grader looks for it: the directory named by MAKEFUN_OUTPUT_DIR when
// it is set, otherwise /output. The target directory is created on
// demand, and the copy is measured afterwards so a truncated or empty
// write fails loudly instead of passing silently.

import { copyFileSync, existsSync, mkdirSync, statSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const FALLBACK_DIR = "/output";

function outputDirectory(): string {
  return process.env.MAKEFUN_OUTPUT_DIR ?? FALLBACK_DIR;
}

function placeEntryImage(): void {
  const scriptDir = dirname(fileURLToPath(import.meta.url));
  const origin = resolve(scriptDir, "entry.png");
  if (!existsSync(origin)) {
    const missing = `entry.png is missing next to main.ts: ${origin}`;
    throw new Error(missing);
  }
  const dir = outputDirectory();
  const goal = resolve(dir, "entry.png");
  mkdirSync(dir, { recursive: true });
  copyFileSync(origin, goal);
  const expected = statSync(origin).size;
  const actual = statSync(goal).size;
  if (actual !== expected || actual === 0) {
    const short = `entry.png did not land intact: ${actual} of ${expected} bytes at ${goal}`;
    throw new Error(short);
  }
  console.log(`entry.png placed at ${goal} (${actual} bytes)`);
}

placeEntryImage();
