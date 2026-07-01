#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import { fileURLToPath } from "node:url";

const packageRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const targetRoot = path.join(os.homedir(), ".cursor", "skills");

const skills = fs
  .readdirSync(packageRoot, { withFileTypes: true })
  .filter((e) => e.isDirectory() && e.name.startsWith("bmo-"))
  .map((e) => e.name)
  .filter((name) => fs.existsSync(path.join(packageRoot, name, "SKILL.md")))
  .sort();

if (skills.length === 0) {
  console.error("No bmo-* skills found. Is the package installed correctly?");
  process.exit(1);
}

console.log(`Installing ${skills.length} skill(s) to ${targetRoot}`);

fs.mkdirSync(targetRoot, { recursive: true });

for (const name of skills) {
  fs.cpSync(path.join(packageRoot, name), path.join(targetRoot, name), {
    recursive: true,
    force: true,
  });
  console.log(`  ✓ ${name}`);
}

console.log("Done.");
