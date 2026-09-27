import logging
from app.ai.embedding_service import embedding_service

logger = logging.getLogger(__name__)

class SemanticMatcher:
    """
    Semantic Matcher component using Sentence Transformers to compute:
    1. Overall resume text to job description semantic cosine similarity score (0 - 100%).
    2. Fine-grained skill categorization: EXACT_MATCH, NORMALIZED_MATCH, SEMANTIC_MATCH (>=0.70), MISSING_SKILL.
    """
    
    # Common normalized aliases mapping
    SKILL_ALIASES = {
        'js': 'javascript',
        'ts': 'typescript',
        'py': 'python',
        'react.js': 'react',
        'reactjs': 'react',
        'vue.js': 'vue',
        'vuejs': 'vue',
        'node.js': 'node',
        'nodejs': 'node',
        'express.js': 'express',
        'expressjs': 'express',
        'mongo': 'mongodb',
        'postgres': 'postgresql',
        'docker.io': 'docker',
        'k8s': 'kubernetes',
        'aws': 'amazon web services',
        'gcp': 'google cloud platform',
        'ml': 'machine learning',
        'dl': 'deep learning',
        'nlp': 'natural language processing',
        'ai': 'artificial intelligence'
    }

    def _normalize_skill(self, skill: str) -> str:
        s = skill.lower().strip()
        return self.SKILL_ALIASES.get(s, s)

    def categorize_skills(self, candidate_skills: list, job_skills: list) -> list:
        """
        Categorize job required skills against candidate skills into:
        - EXACT_MATCH
        - NORMALIZED_MATCH
        - SEMANTIC_MATCH (cos sim >= 0.70)
        - MISSING_SKILL
        """
        results = []
        cand_lower = [s.lower().strip() for s in candidate_skills]
        cand_norm = [self._normalize_skill(s) for s in candidate_skills]

        for req_skill in job_skills:
            req_raw = req_skill.strip()
            req_l = req_raw.lower()
            req_n = self._normalize_skill(req_raw)

            # 1. Exact Match
            if req_l in cand_lower:
                results.append({
                    "skill": req_raw,
                    "match_type": "EXACT_MATCH",
                    "matched_with": req_raw,
                    "similarity": 1.0,
                    "status": "matched"
                })
                continue

            # 2. Normalized Match
            if req_n in cand_norm:
                idx = cand_norm.index(req_n)
                matched_cand = candidate_skills[idx]
                results.append({
                    "skill": req_raw,
                    "match_type": "NORMALIZED_MATCH",
                    "matched_with": matched_cand,
                    "similarity": 0.95,
                    "status": "matched"
                })
                continue

            # 3. Semantic Match (if AI available)
            matched_sematically = False
            if embedding_service.is_available():
                req_emb = embedding_service.get_embedding(req_raw)
                best_sim = 0.0
                best_cand = None

                if req_emb is not None:
                    for cand in candidate_skills:
                        cand_emb = embedding_service.get_embedding(cand)
                        sim = embedding_service.cosine_similarity(req_emb, cand_emb)
                        if sim > best_sim:
                            best_sim = sim
                            best_cand = cand

                if best_sim >= 0.70 and best_cand:
                    results.append({
                        "skill": req_raw,
                        "match_type": "SEMANTIC_MATCH",
                        "matched_with": best_cand,
                        "similarity": round(best_sim, 3),
                        "status": "matched"
                    })
                    matched_sematically = True
                    continue

            # 4. Missing Skill
            if not matched_sematically:
                results.append({
                    "skill": req_raw,
                    "match_type": "MISSING_SKILL",
                    "matched_with": None,
                    "similarity": 0.0,
                    "status": "missing"
                })

        return results

    def compute_semantic_match(self, resume_text: str, job_description: str, candidate_skills: list, job_skills: list) -> dict:
        """
        Compute overall semantic similarity score and detailed skill categorization.
        """
        if not embedding_service.is_available():
            return {
                "ai_available": False,
                "ai_semantic_score": 0.0,
                "skill_categorization": self.categorize_skills(candidate_skills, job_skills),
                "explanation": "AI embedding service is currently offline or disabled. Falling back to deterministic analysis."
            }

        # Compute full text cosine similarity
        text_sim_score = embedding_service.compute_text_similarity(resume_text or "", job_description or "")
        skill_cats = self.categorize_skills(candidate_skills or [], job_skills or [])

        matched_count = sum(1 for item in skill_cats if item["status"] == "matched")
        total_count = len(job_skills) if job_skills else 1
        skill_coverage_pct = round((matched_count / total_count) * 100.0, 1)

        # Generate readable explanation
        explanation = (
            f"AI Semantic Analysis completed using sentence-transformers/all-MiniLM-L6-v2. "
            f"Overall text similarity between resume and job description is {text_sim_score}%. "
            f"Skill coverage with semantic detection is {skill_coverage_pct}% ({matched_count}/{total_count} skills)."
        )

        return {
            "ai_available": True,
            "ai_semantic_score": text_sim_score,
            "skill_categorization": skill_cats,
            "skill_coverage_pct": skill_coverage_pct,
            "explanation": explanation
        }

semantic_matcher = SemanticMatcher()
