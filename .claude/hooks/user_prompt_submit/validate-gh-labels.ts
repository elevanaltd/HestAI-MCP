#!/usr/bin/env node
/**
 * Pre-submit hook: Validates GitHub issue labels before command execution
 *
 * Prevents "label not found" errors by:
 * 1. Detecting `gh issue create` commands with --label flags
 * 2. Fetching valid labels from the repository
 * 3. Filtering out invalid labels and warning the agent
 *
 * Exit codes:
 * - 0: Command is valid or modified successfully
 * - 1: Critical error (blocks execution)
 */

import { execSync } from 'child_process';

interface HookContext {
  text: string;
  conversationId: string;
}

// Cache valid labels to avoid repeated API calls
let cachedLabels: string[] | null = null;
let cacheTimestamp: number = 0;
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes

/**
 * Fetch valid labels from GitHub repository
 */
function getValidLabels(): string[] {
  const now = Date.now();

  // Return cached labels if still valid
  if (cachedLabels && (now - cacheTimestamp) < CACHE_TTL) {
    return cachedLabels;
  }

  try {
    const output = execSync('gh label list --json name --jq ".[].name"', {
      encoding: 'utf-8',
      stdio: ['pipe', 'pipe', 'pipe']
    });

    cachedLabels = output.trim().split('\n').filter(Boolean);
    cacheTimestamp = now;
    return cachedLabels;
  } catch (error) {
    // If we can't fetch labels, skip validation to avoid blocking
    console.error('Warning: Could not fetch GitHub labels. Skipping validation.');
    return [];
  }
}

/**
 * Extract labels from gh issue create command
 */
function extractLabelsFromCommand(command: string): string[] {
  const labelMatches = command.matchAll(/--label[s]?\s+["']?([^"'\s]+)["']?/g);
  const labels: string[] = [];

  for (const match of labelMatches) {
    // Handle comma-separated labels
    const labelString = match[1];
    labels.push(...labelString.split(',').map(l => l.trim()));
  }

  return labels;
}

/**
 * Validate and filter labels
 */
function validateLabels(requestedLabels: string[], validLabels: string[]): {
  valid: string[];
  invalid: string[];
} {
  if (validLabels.length === 0) {
    // Skip validation if we couldn't fetch valid labels
    return { valid: requestedLabels, invalid: [] };
  }

  const valid: string[] = [];
  const invalid: string[] = [];

  for (const label of requestedLabels) {
    if (validLabels.includes(label)) {
      valid.push(label);
    } else {
      invalid.push(label);
    }
  }

  return { valid, invalid };
}

/**
 * Replace labels in command with validated labels
 */
function replaceLabelsInCommand(command: string, validLabels: string[]): string {
  // Remove all existing --label/--labels flags
  let cleaned = command.replace(/--labels?\s+["']?[^"'\s]+["']?/g, '').trim();

  // Add back only valid labels
  if (validLabels.length > 0) {
    const labelArg = `--label "${validLabels.join(',')}"`;
    // Insert before the command ends (before any trailing quotes or newlines)
    cleaned = cleaned.replace(/(\s*)$/, ` ${labelArg}$1`);
  }

  return cleaned;
}

/**
 * Main hook logic
 */
async function main() {
  try {
    const input = await new Promise<string>((resolve) => {
      let data = '';
      process.stdin.on('data', (chunk) => data += chunk);
      process.stdin.on('end', () => resolve(data));
    });

    const context: HookContext = JSON.parse(input);
    const text = context.text;

    // Check if this is a gh issue create command with labels
    if (!text.includes('gh issue create') || !text.match(/--labels?/)) {
      // Not a gh issue command with labels, pass through
      console.log(JSON.stringify({ text }));
      process.exit(0);
    }

    // Extract requested labels
    const requestedLabels = extractLabelsFromCommand(text);

    if (requestedLabels.length === 0) {
      // No labels to validate
      console.log(JSON.stringify({ text }));
      process.exit(0);
    }

    // Get valid labels from repository
    const validLabels = getValidLabels();

    // Validate labels
    const { valid, invalid } = validateLabels(requestedLabels, validLabels);

    if (invalid.length === 0) {
      // All labels are valid
      console.log(JSON.stringify({ text }));
      process.exit(0);
    }

    // Some labels are invalid - modify the command
    const modifiedText = replaceLabelsInCommand(text, valid);

    // Build warning message
    const warnings: string[] = [];
    warnings.push('⚠️  GitHub Label Validation:');
    warnings.push(`   Invalid labels removed: ${invalid.join(', ')}`);

    if (valid.length > 0) {
      warnings.push(`   Valid labels kept: ${valid.join(', ')}`);
    } else {
      warnings.push('   No valid labels provided. Command will proceed without labels.');
    }

    warnings.push('');
    warnings.push('💡 Tip: Use the "github-labels" skill to see all valid labels.');
    warnings.push('   Valid labels include: bug, enhancement, documentation, adr, rfc, priority:*, phase:*, area:*, etc.');

    // Output modified text with warnings
    console.log(JSON.stringify({
      text: modifiedText,
      warning: warnings.join('\n')
    }));

    process.exit(0);

  } catch (error) {
    // On any error, pass through original text to avoid blocking
    console.error('Hook error:', error);
    process.exit(0);
  }
}

main();
