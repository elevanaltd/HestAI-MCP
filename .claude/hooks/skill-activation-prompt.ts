#!/usr/bin/env node
/**
 * Skill Activation Hook - Main Entry Point
 *
 * Orchestrates skill auto-loading using modular components.
 * Analyzes user prompts via AI, filters/promotes skills, and injects
 * skill content into the conversation context.
 *
 * Security validations:
 * - Skill name allowlist: ^[a-z0-9][a-z0-9_-]*$
 * - Path containment: resolved paths must start with skillsBase
 * - Directory existence verification before injection
 */

import { readFileSync } from 'fs';
import { join } from 'path';
import { analyzeIntent } from './lib/intent-analyzer.js';
import { resolveSkillDependencies } from './lib/skill-resolution.js';
import { filterAndPromoteSkills, findAffinityInjections } from './lib/skill-filtration.js';
import { readAcknowledgedSkills, writeSessionState } from './lib/skill-state-manager.js';
import {
  injectSkillContent,
  formatActivationBanner,
  formatJustInjectedSection,
  formatAlreadyLoadedSection,
  formatRecommendedSection,
  formatManualLoadSection,
  formatClosingBanner,
} from './lib/output-formatter.js';
import { validateSkillName, validatePathContainment } from './lib/security.js';
import type { SkillRulesConfig } from './lib/types.js';
import { debugLog } from './lib/debug-logger.js';

/**
 * Hook input from Claude
 */
interface HookInput {
  session_id: string;
  conversation_id?: string;
  transcript_path: string;
  cwd?: string;
  permission_mode: string;
  prompt: string;
}

/**
 * Main hook execution
 */
async function main(): Promise<void> {
  try {
    // Read input from stdin
    const input = readFileSync(0, 'utf-8');
    const data: HookInput = JSON.parse(input);

    // Determine project directory and skills base path
    // Precedence:
    // 1. HESTAI_HUB_SKILLS_PATH (hub-level, set by setup-mcp.sh)
    // 2. HESTAI_SKILLS_PATH (explicit override or set by hook.sh)
    // 3. Local project hub/library/skills/ fallback
    const projectDir = data.cwd || process.env.CLAUDE_PROJECT_DIR || process.cwd();
    const skillsBase =
      process.env.HESTAI_HUB_SKILLS_PATH ||
      process.env.HESTAI_SKILLS_PATH ||
      join(projectDir, 'hub', 'library', 'skills');

    // Load skill rules
    const rulesPath = join(projectDir, '.claude', 'hooks', 'skill-rules.json');
    const rules: SkillRulesConfig = JSON.parse(readFileSync(rulesPath, 'utf-8'));

    // Security: Validate all skill names in rules
    for (const skillName of Object.keys(rules.skills)) {
      if (!validateSkillName(skillName)) {
        console.error(`Security: Skipping invalid skill name: ${skillName}`);
        delete rules.skills[skillName];
      }
    }

    // Analyze user intent with AI
    const analysis = await analyzeIntent(data.prompt, rules.skills);

    // Security: Filter out invalid skill names from analysis results
    const requiredDomainSkills = (analysis.required || []).filter(
      (name) => name in rules.skills && validateSkillName(name)
    );
    const suggestedDomainSkills = (analysis.suggested || []).filter(
      (name) => name in rules.skills && validateSkillName(name)
    );

    // DEBUG: Log AI analysis results
    debugLog('=== NEW PROMPT ===');
    debugLog(`Prompt: ${data.prompt}`);
    debugLog('AI Analysis Results:');
    debugLog(`  Required (critical): ${JSON.stringify(requiredDomainSkills)}`);
    debugLog(`  Suggested: ${JSON.stringify(suggestedDomainSkills)}`);
    debugLog(`  Scores: ${JSON.stringify(analysis.scores || {})}`);

    // Output banner
    let output = formatActivationBanner();

    // Handle skill injection for domain skills only
    const hasMatchedSkills = requiredDomainSkills.length > 0 || suggestedDomainSkills.length > 0;
    if (hasMatchedSkills) {
      // State management
      const stateDir = join(projectDir, '.claude', 'hooks', 'state');
      const stateId = data.conversation_id || data.session_id;
      const existingAcknowledged = readAcknowledgedSkills(stateDir, stateId);

      // DEBUG: Log session state
      debugLog('Session State:');
      debugLog(`  Already acknowledged: ${JSON.stringify(existingAcknowledged)}`);

      // Filter and promote skills
      const filtration = filterAndPromoteSkills(
        requiredDomainSkills,
        suggestedDomainSkills,
        existingAcknowledged,
        rules.skills
      );

      // DEBUG: Log filtration results
      debugLog('Filtration Results:');
      debugLog(`  To inject: ${JSON.stringify(filtration.toInject)}`);
      debugLog(`  Promoted: ${JSON.stringify(filtration.promoted)}`);
      debugLog(`  Remaining suggested: ${JSON.stringify(filtration.remainingSuggested)}`);

      // Find affinity injections (bidirectional, free of slot cost)
      const affinitySkills = findAffinityInjections(
        filtration.toInject,
        existingAcknowledged,
        rules.skills
      );

      // DEBUG: Log affinity results
      debugLog('Affinity Injection:');
      debugLog(`  Affinity skills found: ${JSON.stringify(affinitySkills)}`);

      // Resolve dependencies and inject skills
      const allSkillsToInject = [...filtration.toInject, ...affinitySkills];
      // Track only skills that were ACTUALLY loaded successfully (not just attempted)
      const successfullyInjected: string[] = [];

      // DEBUG: Log combined skills before dependency resolution
      debugLog('Combined Skills (before dependency resolution):');
      debugLog(`  All skills to inject: ${JSON.stringify(allSkillsToInject)}`);

      if (allSkillsToInject.length > 0) {
        const resolvedSkills = resolveSkillDependencies(allSkillsToInject, rules.skills);

        // DEBUG: Log final injected skills
        debugLog('Final Injection:');
        debugLog(`  After dependency resolution: ${JSON.stringify(resolvedSkills)}`);

        // Inject skills individually (one console.log per skill)
        for (const skillName of resolvedSkills) {
          // Security: Validate skill name and path containment
          if (!validateSkillName(skillName)) {
            debugLog(`  Security: Skipping invalid skill name: ${skillName}`);
            continue;
          }

          const skillPath = join(skillsBase, skillName, 'SKILL.md');

          // Security: Validate path containment
          if (!validatePathContainment(skillPath, skillsBase)) {
            debugLog(`  Security: Path containment violation for: ${skillName}`);
            continue;
          }

          debugLog(`  Injecting skill: ${skillName} from ${skillPath}`);

          const injectionResult = injectSkillContent([skillName], skillsBase);
          if (injectionResult.output && injectionResult.loadedSkills.length > 0) {
            console.log(injectionResult.output);
            // Track ONLY successfully loaded skills for state
            successfullyInjected.push(...injectionResult.loadedSkills);
            debugLog(`  Injected ${skillName} (${injectionResult.output.length} chars)`);
          } else {
            debugLog(`  Failed to inject ${skillName} - no output generated`);
          }
        }
      }

      // Use successfullyInjected for all subsequent operations
      const injectedSkills = successfullyInjected;

      // Show just-injected skills in banner
      if (injectedSkills.length > 0) {
        output += formatJustInjectedSection(
          injectedSkills,
          filtration.toInject,
          affinitySkills,
          filtration.promoted
        );
      }

      // Show already-loaded skills
      const alreadyAcknowledged = [...requiredDomainSkills, ...suggestedDomainSkills].filter(
        (skill) => existingAcknowledged.includes(skill)
      );
      if (alreadyAcknowledged.length > 0 && injectedSkills.length === 0) {
        output += formatAlreadyLoadedSection(alreadyAcknowledged);
      }

      // Show remaining recommended skills
      output += formatRecommendedSection(filtration.remainingSuggested, analysis.scores);

      // Show manual-load required skills (autoInject: false)
      const manualSkills = [...requiredDomainSkills, ...suggestedDomainSkills].filter((skill) => {
        const skillRule = rules.skills[skill];
        return !existingAcknowledged.includes(skill) && skillRule?.autoInject === false;
      });
      output += formatManualLoadSection(manualSkills);

      output += formatClosingBanner();
      console.log(output);

      // Write session state
      if (injectedSkills.length > 0) {
        writeSessionState(
          stateDir,
          stateId,
          [...existingAcknowledged, ...injectedSkills],
          injectedSkills
        );
      }
    }
  } catch (err) {
    console.error('Skill activation hook error:', err);
    process.exit(0); // Don't fail the conversation on hook errors
  }
}

main();
