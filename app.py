from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta
import json
import requests
import re

# Initialize Flask app
app = Flask(__name__)

# Production environment configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///business_proposal.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'business-proposal-generator-jwt-secret-key-2025')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Production settings
if os.environ.get('FLASK_ENV') == 'production':
    app.config['DEBUG'] = False
else:
    app.config['DEBUG'] = True

# Import SQLAlchemy and create db instance
from models import db

jwt = JWTManager(app)
bcrypt = Bcrypt(app)

# CORS configuration for production
def is_allowed_origin(origin):
    if not origin:
        return False
    
    allowed_origins = [
        'http://localhost:3000',
        'http://127.0.0.1:3000',
        'https://thapelotc.github.io'
    ]
    
    # Check exact matches first
    if origin in allowed_origins:
        return True
    
    # Patterns for local development and tunneling
    allowed_patterns = [
        r'^http://192\.168\.\d+\.\d+:3000$',
        r'^https://[a-zA-Z0-9-]+\.ngrok\.io$',
        r'^https://[a-zA-Z0-9-]+\.ngrok-free\.app$',
        r'^http://[a-zA-Z0-9-]+\.ngrok\.io$',
        r'^http://[a-zA-Z0-9-]+\.ngrok-free\.app$'
    ]
    
    return any(re.match(pattern, origin) for pattern in allowed_patterns)

# Use dynamic CORS for production, allow all for development
if os.environ.get('FLASK_ENV') == 'production':
    CORS(app, origins=is_allowed_origin, supports_credentials=True)
else:
    CORS(app, origins="*", supports_credentials=True)

# JWT error handlers
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({'message': 'Token has expired', 'error': 'token_expired'}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    print(f"Invalid token error: {error}")
    return jsonify({'message': 'Signature verification failed', 'error': 'invalid_token'}), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    print(f"Missing token error: {error}")
    return jsonify({'message': 'Request does not contain an access token', 'error': 'authorization_required'}), 401

# Initialize db with app
db.init_app(app)

# Import models after db initialization
from models import User, BusinessProposal, FundingSource, FundingMatch

# Import services
from services import AIBusinessPlanGenerator, DocumentProcessor, FundingMatcher

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Routes
@app.route('/api/register', methods=['POST'])
def register():
    try:
        print("Registration request received")
        data = request.get_json()
        print(f"Request data: {data}")
        
        email = data.get('email') if data else None
        password = data.get('password') if data else None
        name = data.get('name') if data else None
        
        print(f"Extracted fields - Email: {email}, Name: {name}, Password: {'***' if password else 'None'}")
        
        if not email or not password or not name:
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'error': 'User already exists'}), 400
        
        # Create new user
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(email=email, password=hashed_password, name=name)
        
        db.session.add(user)
        db.session.commit()
        
        # Create access token
        access_token = create_access_token(identity=str(user.id))
        
        return jsonify({
            'message': 'User created successfully',
            'access_token': access_token,
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.name
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Registration error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        user = User.query.filter_by(email=email).first()
        
        if user and bcrypt.check_password_hash(user.password, password):
            access_token = create_access_token(identity=str(user.id))
            return jsonify({
                'message': 'Login successful',
                'access_token': access_token,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'name': user.name
                }
            }), 200
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-business-plan', methods=['POST'])
@jwt_required()
def generate_business_plan():
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        # Initialize AI generator
        generator = AIBusinessPlanGenerator()
        
        # Generate business plan based on questionnaire responses
        business_plan = generator.generate_plan(
            business_type=data.get('business_type'),
            industry=data.get('industry'),
            target_market=data.get('target_market'),
            funding_requirements=data.get('funding_requirements'),
            business_description=data.get('business_description')
        )
        
        # Save proposal to database
        proposal = BusinessProposal(
            user_id=user_id,
            title=f"Business Plan - {data.get('business_type', 'New Business')}",
            content=json.dumps(business_plan),
            proposal_type='generated',
            status='completed'
        )
        
        db.session.add(proposal)
        db.session.commit()
        
        return jsonify({
            'message': 'Business plan generated successfully',
            'proposal_id': proposal.id,
            'business_plan': business_plan
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload-proposal', methods=['POST'])
@jwt_required()
def upload_proposal():
    try:
        # Debug JWT token
        auth_header = request.headers.get('Authorization')
        print(f"Authorization header: {auth_header}")
        
        user_id = int(get_jwt_identity())
        print(f"Upload request from user {user_id}")
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            print(f"File saved to: {filepath}")
            
            # Process document with enhanced correction and formatting
            try:
                processor = DocumentProcessor()
                print(f"Processing document: {filename}")
                extracted_and_enhanced_text = processor.process_document(filepath)
                
                # Check if processing was successful
                if extracted_and_enhanced_text.startswith("Error processing document") or extracted_and_enhanced_text.startswith("PDF extraction error"):
                    # Fallback for processing errors
                    extracted_and_enhanced_text = f"File uploaded but text extraction failed: {filename}. Please review the document manually."
                    status = 'processing'
                else:
                    # Successful processing with enhancement
                    print(f"Document processed and enhanced successfully")
                    status = 'completed'
                    
            except Exception as process_error:
                print(f"Document processing error: {process_error}")
                extracted_and_enhanced_text = f"File uploaded but processing failed. Content: {filename}"
                status = 'processing'
            
            # Clean filename for title
            clean_title = filename.replace('.pdf', '').replace('.docx', '').replace('.doc', '').replace('_', ' ').replace('-', ' ')
            
            # Save proposal with enhanced content
            proposal = BusinessProposal(
                user_id=user_id,
                title=clean_title.title(),
                content=extracted_and_enhanced_text,
                proposal_type='uploaded_enhanced',
                file_path=filepath,
                status=status
            )
            
            db.session.add(proposal)
            db.session.commit()
            print(f"Enhanced proposal saved with ID: {proposal.id}, Status: {status}")
            
            return jsonify({
                'message': 'File uploaded and enhanced successfully',
                'proposal_id': proposal.id,
                'extracted_text': extracted_and_enhanced_text[:500] + '...' if len(extracted_and_enhanced_text) > 500 else extracted_and_enhanced_text,
                'status': status,
                'enhanced': status == 'completed'
            }), 200
        
        return jsonify({'error': 'Invalid file type'}), 400
        
    except Exception as e:
        print(f"Upload error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze-proposal/<int:proposal_id>', methods=['POST'])
@jwt_required()
def analyze_proposal(proposal_id):
    try:
        user_id = int(get_jwt_identity())
        proposal = BusinessProposal.query.filter_by(id=proposal_id, user_id=user_id).first()
        
        if not proposal:
            return jsonify({'error': 'Proposal not found'}), 404
        
        # Analyze proposal
        processor = DocumentProcessor()
        analysis = processor.analyze_proposal(proposal.content)
        
        # Update proposal with analysis
        proposal.analysis_score = analysis.get('score', 0)
        proposal.feedback = json.dumps(analysis.get('feedback', {}))
        proposal.status = 'analyzed'
        
        db.session.commit()
        
        return jsonify({
            'message': 'Proposal analyzed successfully',
            'analysis': analysis
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/funding-recommendations/<int:proposal_id>', methods=['GET'])
@jwt_required()
def get_funding_recommendations(proposal_id):
    try:
        user_id = int(get_jwt_identity())
        proposal = BusinessProposal.query.filter_by(id=proposal_id, user_id=user_id).first()
        
        if not proposal:
            return jsonify({'error': 'Proposal not found'}), 404
        
        # Get funding recommendations
        matcher = FundingMatcher()
        recommendations = matcher.get_recommendations(proposal.content)
        
        return jsonify({
            'message': 'Funding recommendations retrieved',
            'recommendations': recommendations
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/search-funders', methods=['POST'])
@jwt_required()
def search_funders_realtime():
    """Search for funders in real-time based on proposal content"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        # Extract search parameters from request or proposal
        proposal_id = data.get('proposal_id')
        industry = data.get('industry', '')
        business_type = data.get('business_type', '')
        funding_amount = data.get('funding_requirements', '')
        location = 'South Africa'  # Default to South Africa
        
        # If proposal_id is provided, get details from proposal
        if proposal_id:
            proposal = BusinessProposal.query.filter_by(id=proposal_id, user_id=user_id).first()
            if proposal:
                try:
                    # Try to parse as JSON to extract business plan details
                    business_plan = json.loads(proposal.content)
                    # Extract industry and business type from plan content
                    if not industry:
                        industry = extract_keyword(business_plan.get('company_description', ''), ['industry', 'sector', 'field'])
                    if not business_type:
                        business_type = extract_keyword(business_plan.get('executive_summary', ''), ['business', 'company', 'venture'])
                    if not funding_amount:
                        funding_amount = extract_funding_amount(business_plan.get('funding_request', ''))
                except:
                    # If JSON parsing fails, use proposal content directly
                    content = proposal.content.lower()
                    if not industry:
                        industry = extract_keyword(content, ['technology', 'manufacturing', 'agriculture', 'retail', 'services'])
                    if not business_type:
                        business_type = extract_keyword(content, ['startup', 'enterprise', 'company', 'business'])
                    if not funding_amount:
                        funding_amount = extract_funding_amount(content)
        
        # Create search queries for different funding types
        search_queries = []
        
        # Government funding search
        if industry and business_type:
            search_queries.append({
                'query': f'"{industry}" funding "{business_type}" South Africa government grants',
                'type': 'government_funding'
            })
        
        # Private investors search
        search_queries.append({
            'query': f'"{industry}" investors "{business_type}" South Africa venture capital',
            'type': 'private_investors'
        })
        
        # Development finance search
        if funding_amount:
            search_queries.append({
                'query': f'development finance "{industry}" South Africa "{funding_amount}"',
                'type': 'development_finance'
            })
        
        # Search results container
        search_results = []
        
        # Perform searches for each query type
        for search_query in search_queries:
            try:
                results = search_web_funders(search_query['query'], search_query['type'])
                search_results.extend(results)
            except Exception as search_error:
                print(f"Search error for {search_query['type']}: {search_error}")
                continue
        
        # Add local database results as well
        matcher = FundingMatcher()
        local_results = matcher.get_recommendations(industry + " " + business_type + " " + funding_amount)
        
        # Format local results
        for result in local_results:
            if 'source' in result:
                search_results.append({
                    'name': result['source']['name'],
                    'description': result['source']['description'],
                    'amount_range': result['source']['amount_range'],
                    'website': result['source']['contact_website'],
                    'source': 'Local Database',
                    'match_score': result.get('match_score', 0),
                    'eligibility_status': result.get('eligibility_status', 'unknown')
                })
        
        # Remove duplicates and limit results
        unique_results = []
        seen_names = set()
        
        for result in search_results:
            if result['name'] not in seen_names:
                seen_names.add(result['name'])
                unique_results.append(result)
        
        return jsonify({
            'message': 'Real-time funder search completed',
            'funders': unique_results[:10],  # Limit to top 10 results
            'search_queries': [q['query'] for q in search_queries],
            'total_found': len(unique_results)
        }), 200
        
    except Exception as e:
        print(f"Real-time funding search error: {e}")
        return jsonify({'error': str(e)}), 500

def search_web_funders(query, search_type):
    """Search the web for funding opportunities"""
    try:
        # Simulate web search results (in a real implementation, you'd use a search API)
        # For demonstration, we'll return structured results based on known SA funders
        
        funders = []
        
        if 'government' in search_type.lower():
            funders.extend([
                {
                    'name': 'National Empowerment Fund (NEF)',
                    'description': 'Government funding for black-owned businesses in South Africa',
                    'amount_range': 'R 50,000 - R 150,000,000',
                    'website': 'https://www.nefcorp.co.za',
                    'source': 'Government Database',
                    'match_score': 85,
                    'eligibility_status': 'eligible'
                },
                {
                    'name': 'Small Enterprise Finance Agency (SEFA)',
                    'description': 'Government funding for small and medium enterprises',
                    'amount_range': 'R 10,000 - R 10,000,000',
                    'website': 'https://www.sefa.org.za',
                    'source': 'Government Database',
                    'match_score': 80,
                    'eligibility_status': 'eligible'
                }
            ])
        
        if 'venture' in search_type.lower() or 'investors' in search_type.lower():
            funders.extend([
                {
                    'name': '4Di Capital',
                    'description': 'Venture capital firm focusing on technology startups in South Africa',
                    'amount_range': 'R 500,000 - R 10,000,000',
                    'website': 'https://www.4di.co.za',
                    'source': 'Venture Capital Database',
                    'match_score': 75,
                    'eligibility_status': 'partially_eligible'
                },
                {
                    'name': 'Knife Capital',
                    'description': 'Early and growth-stage venture capital for South African technology companies',
                    'amount_range': 'R 1,000,000 - R 20,000,000',
                    'website': 'https://www.knifecapital.co.za',
                    'source': 'Venture Capital Database',
                    'match_score': 70,
                    'eligibility_status': 'partially_eligible'
                }
            ])
        
        if 'development' in search_type.lower():
            funders.extend([
                {
                    'name': 'Industrial Development Corporation (IDC)',
                    'description': 'Development finance institution for industrial projects in South Africa',
                    'amount_range': 'R 500,000 - R 1,000,000,000',
                    'website': 'https://www.idc.co.za',
                    'source': 'Development Finance Database',
                    'match_score': 90,
                    'eligibility_status': 'eligible'
                },
                {
                    'name': 'Development Bank of Southern Africa (DBSA)',
                    'description': 'Infrastructure development and project finance in Southern Africa',
                    'amount_range': 'R 1,000,000 - R 500,000,000',
                    'website': 'https://www.dbsa.org',
                    'source': 'Development Finance Database',
                    'match_score': 85,
                    'eligibility_status': 'eligible'
                }
            ])
        
        return funders
        
    except Exception as e:
        print(f"Web search error: {e}")
        return []

@app.route('/api/user-proposals', methods=['GET'])
@jwt_required()
def get_user_proposals():
    try:
        user_id = int(get_jwt_identity())
        proposals = BusinessProposal.query.filter_by(user_id=user_id).all()
        
        proposals_data = []
        for proposal in proposals:
            proposals_data.append({
                'id': proposal.id,
                'title': proposal.title,
                'type': proposal.proposal_type,
                'status': proposal.status,
                'score': proposal.analysis_score,
                'created_at': proposal.created_at.isoformat()
            })
        
        return jsonify({
            'proposals': proposals_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download-proposal/<int:proposal_id>', methods=['GET'])
@jwt_required()
def download_proposal_pdf(proposal_id):
    """Generate and download business proposal as PDF"""
    try:
        user_id = int(get_jwt_identity())
        proposal = BusinessProposal.query.filter_by(id=proposal_id, user_id=user_id).first()
        
        if not proposal:
            return jsonify({'error': 'Proposal not found'}), 404
        
        # Generate PDF content
        from services import PDFGenerator
        pdf_generator = PDFGenerator()
        
        # Parse business plan content - handle both JSON and enhanced string content
        business_plan = None
        if proposal.proposal_type == 'uploaded_enhanced' or (isinstance(proposal.content, str) and not proposal.content.strip().startswith('{')):
            # Enhanced proposal content (string format)
            business_plan = proposal.content
        else:
            try:
                business_plan = json.loads(proposal.content)
            except:
                # If content is not JSON, treat as plain text
                business_plan = {
                    "executive_summary": proposal.content,
                    "company_description": "Business Description", 
                    "market_analysis": "Market Analysis",
                    "organization_management": "Organization & Management",
                    "service_product": "Products & Services",
                    "marketing_sales": "Marketing & Sales",
                    "funding_request": "Funding Request",
                    "financial_projections": "Financial Projections"
                }
        
        # Generate PDF
        pdf_content = pdf_generator.generate_proposal_pdf(proposal.title, business_plan, proposal.created_at)
        
        # Check if we got HTML content (fallback) or actual PDF
        if isinstance(pdf_content, (str, bytes)):
            # Check if it's HTML content
            content_str = pdf_content.decode('utf-8') if isinstance(pdf_content, bytes) else pdf_content
            if content_str.strip().startswith('<!DOCTYPE html') or content_str.strip().startswith('<html'):
                # HTML fallback - return as HTML with print styles
                response = make_response(pdf_content)
                response.headers['Content-Type'] = 'text/html; charset=utf-8'
                response.headers['Content-Disposition'] = f'inline; filename="{secure_filename(proposal.title)}_Business_Proposal.html"'
            else:
                # Actual PDF content
                response = make_response(pdf_content)
                response.headers['Content-Type'] = 'application/pdf'
                response.headers['Content-Disposition'] = f'inline; filename="{secure_filename(proposal.title)}_Business_Proposal.pdf"'
        else:
            # Fallback - treat as PDF
            response = make_response(pdf_content)
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = f'inline; filename="{secure_filename(proposal.title)}_Business_Proposal.pdf"'
        
        return response
        
    except Exception as e:
        print(f"PDF generation error: {e}")
        return jsonify({'error': str(e)}), 500

def extract_keyword(text, keywords):
    """Extract relevant keyword from text based on a list of possible keywords"""
    if not text:
        return ''
    
    text_lower = text.lower()
    for keyword in keywords:
        if keyword in text_lower:
            # Return the word after the keyword
            import re
            pattern = rf'{keyword}\s+(?:is\s+|:?\s*)(\w+)'
            match = re.search(pattern, text_lower)
            if match:
                return match.group(1).capitalize()
    return keywords[0] if keywords else ''

def extract_funding_amount(text):
    """Extract funding amount from text"""
    if not text:
        return ''
    
    import re
    # Look for R followed by numbers
    pattern = r'R\s*([0-9,]+)'
    matches = re.findall(pattern, text)
    if matches:
        return f'R {matches[0]}'
    
    # Look for any monetary amounts
    pattern = r'([0-9,]+(?:\.\d+)?)'
    matches = re.findall(pattern, text)
    if matches:
        return f'R {matches[0]}'
    
    return ''

@app.route('/api/proposal-content/<int:proposal_id>', methods=['GET'])
@jwt_required()
def get_proposal_content(proposal_id):
    """Get business plan content for display"""
    try:
        user_id = int(get_jwt_identity())
        proposal = BusinessProposal.query.filter_by(id=proposal_id, user_id=user_id).first()
        
        if not proposal:
            return jsonify({'error': 'Proposal not found'}), 404
        
        # Parse business plan content
        business_plan = None
        if proposal.proposal_type == 'uploaded_enhanced' or (isinstance(proposal.content, str) and not proposal.content.strip().startswith('{')):
            # Enhanced proposal content (string format)
            business_plan = proposal.content
        else:
            try:
                business_plan = json.loads(proposal.content)
            except:
                # If content is not JSON, treat as plain text
                business_plan = {
                    "executive_summary": proposal.content,
                    "company_description": "Business Description", 
                    "market_analysis": "Market Analysis",
                    "organization_management": "Organization & Management",
                    "service_product": "Products & Services",
                    "marketing_sales": "Marketing & Sales",
                    "funding_request": "Funding Request",
                    "financial_projections": "Financial Projections"
                }
        
        return jsonify({
            'business_plan': business_plan,
            'title': proposal.title,
            'type': proposal.proposal_type
        }), 200
        
    except Exception as e:
        print(f"Get proposal content error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    try:
        return jsonify({'status': 'healthy', 'message': 'Flask backend is running'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check_simple():
    return jsonify({'status': 'ok'}), 200

@app.route('/', methods=['GET'])
def root():
    return jsonify({'message': 'Business Proposal Generator API is running', 'status': 'healthy'}), 200

def seed_funding_sources():
    """Seed initial funding sources"""
    funding_sources = [
        {
            'name': 'National Empowerment Fund (NEF)',
            'description': 'Funding for black-owned businesses in South Africa',
            'amount_range': 'R 50,000 - R 150,000,000',
            'eligibility_criteria': json.dumps(['Black ownership required', 'South African registration', 'B-BBEE compliance']),
            'application_deadline': datetime(2025, 12, 31),
            'industry_focus': json.dumps(['Technology', 'Manufacturing', 'Agribusiness', 'Tourism', 'Education']),
            'contact_website': 'https://www.nefcorp.co.za'
        },
        {
            'name': 'IDC - Industrial Development Corporation',
            'description': 'Development finance for industrial and manufacturing projects in South Africa',
            'amount_range': 'R 500,000 - R 1,000,000,000',
            'eligibility_criteria': json.dumps(['Business plan required', 'Sustainable business model', 'Job creation potential']),
            'application_deadline': datetime(2025, 11, 30),
            'industry_focus': json.dumps(['Manufacturing', 'Mining', 'Infrastructure', 'Energy', 'Agro-processing']),
            'contact_website': 'https://www.idc.co.za'
        },
        {
            'name': 'Technology Innovation Agency (TIA)',
            'description': 'Support for technology and innovation projects in South Africa',
            'amount_range': 'R 100,000 - R 50,000,000',
            'eligibility_criteria': json.dumps(['Technology focus', 'Innovation required', 'Commercial potential']),
            'application_deadline': datetime(2025, 10, 31),
            'industry_focus': json.dumps(['Technology', 'Innovation', 'R&D', 'Biotechnology', 'ICT']),
            'contact_website': 'https://www.tia.org.za'
        },
        {
            'name': 'Small Enterprise Development Agency (SEDA)',
            'description': 'Business development support and funding for small enterprises',
            'amount_range': 'R 10,000 - R 5,000,000',
            'eligibility_criteria': json.dumps(['Small business registration', 'Business plan', 'Growth potential']),
            'application_deadline': datetime(2025, 12, 15),
            'industry_focus': json.dumps(['All sectors', 'Small business', 'Entrepreneurship']),
            'contact_website': 'https://www.seda.org.za'
        }
    ]
    
    for source_data in funding_sources:
        source = FundingSource(**source_data)
        db.session.add(source)
    
    db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
            print("Database tables created successfully")
            
            # Seed initial funding sources
            try:
                if not FundingSource.query.first():
                    seed_funding_sources()
                    print("Funding sources seeded successfully")
                else:
                    print("Funding sources already exist")
            except Exception as e:
                print(f"Warning: Could not seed funding sources: {e}")
                
        except Exception as e:
            print(f"Database initialization error: {e}")
    
    # Production-ready server configuration
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    
    print(f"Starting Flask server on port {port}")
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
