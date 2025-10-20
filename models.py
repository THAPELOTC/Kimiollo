from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# This will be imported and initialized by app.py
db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with business proposals
    proposals = db.relationship('BusinessProposal', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class BusinessProposal(db.Model):
    __tablename__ = 'business_proposals'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    proposal_type = db.Column(db.String(50), nullable=False)  # 'generated' or 'uploaded'
    file_path = db.Column(db.String(500), nullable=True)
    analysis_score = db.Column(db.Float, nullable=True)  # 0-100 score
    feedback = db.Column(db.Text, nullable=True)  # JSON feedback data
    status = db.Column(db.String(50), default='draft')  # draft, processing, analyzed, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<BusinessProposal {self.title}>'
    
    def to_dict(self):
        import json
        feedback_dict = None
        if self.feedback:
            try:
                feedback_dict = json.loads(self.feedback)
            except:
                feedback_dict = self.feedback
        
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'content': self.content,
            'type': self.proposal_type,
            'file_path': self.file_path,
            'analysis_score': self.analysis_score,
            'feedback': feedback_dict,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class FundingSource(db.Model):
    __tablename__ = 'funding_sources'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    amount_range = db.Column(db.String(100), nullable=False)
    eligibility_criteria = db.Column(db.Text, nullable=True)  # JSON array
    application_deadline = db.Column(db.DateTime, nullable=True)
    industry_focus = db.Column(db.Text, nullable=True)  # JSON array
    contact_website = db.Column(db.String(500), nullable=True)
    contact_email = db.Column(db.String(120), nullable=True)
    requirements = db.Column(db.Text, nullable=True)  # JSON array
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<FundingSource {self.name}>'
    
    def to_dict(self):
        import json
        eligibility_list = []
        industry_list = []
        requirements_list = []
        
        if self.eligibility_criteria:
            try:
                eligibility_list = json.loads(self.eligibility_criteria)
            except:
                eligibility_list = [self.eligibility_criteria]
        
        if self.industry_focus:
            try:
                industry_list = json.loads(self.industry_focus)
            except:
                industry_list = [self.industry_focus]
        
        if self.requirements:
            try:
                requirements_list = json.loads(self.requirements)
            except:
                requirements_list = [self.requirements]
        
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'amount_range': self.amount_range,
            'eligibility_criteria': eligibility_list,
            'application_deadline': self.application_deadline.isoformat() if self.application_deadline else None,
            'industry_focus': industry_list,
            'contact_website': self.contact_website,
            'contact_email': self.contact_email,
            'requirements': requirements_list,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class FundingMatch(db.Model):
    __tablename__ = 'funding_matches'
    
    id = db.Column(db.Integer, primary_key=True)
    proposal_id = db.Column(db.Integer, db.ForeignKey('business_proposals.id'), nullable=False)
    funding_source_id = db.Column(db.Integer, db.ForeignKey('funding_sources.id'), nullable=False)
    match_score = db.Column(db.Float, nullable=False)  # 0-100 match score
    eligibility_status = db.Column(db.String(50), nullable=False)  # 'eligible', 'partially_eligible', 'not_eligible'
    rationale = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    proposal = db.relationship('BusinessProposal', backref='funding_matches')
    funding_source = db.relationship('FundingSource', backref='matches')
    
    def __repr__(self):
        return f'<FundingMatch {self.proposal_id} -> {self.funding_source_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'proposal_id': self.proposal_id,
            'funding_source': self.funding_source.to_dict() if self.funding_source else None,
            'match_score': self.match_score,
            'eligibility_status': self.eligibility_status,
            'rationale': self.rationale,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
