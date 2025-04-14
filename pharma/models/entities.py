"""
Entity models for the pharma CI platform.
Defines data structures for the various entities tracked by the platform.
"""

class DrugEntity:
    """
    Represents a drug or therapeutic compound.
    """
    def __init__(self, name, company=None, phase=None, condition=None):
        self.name = name
        self.company = company
        self.phase = phase
        self.condition = condition
        self.last_updated = None
        self.clinical_trials = []
        self.publications = []
        self.approvals = []
    
    def to_dict(self):
        """Convert entity to dictionary representation"""
        return {
            "name": self.name,
            "company": self.company,
            "phase": self.phase,
            "condition": self.condition,
            "last_updated": self.last_updated,
            "trial_count": len(self.clinical_trials),
            "publication_count": len(self.publications),
            "approval_count": len(self.approvals)
        }


class CompanyEntity:
    """
    Represents a pharmaceutical or biotech company.
    """
    def __init__(self, name):
        self.name = name
        self.drugs = []
        self.pipeline = {}  # Organized by phase
        self.news = []
        self.collaborations = []
    
    def to_dict(self):
        """Convert entity to dictionary representation"""
        return {
            "name": self.name,
            "drug_count": len(self.drugs),
            "pipeline": {phase: len(drugs) for phase, drugs in self.pipeline.items()},
            "news_count": len(self.news),
            "collaboration_count": len(self.collaborations)
        }


class KolEntity:
    """
    Represents a Key Opinion Leader in the pharmaceutical industry.
    """
    def __init__(self, name):
        self.name = name
        self.publications = []
        self.affiliations = []
        self.therapeutic_areas = []
        self.mentions = []
    
    def to_dict(self):
        """Convert entity to dictionary representation"""
        return {
            "name": self.name,
            "publication_count": len(self.publications),
            "affiliation_count": len(self.affiliations),
            "therapeutic_areas": self.therapeutic_areas,
            "mention_count": len(self.mentions)
        }
