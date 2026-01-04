/**
 * Output formatting for skill activation hook
 *
 * Handles all display formatting including skill injection banners,
 * already-loaded sections, recommended skills, and manual load reminders.
 */

import { existsSync, readFileSync } from 'fs';
import { join } from 'path';
import { SKILL_FILE_NAME } from './constants.js';
import { validateSkillName, validatePathContainment } from './security.js';

/**
 * Result of skill injection operation
 */
export interface SkillInjectionResult {
  /** Formatted output with skill content */
  output: string;
  /** Names of skills that were actually loaded successfully */
  loadedSkills: string[];
}

/**
 * Inject skill content into system context
 *
 * Reads skill files and formats them with XML tags for Claude to process.
 * Returns formatted string with banner and skill content, plus the list of
 * skills that were actually loaded (for accurate state tracking).
 *
 * Security: Validates skill names and path containment before reading files.
 *
 * @param skillNames - Names of skills to inject
 * @param skillsBase - Base directory for skills (hub/library/skills)
 * @returns Object with formatted output and list of actually loaded skills
 */
export function injectSkillContent(
  skillNames: string[],
  skillsBase: string
): SkillInjectionResult {
  const result: SkillInjectionResult = {
    output: '',
    loadedSkills: [],
  };

  if (skillNames.length === 0) return result;

  let output = '\n';
  output += '===========================================\n';
  output += 'AUTO-LOADED SKILLS\n';
  output += '===========================================\n\n';

  for (const skillName of skillNames) {
    // Security: Validate skill name
    if (!validateSkillName(skillName)) {
      console.error(`Security: Skipping invalid skill name: ${skillName}`);
      continue;
    }

    const skillPath = join(skillsBase, skillName, SKILL_FILE_NAME);

    // Security: Validate path containment
    if (!validatePathContainment(skillPath, skillsBase)) {
      console.error(`Security: Path containment violation for skill: ${skillName}`);
      continue;
    }

    if (existsSync(skillPath)) {
      try {
        const skillContent = readFileSync(skillPath, 'utf-8');

        output += `<skill name="${skillName}">\n`;
        output += skillContent;
        output += `\n</skill>\n\n`;

        // Track successful load
        result.loadedSkills.push(skillName);
      } catch (err) {
        console.error(`Failed to load skill ${skillName}:`, err);
      }
    } else {
      console.warn(`Skill file not found: ${skillPath}`);
    }
  }

  output += '===========================================\n';
  // Report ACTUAL loaded count, not requested count
  output += `Loaded ${result.loadedSkills.length} skill(s): ${result.loadedSkills.join(', ')}\n`;
  output += '===========================================\n';

  result.output = output;
  return result;
}

/**
 * Format skill activation check banner
 *
 * Shows header banner for skill activation check section with decorator lines.
 *
 * @returns Formatted banner string
 */
export function formatActivationBanner(): string {
  let output = '';
  output += '===========================================\n';
  output += 'SKILL ACTIVATION CHECK\n';
  output += '===========================================\n\n';
  return output;
}

/**
 * Format just-injected skills section
 *
 * Shows skills that were just loaded in this turn with their injection type.
 *
 * @param injectedSkills - Skills that were just injected
 * @param criticalSkills - Skills injected as critical
 * @param affinitySkills - Skills injected via affinity
 * @param promotedSkills - Skills promoted from suggested
 * @returns Formatted section string
 */
export function formatJustInjectedSection(
  injectedSkills: string[],
  criticalSkills: string[],
  affinitySkills: string[],
  promotedSkills: string[]
): string {
  if (injectedSkills.length === 0) return '';

  let output = '\nJUST LOADED:\n';

  injectedSkills.forEach((skill) => {
    let label = '';
    if (affinitySkills.includes(skill)) {
      label = ' (affinity)';
    } else if (promotedSkills.includes(skill)) {
      label = ' (promoted)';
    } else if (criticalSkills.includes(skill)) {
      label = ' (critical)';
    }
    output += `  -> ${skill}${label}\n`;
  });

  return output;
}

/**
 * Format already-loaded skills section
 *
 * Shows skills that were loaded in previous turns (for user awareness).
 * Only shown when no new skills are being injected.
 *
 * @param alreadyLoaded - Skills already acknowledged in this conversation
 * @returns Formatted section string
 */
export function formatAlreadyLoadedSection(alreadyLoaded: string[]): string {
  if (alreadyLoaded.length === 0) return '';

  let output = '\nALREADY LOADED:\n';
  alreadyLoaded.forEach((name) => {
    output += `  -> ${name}\n`;
  });
  return output;
}

/**
 * Format recommended skills section
 *
 * Shows skills that were suggested but not auto-loaded (available for manual loading).
 *
 * @param recommendedSkills - Skills in suggested tier (0.50-0.65 confidence)
 * @param scores - Optional confidence scores to display
 * @returns Formatted section string
 */
export function formatRecommendedSection(
  recommendedSkills: string[],
  scores?: Record<string, number>
): string {
  if (recommendedSkills.length === 0) return '';

  let output = '\nRECOMMENDED SKILLS (not auto-loaded):\n';
  recommendedSkills.forEach((name) => {
    output += `  -> ${name}`;
    if (scores && scores[name]) {
      output += ` (${scores[name].toFixed(2)})`;
    }
    output += '\n';
  });
  output += '\nOptional: Use Skill tool to load if needed\n';
  return output;
}

/**
 * Format manual load section for skills with autoInject: false
 *
 * Shows skills that were matched but require manual loading via Skill tool.
 *
 * @param manualSkills - Skills that need manual loading
 * @returns Formatted section string
 */
export function formatManualLoadSection(manualSkills: string[]): string {
  if (manualSkills.length === 0) return '';

  let output = '\nMANUAL LOAD REQUIRED (autoInject: false):\n';
  manualSkills.forEach((name) => (output += `  -> ${name}\n`));
  output += '\nACTION: Use Skill tool for these skills\n';
  return output;
}

/**
 * Format closing banner for skill activation check
 *
 * @returns Formatted closing banner
 */
export function formatClosingBanner(): string {
  return '===========================================\n';
}
