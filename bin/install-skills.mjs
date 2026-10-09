#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import { fileURLToPath } from "node:url";

const packageRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const cursorRoot = path.join(os.homedir(), ".cursor");
const targetRoot = path.join(cursorRoot, "skills");
const hooksDest = path.join(cursorRoot, "hooks");
const hooksSrc = path.join(packageRoot, "hooks");
const hookFiles = ["pr-checks.md", "pr-checks.py"];

const skills = fs
  .readdirSync(packageRoot, { withFileTypes: true })
  .filter((e) => e.isDirectory() && e.name.startsWith("bmo-"))
  .map((e) => e.name)
  .filter((name) => fs.existsSync(path.join(packageRoot, name, "SKILL.md")))
  .sort();

if (skills.length === 0) {
  console.error(`No bmo-* skills found in ${packageRoot}`);
  console.error("The npm package may be missing skill folders. Try updating bmo-agent-skills.");
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

const skillHooksDir = path.join(targetRoot, "hooks");
fs.mkdirSync(skillHooksDir, { recursive: true });
fs.copyFileSync(path.join(hooksSrc, "pr-checks.md"), path.join(skillHooksDir, "pr-checks.md"));

console.log(`Installing PR-checks hook to ${hooksDest}`);
fs.mkdirSync(hooksDest, { recursive: true });
for (const name of hookFiles) {
  const dest = path.join(hooksDest, name);
  fs.copyFileSync(path.join(hooksSrc, name), dest);
  if (name.endsWith(".py")) {
    fs.chmodSync(dest, 0o755);
  }
  console.log(`  ✓ ${name}`);
}

installHookEntries(path.join(cursorRoot, "hooks.json"), path.join(hooksSrc, "hooks.json"));

console.log("Done.");

function installHookEntries(destPath, fragmentPath) {
  const fragment = JSON.parse(fs.readFileSync(fragmentPath, "utf8"));
  let current = { version: 1, hooks: {} };
  if (fs.existsSync(destPath)) {
    try {
      const parsed = JSON.parse(fs.readFileSync(destPath, "utf8"));
      if (parsed && typeof parsed === "object") {
        current = parsed;
      }
    } catch {
      console.error(`  ! left ${destPath} unchanged (invalid JSON)`);
      return;
    }
  }
  if (!current.hooks || typeof current.hooks !== "object") {
    current.hooks = {};
  }
  current.version = current.version ?? fragment.version ?? 1;

  for (const [event, entries] of Object.entries(fragment.hooks || {})) {
    const existing = Array.isArray(current.hooks[event]) ? current.hooks[event] : [];
    const kept = existing.filter((entry) => !isPrChecksEntry(entry));
    current.hooks[event] = [...kept, ...entries];
  }

  fs.writeFileSync(destPath, `${JSON.stringify(current, null, 2)}\n`);
  console.log(`  ✓ merged pr-checks into ${destPath}`);
}

function isPrChecksEntry(entry) {
  const command = entry && typeof entry.command === "string" ? entry.command : "";
  return command.includes("pr-checks.py");
}
