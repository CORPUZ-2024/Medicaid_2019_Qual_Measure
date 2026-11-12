"""Child and Adult Health Care Quality Measures - Core Set pipeline.

Implements ``project_plan/Medicaid_ViewB_GitHub_Pages_Implementation_Spec_v2.txt``
(Sections 1, 2.2-2.3, 3.1, 4). Regional (2.4) and risk (3.2) analyses were
removed in this version; see the 2026_Version_V1_Expanded_Scope branch.
"""

__all__ = [
    "config",
    "regions",
    "ingest",
    "clean",
    "viewb",
    "trend",
    "spec_audit",
    "build",
]
