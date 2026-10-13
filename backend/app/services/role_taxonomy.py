import logging
import re

logger = logging.getLogger(__name__)

class RoleTaxonomy:
    """
    Centralized Role Taxonomy and Exclusion Dictionary.
    Maps canonical roles to equivalent/subordinate title patterns and strict negative patterns.
    """

    ROLE_TAXONOMY = {
        "Data Analyst": {
            "canonical": "Data Analyst",
            "domain": "DATA_ANALYTICS",
            "allowed_patterns": [
                r"\bdata\s+analyst\b",
                r"\bjunior\s+data\s+analyst\b",
                r"\bjr\.?\s+data\s+analyst\b",
                r"\bentry[- ]level\s+data\s+analyst\b",
                r"\bgraduate\s+data\s+analyst\b",
                r"\bbusiness\s+data\s+analyst\b",
                r"\breporting\s+analyst\b",
                r"\bbi\s+analyst\b",
                r"\bbusiness\s+intelligence\s+analyst\b",
                r"\banalytics\s+specialist\b",
                r"\bdata\s+analytics\s+specialist\b",
                r"\bdata\s+reporter\b",
                r"\bsql\s+data\s+analyst\b",
                r"\bpower\s*bi\s+analyst\b",
                r"\btableau\s+analyst\b",
            ],
            "excluded_patterns": [
                r"\baccountant\b",
                r"\baccounting\b",
                r"\bauditor\b",
                r"\bauditing\b",
                r"\bfinance\s+manager\b",
                r"\bfinancial\s+manager\b",
                r"\bbookkeeper\b",
                r"\bbookkeeping\b",
                r"\btax\s+consultant\b",
                r"\bsales\s+representative\b",
                r"\bsales\s+executive\b",
                r"\barchitect\b",
                r"\bsoftware\s+architect\b",
                r"\bclinical\b",
                r"\bnurse\b",
            ]
        },
        "Software Engineer": {
            "canonical": "Software Engineer",
            "domain": "SOFTWARE_ENGINEERING",
            "allowed_patterns": [
                r"\bsoftware\s+engineer\b",
                r"\bjunior\s+software\s+engineer\b",
                r"\bjr\.?\s+software\s+engineer\b",
                r"\bgraduate\s+software\s+engineer\b",
                r"\bentry[- ]level\s+software\s+engineer\b",
                r"\bsoftware\s+developer\b",
                r"\bjunior\s+developer\b",
                r"\bjr\.?\s+developer\b",
                r"\bentry[- ]level\s+developer\b",
                r"\bassociate\s+software\s+engineer\b",
                r"\bbackend\s+developer\b",
                r"\bback[- ]end\s+developer\b",
                r"\bbackend\s+engineer\b",
                r"\bback[- ]end\s+engineer\b",
                r"\bfrontend\s+developer\b",
                r"\bfront[- ]end\s+developer\b",
                r"\bfrontend\s+engineer\b",
                r"\bfront[- ]end\s+engineer\b",
                r"\bfull[- ]?stack\s+developer\b",
                r"\bfull[- ]?stack\s+engineer\b",
                r"\bweb\s+developer\b",
                r"\bpython\s+developer\b",
                r"\bjava\s+developer\b",
            ],
            "excluded_patterns": [
                r"\bsoftware\s+architect\b",
                r"\bsolution\s+architect\b",
                r"\bsolutions\s+architect\b",
                r"\benterprise\s+architect\b",
                r"\bbuilding\s+architect\b",
                r"\bconstruction\s+architect\b",
                r"\bcloud\s+architect\b",
                r"\bsystem\s+architect\b",
                r"\bchief\s+architect\b",
                r"\barchitect\b",
                r"\baccountant\b",
                r"\bauditor\b",
                r"\bsales\s+rep\b",
            ]
        },
        "Machine Learning Engineer": {
            "canonical": "Machine Learning Engineer",
            "domain": "DATA_SCIENCE_AI",
            "allowed_patterns": [
                r"\bmachine\s+learning\s+engineer\b",
                r"\bml\s+engineer\b",
                r"\bjr\.?\s+ml\s+engineer\b",
                r"\bjunior\s+machine\s+learning\s+engineer\b",
                r"\bai\s+engineer\b",
                r"\bartificial\s+intelligence\s+engineer\b",
                r"\bdeep\s+learning\s+engineer\b",
                r"\bnlp\s+engineer\b",
                r"\bcomputer\s+vision\s+engineer\b",
                r"\bapplied\s+(?:ml\s+|ai\s+)?scientist\b",
                r"\bml\s+scientist\b",
                r"\bmachine\s+learning\s+scientist\b",
                r"\bapplied\s+scientist\b",
                r"\bdata\s+scientist\b",
            ],
            "excluded_patterns": [
                r"\baccountant\b",
                r"\bgeneral\s+manager\b",
                r"\bsales\b",
                r"\bmarketing\b",
                r"\barchitect\b",
                r"\bbuilding\b",
            ]
        },
        "Data Scientist": {
            "canonical": "Data Scientist",
            "domain": "DATA_SCIENCE_AI",
            "allowed_patterns": [
                r"\bdata\s+scientist\b",
                r"\bjunior\s+data\s+scientist\b",
                r"\bjr\.?\s+data\s+scientist\b",
                r"\bassociate\s+data\s+scientist\b",
                r"\bdata\s+science\s+associate\b",
                r"\bmachine\s+learning\s+engineer\b",
                r"\bstatistician\b",
            ],
            "excluded_patterns": [
                r"\baccountant\b",
                r"\bauditor\b",
                r"\bsales\b",
                r"\barchitect\b",
            ]
        },
        "Java Developer": {
            "canonical": "Java Developer",
            "domain": "SOFTWARE_ENGINEERING",
            "allowed_patterns": [
                r"\bjava\s+developer\b",
                r"\bjava\s+software\s+engineer\b",
                r"\bjunior\s+java\s+developer\b",
                r"\bjr\.?\s+java\s+developer\b",
                r"\bspring\s+boot\s+developer\b",
                r"\bbackend\s+java\s+developer\b",
            ],
            "excluded_patterns": [
                r"\barchitect\b",
                r"\baccountant\b",
                r"\bsales\b",
            ]
        },
        "Python Developer": {
            "canonical": "Python Developer",
            "domain": "SOFTWARE_ENGINEERING",
            "allowed_patterns": [
                r"\bpython\s+developer\b",
                r"\bpython\s+software\s+engineer\b",
                r"\bjunior\s+python\s+developer\b",
                r"\bjr\.?\s+python\s+developer\b",
                r"\bdjango\s+developer\b",
                r"\bflask\s+developer\b",
                r"\bbackend\s+developer\s*\(\s*python\s*\)",
            ],
            "excluded_patterns": [
                r"\barchitect\b",
                r"\baccountant\b",
                r"\bsales\b",
            ]
        },
        "DevOps Engineer": {
            "canonical": "DevOps Engineer",
            "domain": "CLOUD_DEVOPS",
            "allowed_patterns": [
                r"\bdevops\s+engineer\b",
                r"\bjr\.?\s+devops\s+engineer\b",
                r"\bjunior\s+devops\s+engineer\b",
                r"\bcloud\s+devops\s+engineer\b",
                r"\bsite\s+reliability\s+engineer\b",
                r"\bsre\b",
                r"\bplatform\s+engineer\b",
                r"\bbuild\s+and\s+release\s+engineer\b",
            ],
            "excluded_patterns": [
                r"\barchitect\b",
                r"\baccountant\b",
                r"\bsales\b",
            ]
        },
        "Cloud Engineer": {
            "canonical": "Cloud Engineer",
            "domain": "CLOUD_DEVOPS",
            "allowed_patterns": [
                r"\bcloud\s+engineer\b",
                r"\bcloud\s+associate\b",
                r"\bjr\.?\s+cloud\s+engineer\b",
                r"\baws\s+engineer\b",
                r"\bazure\s+engineer\b",
                r"\bgcp\s+engineer\b",
                r"\bcloud\s+support\s+engineer\b",
            ],
            "excluded_patterns": [
                r"\bcloud\s+architect\b",
                r"\bsolutions\s+architect\b",
                r"\barchitect\b",
                r"\baccountant\b",
            ]
        },
        "Cybersecurity Analyst": {
            "canonical": "Cybersecurity Analyst",
            "domain": "CYBERSECURITY",
            "allowed_patterns": [
                r"\bcybersecurity\s+analyst\b",
                r"\bcyber\s+security\s+analyst\b",
                r"\binformation\s+security\s+analyst\b",
                r"\bsecurity\s+analyst\b",
                r"\bsoc\s+analyst\b",
                r"\bsecurity\s+operations\s+analyst\b",
            ],
            "excluded_patterns": [
                r"\baccountant\b",
                r"\barchitect\b",
                r"\bsales\b",
            ]
        },
        "Accountant": {
            "canonical": "Accountant",
            "domain": "ACCOUNTING_FINANCE",
            "allowed_patterns": [
                r"\baccountant\b",
                r"\bjunior\s+accountant\b",
                r"\baccounts\s+executive\b",
                r"\baccounts\s+assistant\b",
                r"\bfinance\s+executive\b",
                r"\bbookkeeper\b",
                r"\btax\s+accountant\b",
            ],
            "excluded_patterns": [
                r"\bsoftware\b",
                r"\bdeveloper\b",
                r"\bengineer\b",
                r"\barchitect\b",
            ]
        },
        "Software Architect": {
            "canonical": "Software Architect",
            "domain": "SOFTWARE_ARCHITECTURE",
            "allowed_patterns": [
                r"\bsoftware\s+architect\b",
                r"\bsolution\s+architect\b",
                r"\bsolutions\s+architect\b",
                r"\benterprise\s+architect\b",
                r"\bcloud\s+architect\b",
                r"\bsystem\s+architect\b",
            ],
            "excluded_patterns": [
                r"\bbuilding\s+architect\b",
                r"\binterior\s+architect\b",
                r"\bconstruction\b",
                r"\baccountant\b",
            ]
        }
    }

    # High-level domain exclusion rules (if target domain is X, never allow job domain Y)
    CROSS_DOMAIN_EXCLUSIONS = {
        "DATA_ANALYTICS": ["ACCOUNTING_FINANCE", "ARCHITECTURE", "HEALTHCARE", "CIVIL_ENGINEERING", "MECHANICAL_ENGINEERING"],
        "SOFTWARE_ENGINEERING": ["ACCOUNTING_FINANCE", "ARCHITECTURE", "HEALTHCARE", "CIVIL_ENGINEERING", "MECHANICAL_ENGINEERING", "LEGAL"],
        "DATA_SCIENCE_AI": ["ACCOUNTING_FINANCE", "ARCHITECTURE", "HEALTHCARE", "CIVIL_ENGINEERING"],
        "CLOUD_DEVOPS": ["ACCOUNTING_FINANCE", "ARCHITECTURE", "HEALTHCARE", "CIVIL_ENGINEERING"],
        "CYBERSECURITY": ["ACCOUNTING_FINANCE", "ARCHITECTURE", "HEALTHCARE", "CIVIL_ENGINEERING"],
        "ACCOUNTING_FINANCE": ["SOFTWARE_ENGINEERING", "DATA_SCIENCE_AI", "CLOUD_DEVOPS", "ARCHITECTURE", "HEALTHCARE"]
    }

    @classmethod
    def find_taxonomy_entry(cls, role_name: str):
        """Find matching taxonomy entry by canonical name or alias."""
        if not role_name:
            return None
        r_clean = role_name.strip().lower()

        # Exact match in dict keys
        for key, entry in cls.ROLE_TAXONOMY.items():
            if key.lower() == r_clean:
                return entry

        # Pattern match across allowed patterns
        for key, entry in cls.ROLE_TAXONOMY.items():
            for pat in entry["allowed_patterns"]:
                if re.search(pat, r_clean, re.IGNORECASE):
                    return entry

        return None

    @classmethod
    def evaluate_role_match(cls, target_role: str, job_title: str) -> dict:
        """
        Evaluate if a job_title is a legitimate match for target_role.
        Returns:
          {
            "match": bool,
            "status": "DIRECT_MATCH" | "ALLOWED_EQUIVALENT" | "STRICT_EXCLUSION" | "CROSS_DOMAIN_MISMATCH" | "UNMATCHED",
            "reason": str
          }
        """
        if not target_role or not job_title:
            return {"match": False, "is_allowed": False, "is_strictly_excluded": False, "status": "UNMATCHED", "reason": "Missing role or title"}

        title_lower = job_title.strip().lower()
        entry = cls.find_taxonomy_entry(target_role)

        if not entry:
            # Fallback for dynamic/unlisted roles: exact or clean word containment
            target_clean = target_role.lower().strip()
            if target_clean in title_lower:
                return {"match": True, "is_allowed": True, "is_strictly_excluded": False, "status": "DIRECT_MATCH", "reason": f"Title contains '{target_role}'"}
            # Check if all major words match
            words = [w for w in target_clean.split() if len(w) > 2]
            if words and all(w in title_lower for w in words):
                return {"match": True, "is_allowed": True, "is_strictly_excluded": False, "status": "ALLOWED_EQUIVALENT", "reason": f"Title matches words of '{target_role}'"}
            return {"match": False, "is_allowed": False, "is_strictly_excluded": False, "status": "UNMATCHED", "reason": f"Job does not match unlisted role '{target_role}'"}

        # 1. Hard Exclusion Check: If job title matches an excluded pattern, REJECT immediately!
        for exc in entry.get("excluded_patterns", []):
            if re.search(exc, title_lower, re.IGNORECASE):
                # Special safety check: if user specifically asked for "Software Architect", don't exclude "architect"
                target_lower = target_role.lower()
                if "architect" in target_lower and "architect" in exc and "software architect" in target_lower:
                    continue
                return {
                    "match": False,
                    "is_allowed": False,
                    "is_strictly_excluded": True,
                    "status": "STRICT_EXCLUSION",
                    "reason": f"Title '{job_title}' strictly excluded for target role '{target_role}' by pattern '{exc}'"
                }

        # 2. Check Allowed Patterns
        for pat in entry.get("allowed_patterns", []):
            if re.search(pat, title_lower, re.IGNORECASE):
                is_direct = (entry["canonical"].lower() in title_lower)
                return {
                    "match": True,
                    "is_allowed": True,
                    "is_strictly_excluded": False,
                    "status": "DIRECT_MATCH" if is_direct else "ALLOWED_EQUIVALENT",
                    "reason": f"Title '{job_title}' aligns with '{target_role}' via pattern '{pat}'"
                }

        # 3. Soft title word overlap check (if 70%+ of tokens overlap and no exclusion triggered)
        target_tokens = set(re.findall(r"\b[a-zA-Z]{3,}\b", target_role.lower()))
        title_tokens = set(re.findall(r"\b[a-zA-Z]{3,}\b", title_lower))
        if target_tokens and target_tokens.issubset(title_tokens):
            return {
                "match": True,
                "is_allowed": True,
                "is_strictly_excluded": False,
                "status": "ALLOWED_EQUIVALENT",
                "reason": f"Title '{job_title}' encompasses all keywords of target role '{target_role}'"
            }

        return {
            "match": False,
            "is_allowed": False,
            "is_strictly_excluded": False,
            "status": "UNMATCHED",
            "reason": f"Title '{job_title}' does not match requirements for '{target_role}'"
        }
