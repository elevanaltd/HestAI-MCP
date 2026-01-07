===SKILL:REGISTRY_PROTOCOL===
META:
  TYPE::SKILL
  VERSION::"1.0"
  PURPOSE::"Protocol for official architectural change approval"

§1::APPROVAL_WORKFLOW
PROTOCOL::[
  HOOK_BLOCK_ANALYSIS::"Review /tmp/blocked-* files created by architectural protection hooks",
  ARCHITECTURAL_ASSESSMENT::"Evaluate system architecture coherence, scalability, design pattern compliance",
  REGISTRY_INTEGRATION::"Use mcp__hestai__registry for official approval/rejection workflow",
  APPROVAL_FORMAT::"TECHNICAL-ARCHITECT-APPROVED: [official-registry-token]",
  REJECTION_GUIDANCE::"Provide clear architectural guidance without token for rejected changes"
]

§2::SCOPE
DOMAINS::[
  DATABASE_DESIGN::"Schema changes, normalization patterns, indexing",
  INFRASTRUCTURE_ARCHITECTURE::"Deployment patterns, scaling strategies",
  API_DESIGN::"Interface patterns, protocol selection",
  SYSTEM_BOUNDARIES::"Module separation, dependency management",
  PERFORMANCE_ARCHITECTURE::"Caching strategies, resource allocation",
  SECURITY_ARCHITECTURE::"Authentication patterns, authorization models"
]

===END===
