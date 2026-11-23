// Entry point for the make.fun grader.
//
// The judged image is entry.png, which sits in this repository next to
// this file. The grader runs this program offline with no arguments;
// all it has to do is place a copy of that image at
// $MAKEFUN_OUTPUT_DIR/entry.png (falling back to /output when the
// variable is not set). Only the Node standard library is used.
import { copyFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const repoDir = dirname(fileURLToPath(import.meta.url));
const outputDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";

mkdirSync(outputDir, { recursive: true });
const target = join(outputDir, "entry.png");
copyFileSync(join(repoDir, "entry.png"), target);
console.log(`wrote ${target}`);
