"""
Database module for the pharma CI platform.
Handles database connections and operations.
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Text, Float, DateTime, ForeignKey, Boolean, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime

# Load environment variables from .env file
load_dotenv()

# Get the database URL from environment variable
DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    # Fallback to local development database URL
    DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/pharma_intel"

# Create the SQLAlchemy engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800
)

# Create a base class for declarative models
Base = declarative_base()

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define database models
class Company(Base):
    """Company model for pharmaceutical companies"""
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    website = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    drugs = relationship("Drug", back_populates="company")
    
    def __repr__(self):
        return f"<Company(name='{self.name}')>"

class Drug(Base):
    """Drug model for pharmaceutical products"""
    __tablename__ = "drugs"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    phase = Column(String, index=True)  # Preclinical, Phase 1, Phase 2, Phase 3, Approved, etc.
    condition = Column(String, index=True)
    therapeutic_area = Column(String, index=True)
    status = Column(String)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow)
    description = Column(Text, nullable=True)
    url = Column(String, nullable=True)
    
    # Relationships
    company = relationship("Company", back_populates="drugs")
    
    def __repr__(self):
        return f"<Drug(name='{self.name}', phase='{self.phase}')>"

class NewsArticle(Base):
    """News article model for pharmaceutical news"""
    __tablename__ = "news_articles"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    source = Column(String, index=True)
    url = Column(String, unique=True)
    published_at = Column(DateTime, index=True)
    summary = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    sentiment = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f"<NewsArticle(title='{self.title}')>"

class KOL(Base):
    """Key Opinion Leader model for industry experts"""
    __tablename__ = "kols"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    publication_count = Column(Integer, default=0)
    journals = Column(Text, nullable=True)  # Stored as JSON string
    recent_publication = Column(Text, nullable=True)
    url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f"<KOL(name='{self.name}')>"

class Publication(Base):
    """Scientific publication model"""
    __tablename__ = "publications"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    abstract = Column(Text, nullable=True)
    authors = Column(Text, nullable=True)  # Stored as JSON string
    journal = Column(String, nullable=True)
    pub_date = Column(DateTime, nullable=True)
    url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f"<Publication(title='{self.title}')>"

# Database initialization function
def init_db():
    """Initialize the database with all required tables"""
    try:
        # Check if tables already exist
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        # Only create tables that don't exist
        if not existing_tables:
            Base.metadata.create_all(bind=engine)
            print("Database tables created successfully")
        else:
            print("Database tables already exist")
            
    except Exception as e:
        print(f"Error initializing database: {e}")
        # Don't raise the error, just log it
        pass

# Get a database session
def get_db():
    """Get a database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Seed function to add initial data
def seed_companies():
    """Add initial company data to the database"""
    db = SessionLocal()
    try:
        # Check if companies already exist
        if db.query(Company).count() > 0:
            return
        
        # List of major pharmaceutical companies
        companies = [
            {"name": "Pfizer", "website": "https://www.pfizer.com"},
            {"name": "Novartis", "website": "https://www.novartis.com"},
            {"name": "Roche", "website": "https://www.roche.com"},
            {"name": "Merck", "website": "https://www.merck.com"},
            {"name": "AstraZeneca", "website": "https://www.astrazeneca.com"},
            {"name": "Johnson & Johnson", "website": "https://www.jnj.com"},
            {"name": "Sanofi", "website": "https://www.sanofi.com"},
            {"name": "GlaxoSmithKline", "website": "https://www.gsk.com"},
            {"name": "Gilead", "website": "https://www.gilead.com"},
            {"name": "Bristol Myers Squibb", "website": "https://www.bms.com"},
            {"name": "Amgen", "website": "https://www.amgen.com"},
            {"name": "AbbVie", "website": "https://www.abbvie.com"},
            {"name": "Eli Lilly", "website": "https://www.lilly.com"}
        ]
        
        # Add companies to the database
        for company_data in companies:
            company = Company(**company_data)
            db.add(company)
        
        db.commit()
    finally:
        db.close()

def seed_sample_drugs():
    """Add initial drug data to the database"""
    db = SessionLocal()
    try:
        # Check if drugs already exist
        if db.query(Drug).count() > 0:
            return
        
        # List of sample drugs with company IDs
        # We'll need to get the company IDs from the database
        company_map = {company.name: company.id for company in db.query(Company).all()}
        
        # Create a comprehensive list of drugs covering all phases of development
        drugs = [
            # Approved drugs
            {
                "name": "Comirnaty",
                "company_id": company_map.get("Pfizer"),
                "phase": "Approved",
                "condition": "COVID-19",
                "therapeutic_area": "Infectious Disease",
                "status": "Marketed",
                "last_updated": datetime.datetime.utcnow(),
                "url": "https://www.pfizer.com/products/coronavirus/covid-19-vaccine"
            },
            {
                "name": "Keytruda",
                "company_id": company_map.get("Merck"),
                "phase": "Approved",
                "condition": "Multiple cancer types",
                "therapeutic_area": "Oncology",
                "status": "Marketed",
                "last_updated": datetime.datetime.utcnow(),
                "url": "https://www.keytruda.com/"
            },
            {
                "name": "Humira",
                "company_id": company_map.get("AbbVie"),
                "phase": "Approved",
                "condition": "Rheumatoid arthritis, Crohn's disease",
                "therapeutic_area": "Immunology",
                "status": "Marketed",
                "last_updated": datetime.datetime.utcnow(),
                "url": "https://www.humira.com/"
            },
            {
                "name": "Revlimid",
                "company_id": company_map.get("Bristol Myers Squibb"),
                "phase": "Approved",
                "condition": "Multiple myeloma",
                "therapeutic_area": "Oncology",
                "status": "Marketed",
                "last_updated": datetime.datetime.utcnow(),
                "url": "https://www.revlimid.com/"
            },
            
            # Phase 4 (post-approval) drugs
            {
                "name": "Eliquis",
                "company_id": company_map.get("Bristol Myers Squibb"),
                "phase": "Phase 4",
                "condition": "Atrial fibrillation, prevention of stroke",
                "therapeutic_area": "Cardiovascular",
                "status": "Post-marketing surveillance",
                "last_updated": datetime.datetime.utcnow(),
                "url": "https://www.eliquis.com/"
            },
            {
                "name": "Jardiance",
                "company_id": company_map.get("Eli Lilly"),
                "phase": "Phase 4",
                "condition": "Type 2 diabetes, heart failure",
                "therapeutic_area": "Metabolic",
                "status": "Post-approval study",
                "last_updated": datetime.datetime.utcnow(),
                "url": "https://www.jardiance.com/"
            },
            
            # Phase 3 drugs
            {
                "name": "PFE-3782",
                "company_id": company_map.get("Pfizer"),
                "phase": "Phase 3",
                "condition": "Advanced breast cancer",
                "therapeutic_area": "Oncology",
                "status": "Active, not recruiting",
                "last_updated": datetime.datetime.utcnow(),
                "url": "#"
            },
            {
                "name": "NVS-2190",
                "company_id": company_map.get("Novartis"),
                "phase": "Phase 3",
                "condition": "Severe asthma",
                "therapeutic_area": "Respiratory",
                "status": "Recruiting",
                "last_updated": datetime.datetime.utcnow(),
                "url": "#"
            },
            
            # Phase 2/3 drugs
            {
                "name": "GSK-5501",
                "company_id": company_map.get("GlaxoSmithKline"),
                "phase": "Phase 2/3",
                "condition": "Ulcerative colitis",
                "therapeutic_area": "Immunology",
                "status": "Recruiting",
                "last_updated": datetime.datetime.utcnow(),
                "url": "#"
            },
            
            # Phase 2 drugs
            {
                "name": "ABP-123",
                "company_id": company_map.get("Amgen"),
                "phase": "Phase 2",
                "condition": "Solid tumors",
                "therapeutic_area": "Oncology",
                "status": "Recruiting",
                "last_updated": datetime.datetime.utcnow(),
                "url": "#"
            },
            {
                "name": "ROG-4455",
                "company_id": company_map.get("Roche"),
                "phase": "Phase 2",
                "condition": "Multiple sclerosis",
                "therapeutic_area": "Neurology",
                "status": "Recruiting",
                "last_updated": datetime.datetime.utcnow(),
                "url": "#"
            },
            
            # Phase 1/2 drugs
            {
                "name": "AZN-7731",
                "company_id": company_map.get("AstraZeneca"),
                "phase": "Phase 1/2",
                "condition": "Advanced non-small cell lung cancer",
                "therapeutic_area": "Oncology",
                "status": "Recruiting",
                "last_updated": datetime.datetime.utcnow(),
                "url": "#"
            },
            
            # Phase 1 drugs
            {
                "name": "JNJ-9876",
                "company_id": company_map.get("Johnson & Johnson"),
                "phase": "Phase 1",
                "condition": "Rheumatoid arthritis",
                "therapeutic_area": "Immunology",
                "status": "Recruiting",
                "last_updated": datetime.datetime.utcnow(),
                "url": "#"
            },
            {
                "name": "SNF-6622",
                "company_id": company_map.get("Sanofi"),
                "phase": "Phase 1",
                "condition": "Atopic dermatitis",
                "therapeutic_area": "Immunology",
                "status": "Recruiting",
                "last_updated": datetime.datetime.utcnow(),
                "url": "#"
            },
            
            # Preclinical drugs
            {
                "name": "LLY-5432",
                "company_id": company_map.get("Eli Lilly"),
                "phase": "Preclinical",
                "condition": "Type 2 diabetes",
                "therapeutic_area": "Metabolic",
                "status": "IND-enabling studies",
                "last_updated": datetime.datetime.utcnow(),
                "url": "#"
            },
            {
                "name": "GILD-8910",
                "company_id": company_map.get("Gilead"),
                "phase": "Preclinical",
                "condition": "Hepatitis B",
                "therapeutic_area": "Infectious Disease",
                "status": "Lead optimization",
                "last_updated": datetime.datetime.utcnow(),
                "url": "#"
            }
        ]
        
        # Add drugs to the database
        for drug_data in drugs:
            if drug_data["company_id"]:  # Only add if company exists
                drug = Drug(**drug_data)
                db.add(drug)
        
        db.commit()
    finally:
        db.close()

def seed_sample_kols():
    """Add initial KOL data to the database"""
    db = SessionLocal()
    try:
        # Check if KOLs already exist
        if db.query(KOL).count() > 0:
            return
        
        # List of sample KOLs
        kols = [
            {
                "name": "Dr. Jane Smith",
                "publication_count": 45,
                "journals": "Nature Medicine, JAMA, The Lancet",
                "recent_publication": "Novel Therapy Approaches in Oncology",
                "url": "https://pubmed.ncbi.nlm.nih.gov/?term=smith+j"
            },
            {
                "name": "Dr. Robert Johnson",
                "publication_count": 67,
                "journals": "New England Journal of Medicine, Nature Reviews",
                "recent_publication": "Immunotherapy for Autoimmune Disorders",
                "url": "https://pubmed.ncbi.nlm.nih.gov/?term=johnson+r"
            },
            {
                "name": "Dr. Michael Chen",
                "publication_count": 32,
                "journals": "Cell, Science, Nature Biotechnology",
                "recent_publication": "CRISPR Applications in Rare Genetic Diseases",
                "url": "https://pubmed.ncbi.nlm.nih.gov/?term=chen+m"
            },
            {
                "name": "Dr. Sarah Williams",
                "publication_count": 28,
                "journals": "JAMA Neurology, Neuron",
                "recent_publication": "Advances in Alzheimer's Treatment",
                "url": "https://pubmed.ncbi.nlm.nih.gov/?term=williams+s"
            },
            {
                "name": "Dr. David Martinez",
                "publication_count": 52,
                "journals": "The Lancet, Science Translational Medicine",
                "recent_publication": "Novel Cardiovascular Drug Targets",
                "url": "https://pubmed.ncbi.nlm.nih.gov/?term=martinez+d"
            }
        ]
        
        # Add KOLs to the database
        for kol_data in kols:
            kol = KOL(**kol_data)
            db.add(kol)
        
        db.commit()
    finally:
        db.close()

def seed_sample_publications():
    """Add initial publication data to the database"""
    db = SessionLocal()
    try:
        # Check if publications already exist
        if db.query(Publication).count() > 0:
            return
        
        # List of sample publications
        publications = [
            {
                "title": "Novel Therapy Approaches in Oncology",
                "abstract": "This review covers emerging therapeutic approaches in oncology with a focus on targeted therapies.",
                "authors": "Smith J, Johnson R, Chen M",
                "journal": "Nature Medicine",
                "pub_date": datetime.datetime.utcnow() - datetime.timedelta(days=30),
                "url": "https://pubmed.ncbi.nlm.nih.gov/"
            },
            {
                "title": "Immunotherapy for Autoimmune Disorders",
                "abstract": "An investigation of new immunotherapeutic approaches for treating autoimmune conditions.",
                "authors": "Johnson R, Williams S",
                "journal": "New England Journal of Medicine",
                "pub_date": datetime.datetime.utcnow() - datetime.timedelta(days=45),
                "url": "https://pubmed.ncbi.nlm.nih.gov/"
            },
            {
                "title": "CRISPR Applications in Rare Genetic Diseases",
                "abstract": "Review of gene editing technologies and their applications in treating rare genetic conditions.",
                "authors": "Chen M, Martinez D",
                "journal": "Cell",
                "pub_date": datetime.datetime.utcnow() - datetime.timedelta(days=60),
                "url": "https://pubmed.ncbi.nlm.nih.gov/"
            },
            {
                "title": "Advances in Alzheimer's Treatment",
                "abstract": "Recent advances in developing effective treatments for Alzheimer's disease.",
                "authors": "Williams S, Smith J",
                "journal": "JAMA Neurology",
                "pub_date": datetime.datetime.utcnow() - datetime.timedelta(days=90),
                "url": "https://pubmed.ncbi.nlm.nih.gov/"
            },
            {
                "title": "Novel Cardiovascular Drug Targets",
                "abstract": "Investigation of new molecular targets for cardiovascular drug development.",
                "authors": "Martinez D, Johnson R",
                "journal": "The Lancet",
                "pub_date": datetime.datetime.utcnow() - datetime.timedelta(days=120),
                "url": "https://pubmed.ncbi.nlm.nih.gov/"
            }
        ]
        
        # Add publications to the database
        for pub_data in publications:
            publication = Publication(**pub_data)
            db.add(publication)
        
        db.commit()
    finally:
        db.close()

# Seed the database
def seed_database():
    """Seed the database with initial data"""
    seed_companies()
    seed_sample_drugs()
    seed_sample_kols()
    seed_sample_publications()