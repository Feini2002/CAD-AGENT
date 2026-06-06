#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";

const repoRoot = process.cwd();
const sourceRoot = path.join(repoRoot, "workers", "orchestrator", "src");

const moduleImportRules = [
  {
    ruleId: "node-child-process-import",
    test: (specifier) => /^(node:)?child_process$/i.test(specifier),
    message: "Worker source must not import child_process or node:child_process.",
  },
  {
    ruleId: "node-fs-import",
    test: (specifier) => /^(node:)?fs(\/promises)?$/i.test(specifier),
    message: "Worker source must not import local filesystem modules.",
  },
  {
    ruleId: "cad-mcp-import",
    test: (specifier) => /\bcad[-_]?mcp\b/i.test(specifier),
    message: "Worker source must not import CAD-MCP execution modules.",
  },
  {
    ruleId: "autocad-import",
    test: (specifier) => /\bauto[-_]?cad\b|\bautocad\b/i.test(specifier),
    message: "Worker source must not import AutoCAD execution modules.",
  },
  {
    ruleId: "dwg-execution-import",
    test: (specifier) => /\bdwg\b/i.test(specifier) && /\b(save|writer|execute|executor|command|local)\b/i.test(specifier),
    message: "Worker source must not import DWG save or local DWG execution modules.",
  },
];

const moduleSpecifierPatterns = [
  /\bimport\s+(?:type\s+)?(?:[^'"]*?\s+from\s+)?["']([^"']+)["']/g,
  /\bexport\s+(?:type\s+)?[^'"]*?\s+from\s+["']([^"']+)["']/g,
  /\b(?:require|import)\s*\(\s*["']([^"']+)["']\s*\)/g,
];

const executableCodeRules = [
  {
    ruleId: "child-process-identifier",
    regex: /\bchild_process\b/g,
    message: "Worker source must not reference child_process.",
  },
  {
    ruleId: "exec-call",
    regex: /(?<![.\w$])(?:exec|execFile|execSync|execFileSync)\s*\(/g,
    message: "Worker source must not call local exec APIs.",
  },
  {
    ruleId: "spawn-call",
    regex: /(?<![.\w$])(?:spawn|spawnSync|fork)\s*\(/g,
    message: "Worker source must not call local spawn/fork APIs.",
  },
  {
    ruleId: "shell-command-identifier",
    regex: /\b(?:cmd|cmd\.exe|powershell|powershell\.exe|pwsh|pwsh\.exe)\b/gi,
    message: "Worker source must not reference local shell command identifiers.",
  },
  {
    ruleId: "cad-mcp-execution-call",
    regex: /\b(?:executeCadMcp|runCadMcp|invokeCadMcp|cadMcpExecute|executeCADMCP|runCADMCP)\b/g,
    message: "Worker source must not call CAD-MCP execution helpers.",
  },
  {
    ruleId: "autocad-execution-call",
    regex: /\b(?:executeAutoCAD|executeAutocad|runAutoCAD|runAutocad|invokeAutoCAD|invokeAutocad|autocadExecute|autoCadExecute)\b/g,
    message: "Worker source must not call AutoCAD execution helpers.",
  },
  {
    ruleId: "dwg-save-call",
    regex: /\b(?:save_current_dwg|saveCurrentDwg|saveCurrentDWG|saveDwg|saveDWG|dwgSave|saveAsCurrentDwg)\b\s*\(/g,
    message: "Worker source must not call DWG save helpers.",
  },
  {
    ruleId: "saved-current-dwg-enabled",
    regex: /\b(?:savedCurrentDwg|workerSavesCurrentDwg)\s*:\s*true\b/g,
    message: "Worker source must not enable current DWG save capability.",
  },
  {
    ruleId: "user-supplied-outbound-fetch",
    regex:
      /\bfetch\s*\(\s*(?:(?:body|input|payload|params|query)\s*\.\s*[A-Za-z0-9_$]*(?:url|URL|Url)|(?:asString|stringFrom)\s*\(\s*(?:body|input|payload|params|query)\s*\.)/g,
    message: "Worker source must not fetch arbitrary user-supplied outbound URLs.",
  },
];

const dangerousLiteralRules = [
  {
    ruleId: "child-process-literal",
    regex: /(['"`])(?:node:)?child_process\1/gi,
    message: "Worker source must not declare child_process as a usable capability.",
  },
  {
    ruleId: "exec-tool-literal",
    regex: /(['"`])(?:exec|execFile|execSync|spawn|spawnSync|fork)\1/g,
    message: "Worker source must not declare exec/spawn as usable capabilities.",
  },
  {
    ruleId: "shell-tool-literal",
    regex: /(['"`])(?:cmd(?:\.exe)?|powershell(?:\.exe)?|pwsh(?:\.exe)?)\1/gi,
    message: "Worker source must not declare cmd or powershell as usable capabilities.",
  },
  {
    ruleId: "shell-arbitrary-literal",
    regex: /(['"`])shell_arbitrary\1/g,
    message: "Worker source must not declare arbitrary shell as a usable capability.",
  },
  {
    ruleId: "cad-mcp-execution-literal",
    regex:
      /(['"`])(?:cad[-_ ]?mcp[-_ ]?(?:exec|execute|run|command)|(?:exec|execute|run|command)[-_ ]?cad[-_ ]?mcp|cad_mcp_execute|cad-mcp-execute)\1/gi,
    message: "Worker source must not declare CAD-MCP execution as a usable capability.",
  },
  {
    ruleId: "autocad-execution-literal",
    regex:
      /(['"`])(?:(?:auto[-_ ]?cad|autocad)[-_ ]?(?:exec|execute|run|command)|(?:exec|execute|run|command)[-_ ]?(?:auto[-_ ]?cad|autocad)|autocad_execute|autocad-execute)\1/gi,
    message: "Worker source must not declare AutoCAD execution as a usable capability.",
  },
  {
    ruleId: "dwg-save-literal",
    regex: /(['"`])(?:save_current_dwg|dwg_save|save_dwg|saveCurrentDwg|saveCurrentDWG)\1/g,
    message: "Worker source must not declare DWG save as a usable capability.",
  },
];

function main() {
  const scannedFiles = [];
  const violations = [];

  if (!fs.existsSync(sourceRoot)) {
    violations.push({
      file: relativePath(sourceRoot),
      line: 0,
      column: 0,
      ruleId: "source-root-missing",
      match: "",
      message: "Expected Worker source directory does not exist.",
    });
    writeResult(scannedFiles, violations);
    return;
  }

  for (const filePath of collectTsFiles(sourceRoot)) {
    const rel = relativePath(filePath);
    scannedFiles.push(rel);
    const source = fs.readFileSync(filePath, "utf8");
    violations.push(...scanSource(rel, source));
  }

  writeResult(scannedFiles, violations);
}

function collectTsFiles(dir) {
  const entries = fs.readdirSync(dir, { withFileTypes: true }).sort((a, b) => a.name.localeCompare(b.name));
  const files = [];
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      files.push(...collectTsFiles(fullPath));
    } else if (entry.isFile() && entry.name.endsWith(".ts") && !entry.name.endsWith(".d.ts")) {
      files.push(fullPath);
    }
  }
  return files;
}

function scanSource(file, source) {
  const violations = [];
  const commentFree = maskComments(source);
  const executableCode = maskCommentsAndStrings(source);
  const policyLines = findPolicyDeclarationLines(file, commentFree);

  for (const pattern of moduleSpecifierPatterns) {
    pattern.lastIndex = 0;
    for (const match of commentFree.matchAll(pattern)) {
      const specifier = match[1];
      const specifierOffset = match.index + match[0].indexOf(specifier);
      for (const rule of moduleImportRules) {
        if (rule.test(specifier)) {
          violations.push(buildViolation(file, source, specifierOffset, rule, specifier));
        }
      }
    }
  }

  for (const rule of executableCodeRules) {
    rule.regex.lastIndex = 0;
    for (const match of executableCode.matchAll(rule.regex)) {
      violations.push(buildViolation(file, source, match.index, rule, match[0].trim()));
    }
  }

  for (const rule of dangerousLiteralRules) {
    rule.regex.lastIndex = 0;
    for (const match of commentFree.matchAll(rule.regex)) {
      const location = lineColumnForOffset(source, match.index);
      if (isAllowedPolicyLiteral(file, source, location.line, policyLines)) {
        continue;
      }
      violations.push(buildViolation(file, source, match.index, rule, stripQuotes(match[0])));
    }
  }

  return violations;
}

function findPolicyDeclarationLines(file, source) {
  const baseName = path.basename(file);
  const lines = source.split(/\r?\n/);
  const policyLines = new Set();
  let inPolicyBlock = false;
  let blockDepth = 0;

  for (let index = 0; index < lines.length; index += 1) {
    const lineNumber = index + 1;
    const line = lines[index];
    const startsPolicyBlock = lineLooksLikePolicyDeclaration(line) || baseName === "constants.ts";

    if (startsPolicyBlock) {
      inPolicyBlock = true;
      blockDepth = Math.max(blockDepth, 0);
    }

    if (inPolicyBlock || startsPolicyBlock) {
      policyLines.add(lineNumber);
    }

    if (inPolicyBlock) {
      blockDepth += bracketDelta(line);
      if (blockDepth <= 0 && /[;\]}),]\s*$/.test(line)) {
        inPolicyBlock = false;
        blockDepth = 0;
      }
    }
  }

  return policyLines;
}

function isAllowedPolicyLiteral(file, source, lineNumber, policyLines) {
  const line = getLine(source, lineNumber);
  if (lineLooksLikeExecutableCapability(line)) {
    return false;
  }
  if (policyLines.has(lineNumber)) {
    return true;
  }
  const baseName = path.basename(file);
  return baseName === "constants.ts" && !lineLooksLikeExecutableCapability(line);
}

function lineLooksLikePolicyDeclaration(line) {
  return /\b(?:FORBIDDEN_[A-Z0-9_]*|forbidden[A-Za-z0-9_]*|forbidden_[a-z0-9_]*|blockedReasons|securityBlocks|boundaries|workerExecutesShell|workerSavesCurrentDwg)\b/.test(
    line,
  );
}

function lineLooksLikeExecutableCapability(line) {
  return /\b(?:allowedTools|requestedActions|capabilities|supportedStages|DEFAULT_ALLOWED|ENABLED_TOOLS|AVAILABLE_TOOLS|toolName|actionName)\b/.test(
    line,
  ) && !/\bforbidden[A-Za-z0-9_]*\b|\bFORBIDDEN_[A-Z0-9_]*\b/.test(line);
}

function bracketDelta(line) {
  let delta = 0;
  for (const char of line) {
    if (char === "[" || char === "{" || char === "(") {
      delta += 1;
    } else if (char === "]" || char === "}" || char === ")") {
      delta -= 1;
    }
  }
  return delta;
}

function maskComments(source) {
  return maskSource(source, { strings: false, comments: true });
}

function maskCommentsAndStrings(source) {
  return maskSource(source, { strings: true, comments: true });
}

function maskSource(source, options) {
  const chars = [...source];
  let state = "code";
  let quote = "";

  for (let index = 0; index < chars.length; index += 1) {
    const char = chars[index];
    const next = chars[index + 1] || "";

    if (state === "code") {
      if (options.comments && char === "/" && next === "/") {
        chars[index] = " ";
        chars[index + 1] = " ";
        index += 1;
        state = "line-comment";
        continue;
      }
      if (options.comments && char === "/" && next === "*") {
        chars[index] = " ";
        chars[index + 1] = " ";
        index += 1;
        state = "block-comment";
        continue;
      }
      if (options.strings && (char === "'" || char === '"' || char === "`")) {
        quote = char;
        chars[index] = " ";
        state = "string";
        continue;
      }
      continue;
    }

    if (state === "line-comment") {
      if (char === "\n" || char === "\r") {
        state = "code";
      } else {
        chars[index] = " ";
      }
      continue;
    }

    if (state === "block-comment") {
      if (char === "*" && next === "/") {
        chars[index] = " ";
        chars[index + 1] = " ";
        index += 1;
        state = "code";
      } else if (char !== "\n" && char !== "\r") {
        chars[index] = " ";
      }
      continue;
    }

    if (state === "string") {
      if (char === "\\") {
        chars[index] = " ";
        if (next) {
          chars[index + 1] = next === "\n" || next === "\r" ? next : " ";
          index += 1;
        }
        continue;
      }
      if (char === quote) {
        chars[index] = " ";
        state = "code";
      } else if (char !== "\n" && char !== "\r") {
        chars[index] = " ";
      }
    }
  }

  return chars.join("");
}

function buildViolation(file, source, offset, rule, match) {
  const location = lineColumnForOffset(source, offset);
  return {
    file,
    line: location.line,
    column: location.column,
    ruleId: rule.ruleId,
    match,
    message: rule.message,
  };
}

function lineColumnForOffset(source, offset) {
  const before = source.slice(0, offset);
  const lines = before.split(/\r?\n/);
  return {
    line: lines.length,
    column: lines[lines.length - 1].length + 1,
  };
}

function getLine(source, lineNumber) {
  return source.split(/\r?\n/)[lineNumber - 1] || "";
}

function stripQuotes(value) {
  return value.replace(/^['"`]|['"`]$/g, "");
}

function relativePath(filePath) {
  return path.relative(repoRoot, filePath).split(path.sep).join("/");
}

function writeResult(scannedFiles, violations) {
  const status = violations.length === 0 ? "pass" : "fail";
  const result = {
    status,
    scannedFiles,
    violations,
  };
  process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
  process.exitCode = status === "pass" ? 0 : 1;
}

main();
