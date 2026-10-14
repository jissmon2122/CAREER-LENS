import logging
import re

logger = logging.getLogger(__name__)

class RoleTaxonomy:
    """
    Centralized Universal Role Taxonomy and Exclusion Dictionary.
    Maps canonical roles across all major professions (Skilled Trades, Healthcare,
    Education, Accounting/Finance, Hospitality, Logistics, Construction, Sales/Retail,
    Administration, Engineering, and IT) to equivalent title patterns and strict negative patterns.
    """

    ROLE_TAXONOMY = {
        # --- SKILLED TRADES ---
        "Electrician": {
            "canonical": "Electrician",
            "domain": "SKILLED_TRADES_ELECTRICAL",
            "allowed_patterns": [
                r"\belectrician\b",
                r"\belectrical\s+maintenance\s+technician\b",
                r"\belectrical\s+technician\b",
                r"\bjourneyman\s+electrician\b",
                r"\bmaster\s+electrician\b",
                r"\bapprentice\s+electrician\b",
                r"\bcommercial\s+electrician\b",
                r"\bindustrial\s+electrician\b",
                r"\bresidential\s+electrician\b",
                r"\belectrical\s+helper\b",
                r"\bmaintenance\s+electrician\b",
                r"\bwireman\b",
                r"\blineman\b",
                r"\belectrical\s+specialist\b"
            ],
            "excluded_patterns": [
                r"\bsoftware\b",
                r"\bdeveloper\b",
                r"\bdata\s+analyst\b",
                r"\baccountant\b",
                r"\bnurse\b",
                r"\bprogrammer\b",
                r"\barchitect\b",
                r"\bweb\b"
            ]
        },
        "Plumber": {
            "canonical": "Plumber",
            "domain": "SKILLED_TRADES_PLUMBING",
            "allowed_patterns": [
                r"\bplumber\b",
                r"\bpipefitter\b",
                r"\bplumbing\s+technician\b",
                r"\bjourneyman\s+plumber\b",
                r"\bmaster\s+plumber\b",
                r"\bapprentice\s+plumber\b",
                r"\bmaintenance\s+plumber\b",
                r"\bsteamfitter\b"
            ],
            "excluded_patterns": [
                r"\bsoftware\b",
                r"\bdeveloper\b",
                r"\belectrician\b",
                r"\baccountant\b"
            ]
        },
        "Welder": {
            "canonical": "Welder",
            "domain": "SKILLED_TRADES_WELDING",
            "allowed_patterns": [
                r"\bwelder\b",
                r"\bmetal\s+fabricator\b",
                r"\bmig\s+welder\b",
                r"\btig\s+welder\b",
                r"\bpipe\s+welder\b",
                r"\bstructural\s+welder\b",
                r"\barc\s+welder\b",
                r"\bfabricator\b"
            ],
            "excluded_patterns": [
                r"\bsoftware\b",
                r"\bdeveloper\b",
                r"\baccountant\b"
            ]
        },
        "Automotive Technician": {
            "canonical": "Automotive Technician",
            "domain": "SKILLED_TRADES_MECHANIC",
            "allowed_patterns": [
                r"\bautomotive\s+technician\b",
                r"\bauto\s+mechanic\b",
                r"\bmechanic\b",
                r"\bmaintenance\s+mechanic\b",
                r"\bdiesel\s+mechanic\b",
                r"\bservice\s+technician\b",
                r"\bvehicle\s+technician\b"
            ],
            "excluded_patterns": [
                r"\bsoftware\b",
                r"\bdeveloper\b",
                r"\baccountant\b"
            ]
        },
        "HVAC Technician": {
            "canonical": "HVAC Technician",
            "domain": "SKILLED_TRADES_HVAC",
            "allowed_patterns": [
                r"\bhvac\s+technician\b",
                r"\brefrigeration\s+technician\b",
                r"\bhvac\s+service\s+technician\b",
                r"\bhvac\s+installer\b",
                r"\bhvac\s+mechanic\b",
                r"\bair\s+conditioning\s+technician\b"
            ],
            "excluded_patterns": [
                r"\bsoftware\b",
                r"\bdeveloper\b",
                r"\baccountant\b"
            ]
        },

        # --- HEALTHCARE ---
        "Staff Nurse": {
            "canonical": "Staff Nurse",
            "domain": "HEALTHCARE",
            "allowed_patterns": [
                r"\bstaff\s+nurse\b",
                r"\bregistered\s+nurse\b",
                r"\bclinical\s+nurse\b",
                r"\bhospital\s+nurse\b",
                r"\bnurse\b",
                r"\brn\b",
                r"\bcharge\s+nurse\b",
                r"\bicu\s+nurse\b",
                r"\bpediatric\s+nurse\b"
            ],
            "excluded_patterns": [
                r"\bsoftware\b",
                r"\bdeveloper\b",
                r"\baccountant\b",
                r"\belectrician\b"
            ]
        },
        "Caregiver": {
            "canonical": "Caregiver",
            "domain": "HEALTHCARE_SUPPORT",
            "allowed_patterns": [
                r"\bcaregiver\b",
                r"\bmedical\s+assistant\b",
                r"\bcertified\s+nursing\s+assistant\b",
                r"\bcna\b",
                r"\bhome\s+health\s+aide\b",
                r"\bpatient\s+care\s+assistant\b",
                r"\bphlebotomist\b",
                r"\bmedical\s+lab\s+technician\b"
            ],
            "excluded_patterns": [
                r"\bsoftware\b",
                r"\bdeveloper\b",
                r"\belectrician\b"
            ]
        },

        # --- EDUCATION ---
        "School Teacher": {
            "canonical": "School Teacher",
            "domain": "EDUCATION",
            "allowed_patterns": [
                r"\bschool\s+teacher\b",
                r"\bteacher\b",
                r"\bsubject\s+teacher\b",
                r"\btutor\b",
                r"\beducator\b",
                r"\binstructor\b",
                r"\bhigh\s+school\s+teacher\b",
                r"\bprimary\s+teacher\b",
                r"\blecturer\b"
            ],
            "excluded_patterns": [
                r"\bsoftware\s+developer\b",
                r"\belectrician\b",
                r"\baccountant\b"
            ]
        },

        # --- ACCOUNTING & FINANCE ---
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
                r"\bfinancial\s+analyst\b"
            ],
            "excluded_patterns": [
                r"\bsoftware\b",
                r"\bdeveloper\b",
                r"\belectrician\b",
                r"\bnurse\b"
            ]
        },

        # --- ADMINISTRATION & OFFICE ---
        "Administrative Assistant": {
            "canonical": "Administrative Assistant",
            "domain": "ADMINISTRATION_OFFICE",
            "allowed_patterns": [
                r"\badministrative\s+assistant\b",
                r"\boffice\s+administrator\b",
                r"\bexecutive\s+assistant\b",
                r"\breceptionist\b",
                r"\boffice\s+assistant\b",
                r"\boffice\s+coordinator\b",
                r"\bdata\s+entry\s+specialist\b",
                r"\bclerk\b"
            ],
            "excluded_patterns": [
                r"\bsoftware\s+engineer\b",
                r"\belectrician\b"
            ]
        },

        # --- HOSPITALITY & CULINARY ---
        "Chef": {
            "canonical": "Chef",
            "domain": "HOSPITALITY_CULINARY",
            "allowed_patterns": [
                r"\bchef\b",
                r"\bline\s+cook\b",
                r"\bcook\b",
                r"\bsous\s+chef\b",
                r"\bhead\s+chef\b",
                r"\bkitchen\s+manager\b",
                r"\bfood\s+service\s+worker\b",
                r"\bbartender\b"
            ],
            "excluded_patterns": [
                r"\bsoftware\b",
                r"\bdeveloper\b",
                r"\belectrician\b"
            ]
        },

        # --- LOGISTICS & WAREHOUSE ---
        "Forklift Operator": {
            "canonical": "Forklift Operator",
            "domain": "LOGISTICS_WAREHOUSE",
            "allowed_patterns": [
                r"\bforklift\s+operator\b",
                r"\bforklift\s+driver\b",
                r"\bwarehouse\s+associate\b",
                r"\border\s+picker\b",
                r"\bmaterial\s+handler\b",
                r"\bwarehouse\s+worker\b",
                r"\bshipping\s+and\s+receiving\b",
                r"\bdelivery\s+driver\b",
                r"\btruck\s+driver\b"
            ],
            "excluded_patterns": [
                r"\bsoftware\b",
                r"\bdeveloper\b",
                r"\baccountant\b"
            ]
        },

        # --- CONSTRUCTION & CARPENTRY ---
        "Carpenter": {
            "canonical": "Carpenter",
            "domain": "CONSTRUCTION_CARPENTRY",
            "allowed_patterns": [
                r"\bcarpenter\b",
                r"\bconstruction\s+worker\b",
                r"\bdrywall\s+installer\b",
                r"\bmason\b",
                r"\broofer\b",
                r"\bconstruction\s+laborer\b",
                r"\bforeman\b"
            ],
            "excluded_patterns": [
                r"\bsoftware\b",
                r"\bdeveloper\b"
            ]
        },

        # --- SALES & RETAIL ---
        "Sales Executive": {
            "canonical": "Sales Executive",
            "domain": "SALES_RETAIL",
            "allowed_patterns": [
                r"\bsales\s+executive\b",
                r"\bretail\s+associate\b",
                r"\bcashier\b",
                r"\bcustomer\s+service\s+representative\b",
                r"\bstore\s+associate\b",
                r"\bsales\s+representative\b",
                r"\baccount\s+executive\b"
            ],
            "excluded_patterns": [
                r"\bsoftware\s+developer\b",
                r"\belectrician\b"
            ]
        },

        # --- ENGINEERING ---
        "Mechanical Engineer": {
            "canonical": "Mechanical Engineer",
            "domain": "MECHANICAL_ENGINEERING",
            "allowed_patterns": [
                r"\bmechanical\s+engineer\b",
                r"\bdesign\s+engineer\b",
                r"\bcad\s+engineer\b",
                r"\bproduction\s+engineer\b",
                r"\bmanufacturing\s+engineer\b"
            ],
            "excluded_patterns": [
                r"\bsoftware\s+developer\b",
                r"\baccountant\b",
                r"\bnurse\b"
            ]
        },
        "Civil Engineer": {
            "canonical": "Civil Engineer",
            "domain": "CIVIL_ENGINEERING",
            "allowed_patterns": [
                r"\bcivil\s+engineer\b",
                r"\bsite\s+engineer\b",
                r"\bstructural\s+engineer\b",
                r"\bquantity\s+surveyor\b",
                r"\bconstruction\s+engineer\b"
            ],
            "excluded_patterns": [
                r"\bsoftware\s+developer\b",
                r"\baccountant\b"
            ]
        },
        "Electrical Engineer": {
            "canonical": "Electrical Engineer",
            "domain": "ELECTRICAL_ENGINEERING",
            "allowed_patterns": [
                r"\belectrical\s+engineer\b",
                r"\belectrical\s+design\s+engineer\b",
                r"\bpower\s+engineer\b",
                r"\bcontrol\s+systems\s+engineer\b"
            ],
            "excluded_patterns": [
                r"\bsoftware\s+developer\b",
                r"\baccountant\b"
            ]
        },

        # --- SOFTWARE & IT ---
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
                r"\bassociate\s+software\s+engineer\b",
                r"\bbackend\s+developer\b",
                r"\bback[- ]end\s+developer\b",
                r"\bbackend\s+engineer\b",
                r"\bfrontend\s+developer\b",
                r"\bfront[- ]end\s+developer\b",
                r"\bfull[- ]?stack\s+developer\b",
                r"\bfull[- ]?stack\s+engineer\b",
                r"\bweb\s+developer\b",
                r"\bpython\s+developer\b",
                r"\bjava\s+developer\b"
            ],
            "excluded_patterns": [
                r"\belectrician\b",
                r"\bplumber\b",
                r"\bwelder\b",
                r"\bmechanic\b",
                r"\bnurse\b",
                r"\baccountant\b",
                r"\barchitect\b"
            ]
        },
        "Data Analyst": {
            "canonical": "Data Analyst",
            "domain": "DATA_ANALYTICS",
            "allowed_patterns": [
                r"\bdata\s+analyst\b",
                r"\bjunior\s+data\s+analyst\b",
                r"\bbusiness\s+data\s+analyst\b",
                r"\breporting\s+analyst\b",
                r"\bbi\s+analyst\b",
                r"\bbusiness\s+intelligence\s+analyst\b",
                r"\banalytics\s+specialist\b"
            ],
            "excluded_patterns": [
                r"\belectrician\b",
                r"\baccountant\b",
                r"\bnurse\b"
            ]
        },
        "Machine Learning Engineer": {
            "canonical": "Machine Learning Engineer",
            "domain": "DATA_SCIENCE_AI",
            "allowed_patterns": [
                r"\bmachine\s+learning\s+engineer\b",
                r"\bml\s+engineer\b",
                r"\bai\s+engineer\b",
                r"\bdata\s+scientist\b"
            ],
            "excluded_patterns": [
                r"\belectrician\b",
                r"\baccountant\b"
            ]
        },
        "DevOps Engineer": {
            "canonical": "DevOps Engineer",
            "domain": "CLOUD_DEVOPS",
            "allowed_patterns": [
                r"\bdevops\s+engineer\b",
                r"\bcloud\s+devops\s+engineer\b",
                r"\bsite\s+reliability\s+engineer\b",
                r"\bsre\b"
            ],
            "excluded_patterns": [
                r"\belectrician\b",
                r"\baccountant\b"
            ]
        }
    }

    # Cross-domain exclusion mapping to prevent misaligned roles showing up
    CROSS_DOMAIN_EXCLUSIONS = {
        "SKILLED_TRADES_ELECTRICAL": ["SOFTWARE_ENGINEERING", "DATA_ANALYTICS", "DATA_SCIENCE_AI", "ACCOUNTING_FINANCE", "HEALTHCARE"],
        "SKILLED_TRADES_PLUMBING": ["SOFTWARE_ENGINEERING", "DATA_ANALYTICS", "DATA_SCIENCE_AI", "ACCOUNTING_FINANCE", "HEALTHCARE"],
        "SKILLED_TRADES_WELDING": ["SOFTWARE_ENGINEERING", "DATA_ANALYTICS", "DATA_SCIENCE_AI", "ACCOUNTING_FINANCE", "HEALTHCARE"],
        "SKILLED_TRADES_MECHANIC": ["SOFTWARE_ENGINEERING", "DATA_ANALYTICS", "DATA_SCIENCE_AI", "ACCOUNTING_FINANCE", "HEALTHCARE"],
        "SKILLED_TRADES_HVAC": ["SOFTWARE_ENGINEERING", "DATA_ANALYTICS", "DATA_SCIENCE_AI", "ACCOUNTING_FINANCE", "HEALTHCARE"],
        "HEALTHCARE": ["SOFTWARE_ENGINEERING", "DATA_ANALYTICS", "SKILLED_TRADES_ELECTRICAL", "ACCOUNTING_FINANCE"],
        "EDUCATION": ["SOFTWARE_ENGINEERING", "SKILLED_TRADES_ELECTRICAL", "ACCOUNTING_FINANCE"],
        "ACCOUNTING_FINANCE": ["SOFTWARE_ENGINEERING", "DATA_SCIENCE_AI", "SKILLED_TRADES_ELECTRICAL", "HEALTHCARE"],
        "SOFTWARE_ENGINEERING": ["SKILLED_TRADES_ELECTRICAL", "SKILLED_TRADES_PLUMBING", "ACCOUNTING_FINANCE", "HEALTHCARE", "CIVIL_ENGINEERING"],
        "DATA_ANALYTICS": ["SKILLED_TRADES_ELECTRICAL", "ACCOUNTING_FINANCE", "HEALTHCARE", "CIVIL_ENGINEERING"]
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
        Evaluate if a job_title is a legitimate match for target_role across all professions.
        Returns:
          {
            "match": bool,
            "is_allowed": bool,
            "is_strictly_excluded": bool,
            "status": "DIRECT_MATCH" | "ALLOWED_EQUIVALENT" | "STRICT_EXCLUSION" | "UNMATCHED",
            "reason": str
          }
        """
        if not target_role or not job_title:
            return {
                "match": False,
                "is_allowed": False,
                "is_strictly_excluded": False,
                "status": "UNMATCHED",
                "reason": "Missing role or title"
            }

        title_lower = job_title.strip().lower()
        entry = cls.find_taxonomy_entry(target_role)

        if not entry:
            # Fallback for dynamic/unlisted roles: exact or clean word containment
            target_clean = target_role.lower().strip()
            if target_clean in title_lower:
                return {
                    "match": True,
                    "is_allowed": True,
                    "is_strictly_excluded": False,
                    "status": "DIRECT_MATCH",
                    "reason": f"Title contains '{target_role}'"
                }
            # Check if all major words match
            words = [w for w in target_clean.split() if len(w) > 2]
            if words and all(w in title_lower for w in words):
                return {
                    "match": True,
                    "is_allowed": True,
                    "is_strictly_excluded": False,
                    "status": "ALLOWED_EQUIVALENT",
                    "reason": f"Title matches words of '{target_role}'"
                }
            return {
                "match": False,
                "is_allowed": False,
                "is_strictly_excluded": False,
                "status": "UNMATCHED",
                "reason": f"Job does not match unlisted role '{target_role}'"
            }

        # 1. Hard Exclusion Check: If job title matches an excluded pattern, REJECT immediately!
        for exc in entry.get("excluded_patterns", []):
            if re.search(exc, title_lower, re.IGNORECASE):
                target_lower = target_role.lower()
                # Safety check: if target role itself contains the keyword, don't self-exclude
                if any(w in target_lower for w in re.findall(r'\b[a-z]{3,}\b', exc)):
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

        # 3. Soft title word overlap check (if target tokens are present in title)
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
