/**
 * Security validation utilities for skill activation system
 *
 * Implements CRS-mandated security validations:
 * - Skill name allowlist pattern: ^[a-z0-9][a-z0-9_-]*$
 * - Path containment: resolved paths must start with skillsBase
 * - Directory existence verification
 */

import { existsSync, realpathSync } from 'fs';
import { resolve, normalize } from 'path';

/**
 * Skill name validation pattern (allowlist)
 *
 * Requirements:
 * - Must start with lowercase letter or digit
 * - Can contain lowercase letters, digits, underscores, and hyphens
 * - Prevents directory traversal via ../
 * - Prevents shell injection via special characters
 */
const SKILL_NAME_PATTERN = /^[a-z0-9][a-z0-9_-]*$/;

/**
 * Validate skill name against allowlist pattern
 *
 * Security: Prevents directory traversal and injection attacks by
 * ensuring skill names contain only safe characters.
 *
 * @param skillName - Name of the skill to validate
 * @returns true if valid, false otherwise
 *
 * @example
 * ```typescript
 * validateSkillName('test-coverage');  // true
 * validateSkillName('build_execution'); // true
 * validateSkillName('../etc/passwd');  // false
 * validateSkillName('skill; rm -rf /'); // false
 * ```
 */
export function validateSkillName(skillName: string): boolean {
  if (!skillName || typeof skillName !== 'string') {
    return false;
  }

  // Check against allowlist pattern
  if (!SKILL_NAME_PATTERN.test(skillName)) {
    return false;
  }

  // Additional check: no path separators
  if (skillName.includes('/') || skillName.includes('\\')) {
    return false;
  }

  return true;
}

/**
 * Validate path containment within base directory
 *
 * Security: Prevents directory traversal attacks by ensuring the
 * resolved path stays within the designated base directory.
 *
 * @param targetPath - Path to validate
 * @param basePath - Base directory that must contain the target
 * @returns true if target is within base, false otherwise
 *
 * @example
 * ```typescript
 * validatePathContainment('/base/skills/test.md', '/base/skills');  // true
 * validatePathContainment('/base/skills/../etc/passwd', '/base/skills');  // false
 * ```
 */
export function validatePathContainment(targetPath: string, basePath: string): boolean {
  try {
    // Normalize paths to handle . and ..
    const normalizedTarget = normalize(resolve(targetPath));
    const normalizedBase = normalize(resolve(basePath));

    // Ensure base path ends with separator for proper prefix matching
    const baseWithSep = normalizedBase.endsWith('/') ? normalizedBase : normalizedBase + '/';

    // Check if target starts with base (or equals base)
    return normalizedTarget === normalizedBase || normalizedTarget.startsWith(baseWithSep);
  } catch {
    // Any path resolution error means invalid path
    return false;
  }
}

/**
 * Validate directory exists and is accessible
 *
 * Security: Ensures the target directory exists before attempting
 * to read files from it.
 *
 * @param dirPath - Directory path to validate
 * @returns true if directory exists, false otherwise
 */
export function validateDirectoryExists(dirPath: string): boolean {
  try {
    return existsSync(dirPath);
  } catch {
    return false;
  }
}

/**
 * Get the canonical (real) path of a file/directory
 *
 * Security: Resolves symlinks and normalizes the path to detect
 * symlink-based traversal attacks.
 *
 * @param targetPath - Path to resolve
 * @returns Canonical path or null if path doesn't exist
 */
export function getCanonicalPath(targetPath: string): string | null {
  try {
    return realpathSync(targetPath);
  } catch {
    return null;
  }
}
