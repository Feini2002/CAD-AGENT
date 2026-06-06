#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const scanRoots = [
  "package.json",
  "wrangler.jsonc",
  "WORKER_ORCHESTRATOR_DEPLOY_CHECKLIST.md",
  path.join("workers", "orchestrator"),
];

const ignoredDirs = new Set(["node_modules", ".git", ".wrangler", ".wrangler-config", "dist", "coverage"]);
const ignoredFiles = new Set(["workers/orchestrator/src/worker-configuration.d.ts"]);

const rules = [
  {
    ruleId: "openai-secret-key",
    regex: /\bsk-[A-Za-z0-9_-]{20,}\b/g,
    message: "Potential OpenAI secret key.",
  },
  {
    ruleId: "aws-access-key",
    regex: /\bAKIA[0-9A-Z]{16}\b/g,
    message: "Potential AWS access key.",
  },
  {
    ruleId: "real-worker-token-env",
    regex: /\b(?:WORKER_API_TOKEN|BRIDGE_API_TOKEN|ADMIN_API_TOKEN)\s*=\s*(?!replace-with-|local-)[^\s#]+/gi,
    message: "Potential committed Worker orchestrator token value.",
  },
  {
    ruleId: "literal-bearer-token",
    regex: /\bBearer\s+(?!\$\{|local-|replace-with-|wrong\b|placeholder\b)[A-Za-z0-9._~+/=-]{20,}/gi,
    message: "Potential literal bearer token.",
  },
];

const scannedFiles = [];
const violations = [];

for (const item of scanRoots) {
  const target = path.join(root, item);
  if (!fs.existsSync(target)) {
    continue;
  }
  for (const file of collectFiles(target)) {
    const rel = relativePath(file);
    if (ignoredFiles.has(rel)) {
      continue;
    }
    const source = fs.readFileSync(file, "utf8");
    scannedFiles.push(rel);
    for (const rule of rules) {
      rule.regex.lastIndex = 0;
      for (const match of source.matchAll(rule.regex)) {
        const location = lineColumnForOffset(source, match.index || 0);
        violations.push({
          file: rel,
          line: location.line,
          column: location.column,
          ruleId: rule.ruleId,
          message: rule.message,
        });
      }
    }
  }
}

const status = violations.length === 0 ? "pass" : "fail";
process.stdout.write(`${JSON.stringify({ status, scannedFiles, violations }, null, 2)}\n`);
process.exitCode = status === "pass" ? 0 : 1;

function collectFiles(target) {
  const stat = fs.statSync(target);
  if (stat.isFile()) {
    return [target];
  }
  const files = [];
  for (const entry of fs.readdirSync(target, { withFileTypes: true }).sort((a, b) => a.name.localeCompare(b.name))) {
    if (entry.isDirectory() && ignoredDirs.has(entry.name)) {
      continue;
    }
    const full = path.join(target, entry.name);
    if (entry.isDirectory()) {
      files.push(...collectFiles(full));
    } else if (entry.isFile() && isTextFile(entry.name)) {
      files.push(full);
    }
  }
  return files;
}

function isTextFile(name) {
  if (name === ".dev.vars" || name.startsWith(".dev.vars.")) {
    return true;
  }
  return /\.(?:c?js|mjs|ts|json|jsonc|md|txt|example|env|toml|yml|yaml)$/i.test(name) || name === ".gitignore";
}

function relativePath(file) {
  return path.relative(root, file).replace(/\\/g, "/");
}

function lineColumnForOffset(source, offset) {
  const before = source.slice(0, offset);
  const lines = before.split(/\r?\n/);
  return { line: lines.length, column: lines[lines.length - 1].length + 1 };
}
