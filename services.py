import os
import json
from typing import Dict, List, Any
import re
from datetime import datetime

try:
    import openai
    from openai import OpenAI
except ImportError:
    print("OpenAI not installed. Install with: pip install openai")

try:
    import pytesseract
    from PIL import Image
except ImportError:
    print("OCR libraries not installed. Install with: pip install pytesseract pillow")

try:
    import PyPDF2
    from docx import Document
except ImportError:
    print("Document processing libraries not installed. Install with: pip install PyPDF2 python-docx")

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import pandas as pd
    SKLEARN_AVAILABLE = True
except ImportError:
    print("Scikit-learn and pandas not available. Some advanced features will be limited.")
    SKLEARN_AVAILABLE = False

class AIBusinessPlanGenerator:
    """AI-powered business plan generator using OpenAI API or template-based generation"""
    
    def __init__(self):
        # Initialize OpenAI client if API key is available
        self.openai_client = None
        if os.getenv('OPENAI_API_KEY'):
            try:
                self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            except Exception as e:
                print(f"OpenAI initialization failed: {e}")
    
    def generate_plan(self, business_type: str, industry: str, target_market: str, 
                     funding_requirements: str, business_description: str) -> Dict[str, Any]:
        """Generate a comprehensive business plan based on input parameters"""
        
        try:
            if self.openai_client:
                return self._generate_with_openai(business_type, industry, target_market, 
                                                funding_requirements, business_description)
            else:
                return self._generate_with_templates(business_type, industry, target_market, 
                                                   funding_requirements, business_description)
        except Exception as e:
            print(f"Business plan generation error: {e}")
            return self._generate_fallback_plan(business_type, industry, target_market, 
                                              funding_requirements, business_description)
    
    def _generate_with_openai(self, business_type: str, industry: str, target_market: str, 
                             funding_requirements: str, business_description: str) -> Dict[str, Any]:
        """Generate business plan using OpenAI API with research-based enhanced content"""
        
        formatted_funding = self._format_currency_zar(funding_requirements)
        
        # First, research similar business plans and gather insights
        research_prompt = f"""
        I need you to research and analyze successful business plans for businesses similar to the following:
        - Business Type: {business_type}
        - Industry: {industry}  
        - Target Market: {target_market}
        
        Please provide insights on:
        1. Common successful strategies used in similar businesses
        2. Key success factors and best practices in this industry
        3. Typical financial structures and funding approaches
        4. Market entry strategies that work well
        5. Risk factors commonly faced by similar businesses
        
        Focus on South African market context and provide specific, actionable insights.
        """
        
        # Generate enhanced business plan with research insights
        prompt = f"""
        Generate a comprehensive business plan for a South African business that incorporates research from similar successful businesses. Use the research insights to create a more informed and strategic plan.
        
        BUSINESS DETAILS:
        - Business Type: {business_type}
        - Industry: {industry}
        - Target Market: {target_market}
        - Funding Requirements: {formatted_funding}
        - Business Description: {business_description}
        
        ENHANCED REQUIREMENTS:
        - Research similar successful businesses in the {industry} sector targeting {target_market}
        - Incorporate proven strategies and best practices from successful {business_type} ventures
        - Include specific South African market insights and regulatory considerations
        - All financial amounts should be in South African Rand (ZAR)
        - Include B-BBEE compliance considerations and transformation strategies
        - Reference local market conditions, opportunities, and competitive landscape
        - Minimum 200 words per section with proper business plan structure
        
        COMPREHENSIVE BUSINESS PLAN STRUCTURE:
        Generate a detailed business plan with these sections (each section must be substantial and well-researched):
        
        1. Executive Summary (minimum 200 words)
           - Company overview and mission
           - Market opportunity and competitive advantage
           - Financial highlights and funding needs
           - Key success factors and projected outcomes
        
        2. Company Description (minimum 200 words)
           - Business structure and legal entity details
           - Mission, vision, and core values
           - Products/services overview and unique value proposition
           - Company history, ownership, and management credentials
        
        3. Market Analysis (minimum 250 words)
           - Industry overview and South African market size
           - Target market analysis and customer demographics
           - Competitive landscape and positioning strategy
           - Market trends, opportunities, and growth potential
        
        4. Organization & Management (minimum 200 words)
           - Management team structure and key personnel
           - Organizational chart and reporting relationships
           - Roles, responsibilities, and qualifications
           - Advisory board and external support systems
        
        5. Products & Services (minimum 200 words)
           - Detailed product/service portfolio
           - Competitive advantages and differentiation factors
           - Pricing strategy and revenue models
           - Product development roadmap and innovation plans
        
        6. Marketing & Sales Strategy (minimum 250 words)
           - Target customer identification and segmentation
           - Marketing channels and promotional strategies
           - Sales process and distribution methods
           - Customer acquisition and retention programs
        
        7. Funding Request (minimum 200 words)
           - Detailed funding breakdown and use of funds
           - Capital structure and funding sources
           - Return on investment projections and exit strategies
           - Investor benefits and risk mitigation measures
        
        8. Financial Projections (minimum 250 words)
           - 3-year revenue and expense forecasts with detailed assumptions
           - Cash flow projections and working capital requirements
           - Break-even analysis and key financial metrics
           - Sensitivity analysis and scenario planning
        
        9. Risk Analysis & Mitigation (minimum 200 words)
           - Identification of key business and market risks
           - Risk assessment and impact analysis
           - Mitigation strategies and contingency planning
           - Insurance and legal protection measures
        
        10. Implementation Timeline (minimum 200 words)
            - Phase-by-phase implementation plan with milestones
            - Resource allocation and project timelines
            - Key performance indicators and success metrics
            - Monitoring and evaluation framework
        
        Ensure each section is comprehensive, professional, and draws insights from successful similar businesses in the {industry} sector. The total business plan should exceed 2000 words and follow proper business plan formatting and structure.
        """
        
        try:
            # First, get research insights for similar businesses
            research_response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": research_prompt}],
                max_tokens=1000,
                temperature=0.6
            )
            
            research_insights = research_response.choices[0].message.content
            
            # Enhanced prompt that includes research insights
            enhanced_prompt = f"""
            RESEARCH INSIGHTS FROM SIMILAR BUSINESSES:
            {research_insights}
            
            {prompt}
            
            IMPORTANT: Use the research insights above to inform your business plan generation. Incorporate successful strategies, best practices, and lessons learned from similar businesses to create a more robust and realistic plan.
            """
            
            # Generate comprehensive business plan with research insights
            response = self.openai_client.chat.completions.create(
                model="gpt-4",  # Use GPT-4 for better quality and longer responses
                messages=[{"role": "user", "content": enhanced_prompt}],
                max_tokens=4000,  # Increased token limit for comprehensive content
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            
            # Try to parse as JSON, fallback to structured text
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return self._parse_text_to_structured(content)
                
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return self._generate_with_templates(business_type, industry, target_market, 
                                               funding_requirements, business_description)
    
    def _generate_with_templates(self, business_type: str, industry: str, target_market: str, 
                               funding_requirements: str, business_description: str) -> Dict[str, Any]:
        """Generate comprehensive professional business plan using enhanced South African templates with research insights"""
        
        # Format funding requirements to include ZAR currency
        formatted_funding = self._format_currency_zar(funding_requirements)
        current_date = datetime.now().strftime("%B %Y")
        
        # Research insights for similar businesses (embedded template enhancement)
        research_context = self._get_research_insights_template(business_type, industry, target_market)
        
        return {
            "executive_summary": f"""
EXECUTIVE SUMMARY
Generated: {current_date}

COMPANY OVERVIEW
Our venture is a {business_type} operating in the dynamic {industry} sector, strategically positioned to serve the {target_market} market segment. Based on comprehensive analysis of successful businesses in similar market positions, our approach incorporates proven strategies and best practices that have demonstrated success in the South African business environment. Our mission centers around {business_description}, positioning us to capitalize on significant market opportunities while contributing to local economic development.

TARGET MARKET ANALYSIS & COMPETITIVE ADVANTAGE
Our primary target market encompasses {target_market}, a segment that research shows has demonstrated strong growth potential and resilience in the South African economy. Through analysis of successful {business_type} operations in the {industry} sector, we have identified key success factors including customer relationship excellence, technology integration, and strategic market positioning. Our competitive advantage stems from our deep understanding of local market dynamics, combined with innovative approaches learned from industry leaders who have successfully navigated similar market conditions.

FUNDING REQUIREMENTS & STRATEGIC IMPLEMENTATION
We are seeking {formatted_funding} in total capital to establish and scale our operations effectively. This funding will be strategically allocated based on insights from similar successful businesses, prioritizing areas that have shown the highest return on investment in comparable ventures. Our financial projections are grounded in realistic market assessments and conservative growth assumptions, ensuring sustainable development and risk mitigation.

STRATEGIC OBJECTIVES & GROWTH TRAJECTORY
Our strategic objectives focus on establishing market leadership through innovation, building sustainable competitive advantages, and achieving profitable growth while maintaining B-BBEE compliance. These goals are informed by successful business models in our sector and are designed to create employment opportunities while delivering superior value to our target market. The execution timeline incorporates phased implementation approaches that have proven effective for similar businesses, ensuring measured and sustainable growth.
            """,
            
            "company_description": f"""
COMPANY DESCRIPTION
Our organization is a {business_type} registered and operating within the {industry} industry classification, strategically positioned to serve the {target_market} market segment. Our legal structure will be determined based on optimal operational requirements, likely incorporating as a Proprietary Limited company (Pty Ltd) to ensure proper governance, liability protection, and growth facilitation. The company registration process with the Companies and Intellectual Property Commission (CIPC) is integral to our establishment timeline and will ensure full regulatory compliance from inception.

COMPANY MISSION & VISION FRAMEWORK
Our mission statement centers on {business_description}, driving our commitment to deliver exceptional value and innovation within our chosen market segment. This mission is informed by successful business models we have analyzed in similar {business_type} operations, ensuring our approach incorporates proven strategies while maintaining our unique value proposition. Our vision is to become the leading {business_type} in the {industry} sector, recognized nationally for excellence in serving {target_market} across South Africa while contributing significantly to economic development and transformation objectives.

CORE VALUES & OPERATIONAL PRINCIPLES
Our organizational values form the foundation of all business operations and decision-making processes. These include unwavering commitment to integrity and ethical business practices, continuous innovation and improvement methodologies, comprehensive B-BBEE compliance and transformation initiatives, customer-centric approaches that prioritize client satisfaction and long-term relationships, and social responsibility that extends beyond profit objectives to meaningful community impact and sustainable business practices.

OPERATIONAL SCOPE & BUSINESS MODEL
Our primary geographic focus encompasses South Africa as the core market, with strategic consideration for regional expansion opportunities as the business matures. Our target market segments specifically address {target_market}, where we have identified significant opportunity based on comprehensive market analysis and competitor research. Our business model incorporates multiple revenue streams designed for sustainability and growth, with our core value proposition delivering unique benefits specifically tailored to {target_market} needs and requirements.
            """,
            
            "market_analysis": f"""
MARKET ANALYSIS - SOUTH AFRICAN CONTEXT
Analysis Date: {current_date}

TARGET MARKET PROFILE
Primary Market: {target_market}
Market Size: [To be researched - include SA market statistics]
Market Growth Rate: [Industry growth projections for SA]

INDUSTRY OVERVIEW
Sector: {industry}
Current Industry Trends in South Africa:
- Economic recovery and infrastructure development
- Digital transformation and technology adoption
- B-BBEE requirements and transformation goals
- Government support for small and medium enterprises

COMPETITIVE LANDSCAPE
Direct Competitors: [List main competitors operating in SA]
Competitive Advantages: 
- Local market knowledge and relationships
- Understanding of SA regulatory environment
- Competitive pricing and service delivery
- B-BBEE compliance for government contracts

MARKET ENTRY STRATEGY
- Leverage local market understanding
- Build strategic partnerships with established players
- Focus on underserved market segments
- Implement competitive pricing strategies

RISK ANALYSIS
Market Risks: Economic volatility, regulatory changes, competition
Mitigation Strategies: Diversified approach, strong relationships, adaptable operations
            """,
            
            "organization_management": f"""
ORGANIZATION & MANAGEMENT STRUCTURE

MANAGEMENT TEAM
Chief Executive Officer (CEO): [Name and credentials]
- Primary responsibility: Strategic leadership and stakeholder management
- Qualifications: [Relevant experience in {industry} sector]

Chief Operations Officer (COO): [Name and credentials]  
- Primary responsibility: Day-to-day operations and implementation
- Focus: Operational efficiency and quality management

Chief Financial Officer (CFO): [Name and credentials]
- Primary responsibility: Financial management and funding
- Expertise: Financial planning, compliance, and risk management

ORGANIZATIONAL STRUCTURE
Board of Directors: [Composition including B-BBEE compliance]
Management Hierarchy: Clear reporting structures and responsibilities
Advisory Board: Industry experts and business advisors

HUMAN RESOURCES STRATEGY
Employment Equity Plan: B-BBEE aligned recruitment and development
Skills Development: Training programs and professional development
Performance Management: Clear KPIs and evaluation processes

SUCCESSION PLANNING
Leadership Development: Internal talent pipeline
Knowledge Management: Documentation and training systems
Continuity Planning: Risk mitigation for key personnel changes
            """,
            
            "service_product": f"""
PRODUCTS & SERVICES PORTFOLIO
Business Model: {business_type} in {industry} Sector

PRIMARY OFFERINGS
Core Products/Services: 
[Detailed description of main offerings targeting {target_market}]
- Unique value proposition
- Quality standards and certifications
- Pricing strategy and competitiveness

SECONDARY SERVICES
Value-Added Services:
- Customer support and after-sales service
- Consultation and advisory services
- Customized solutions for specific client needs

TECHNOLOGY & INNOVATION
Digital Platforms: [If applicable - online services, apps, systems]
Innovation Approach: Continuous improvement and R&D investment
Quality Assurance: Standards compliance and certification processes

SUPPLY CHAIN MANAGEMENT
Supplier Relationships: Local and international partnerships
Quality Control: Product/service quality standards
Logistics: Distribution and delivery capabilities

COMPETITIVE POSITIONING
Differentiation Factors:
- Superior service quality and customer experience
- Local market expertise and relationships
- Competitive pricing and flexible terms
- Innovation and technology adoption
            """,
            
            "marketing_sales": f"""
MARKETING & SALES STRATEGY
Target Market: {target_market}

MARKETING APPROACH
Digital Marketing Strategy:
- Website development and SEO optimization
- Social media presence (LinkedIn, Facebook, industry platforms)
- Content marketing and thought leadership
- Email marketing and customer relationship management

Traditional Marketing:
- Industry networking and trade shows
- Print advertising in relevant publications
- Direct mail and promotional campaigns
- Public relations and media engagement

SALES STRATEGY
Sales Channels:
1. Direct Sales: Face-to-face meetings and presentations
2. Digital Sales: Online inquiries and e-commerce capabilities
3. Partnership Sales: Through strategic partners and distributors
4. Referral Programs: Customer referral incentives

Sales Process:
- Lead generation and qualification
- Needs assessment and proposal development
- Presentation and negotiation
- Contract closure and relationship building

CUSTOMER RELATIONSHIP MANAGEMENT
Customer Retention: Loyalty programs and ongoing support
Feedback Systems: Regular customer satisfaction surveys
Service Excellence: Continuous improvement based on customer input

PRICING STRATEGY
Competitive Analysis: Market rate assessment and positioning
Value-Based Pricing: Pricing based on customer value delivered
Flexible Terms: Payment options and contract structures
            """,
            
            "funding_request": f"""
FUNDING REQUEST & CAPITAL STRUCTURE
Total Funding Required: {formatted_funding}
Business Type: {business_type}

FUNDING BREAKDOWN
1. Initial Setup and Infrastructure: 35%
   - Equipment and technology: [Amount in ZAR]
   - Premises and facilities: [Amount in ZAR]
   - Legal and registration costs: [Amount in ZAR]

2. Working Capital: 40%
   - Inventory and supplies: [Amount in ZAR]  
   - Operating expenses (6 months): [Amount in ZAR]
   - Marketing and customer acquisition: [Amount in ZAR]

3. Technology and Systems: 15%
   - Software licenses and IT infrastructure: [Amount in ZAR]
   - Digital platforms and tools: [Amount in ZAR]

4. Reserve and Contingency: 10%
   - Emergency fund and unexpected costs: [Amount in ZAR]

FUNDING SOURCES
Primary Options:
- Government funding (NEF, IDC, SETA programs)
- Bank financing and commercial loans
- Private investors and venture capital
- B-BBEE investors and strategic partners

EXPECTED RETURN ON INVESTMENT
Financial Projections: [3-year financial forecasts]
Break-even Analysis: [Timeline to profitability]
Investor Returns: Expected ROI and exit strategies

RISK MITIGATION
Financial Controls: Budget management and monitoring systems
Insurance Coverage: Business and liability insurance
Contingency Planning: Risk management strategies
            """,
            
            "financial_projections": f"""
FINANCIAL PROJECTIONS & ANALYSIS
Currency: South African Rand (ZAR)
Projection Period: 3 Years

REVENUE PROJECTIONS
Year 1: R [Projected revenue based on market analysis]
Year 2: R [Growth assumptions and market expansion]
Year 3: R [Mature market position and optimization]

Revenue Streams:
- Primary revenue source: [Percentage and amount]
- Secondary revenue sources: [Additional income streams]

EXPENSE PROJECTIONS
Year 1 Operating Expenses:
- Personnel costs: R [Salaries and benefits]
- Marketing and sales: R [Promotional expenses]
- Operations: R [Day-to-day operational costs]
- Technology and systems: R [IT and software costs]
- Professional services: R [Legal, accounting, consulting]
- Office and facilities: R [Rent, utilities, insurance]

FINANCIAL PERFORMANCE METRICS
Year 1: [Revenue - Expenses = Net Income]
Year 2: [Projected improvements and efficiency gains]
Year 3: [Mature operations and optimized performance]

KEY FINANCIAL RATIOS
- Gross profit margin: [Percentage]
- Net profit margin: [Percentage]  
- Return on investment (ROI): [Percentage]
- Break-even point: [Timeline and volume]

CASH FLOW ANALYSIS
Monthly cash flow projections for first 12 months
Quarterly analysis for years 2-3
Working capital requirements and management

FINANCIAL ASSUMPTIONS
Economic conditions in South Africa
Industry growth rates and market trends
Inflation and currency fluctuations
Regulatory and tax considerations
            """
        }
    
    def _get_research_insights_template(self, business_type: str, industry: str, target_market: str) -> str:
        """Get research-based insights for similar businesses to enhance templates"""
        
        # Map common business types and industries to research insights
        research_context = f"""
        Based on analysis of successful {business_type} operations in the {industry} sector targeting {target_market}:
        
        KEY SUCCESS FACTORS:
        - Market positioning and competitive differentiation are critical for {business_type} entities
        - Customer relationship management and service excellence drive retention in {industry}
        - Technology adoption and digital transformation are essential for modern {target_market} engagement
        - Financial management and cash flow optimization are paramount for sustainable growth
        
        COMMON CHALLENGES & SOLUTIONS:
        - Market entry barriers are typically overcome through strategic partnerships and local market knowledge
        - Funding acquisition often requires demonstrating strong business fundamentals and market opportunity
        - Regulatory compliance and B-BBEE alignment provide competitive advantages in South African market
        - Operational scalability requires systematic processes and technology infrastructure
        
        BEST PRACTICES FROM SIMILAR BUSINESSES:
        - Focus on niche market segments before expanding to broader markets
        - Develop strong vendor and supplier relationships for operational efficiency
        - Implement robust financial controls and reporting systems from day one
        - Invest in branding and marketing to build market awareness and credibility
        """
        
        return research_context

    def _format_currency_zar(self, funding_requirements: str) -> str:
        """Format funding requirements to South African Rand (ZAR)"""
        # Clean the input and extract numbers
        import re
        
        # Remove any existing currency symbols and commas
        clean_text = re.sub(r'[^\d.]', '', funding_requirements)
        
        try:
            # Try to parse as number
            if clean_text:
                amount = float(clean_text)
                # Format with proper ZAR formatting
                if amount >= 1000000:
                    return f"R {amount:,.0f}"
                elif amount >= 1000:
                    return f"R {amount:,.0f}"
                else:
                    return f"R {amount:,.2f}"
            else:
                return f"R {funding_requirements}"
        except ValueError:
            # If parsing fails, just add R prefix and return
            return f"R {funding_requirements}"
    
    def _generate_fallback_plan(self, business_type: str, industry: str, target_market: str, 
                              funding_requirements: str, business_description: str) -> Dict[str, Any]:
        """Fallback plan generation if all else fails"""
        
        return {
            "error": "AI generation unavailable",
            "basic_plan": {
                "business_type": business_type,
                "industry": industry,
                "target_market": target_market,
                "funding_requirements": funding_requirements,
                "business_description": business_description,
                "generated_at": datetime.now().isoformat()
            }
        }
    
    def _parse_text_to_structured(self, text: str) -> Dict[str, Any]:
        """Parse unstructured text into structured business plan format"""
        
        sections = {}
        current_section = None
        current_content = []
        
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if this line is a section header
            if any(keyword in line.lower() for keyword in 
                   ['executive summary', 'company description', 'market analysis', 
                    'organization', 'management', 'service', 'product', 'marketing', 
                    'sales', 'funding', 'financial']):
                
                # Save previous section
                if current_section:
                    sections[current_section] = '\n'.join(current_content)
                
                # Start new section
                current_section = line
                current_content = []
            else:
                current_content.append(line)
        
        # Save last section
        if current_section:
            sections[current_section] = '\n'.join(current_content)
        
        return sections if sections else {"content": text}


class DocumentProcessor:
    """Handle document processing including OCR, text extraction, correction, and enhancement"""
    
    def __init__(self):
        self.supported_formats = {'.pdf', '.doc', '.docx', '.txt', '.png', '.jpg', '.jpeg'}
    
    def process_document(self, file_path: str) -> str:
        """Extract and process document with enhancement"""
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_ext = os.path.splitext(file_path)[1].lower()
        
        try:
            # Extract raw text first
            raw_text = self._extract_text_by_format(file_path, file_ext)
            
            # Enhance and correct the proposal
            enhanced_proposal = self.enhance_proposal(raw_text, file_path)
            
            return enhanced_proposal
            
        except Exception as e:
            print(f"Document processing error: {e}")
            return f"Error processing document: {str(e)}"
    
    def _extract_text_by_format(self, file_path: str, file_ext: str) -> str:
        """Extract text from various document formats"""
        
        try:
            if file_ext == '.pdf':
                return self._extract_from_pdf(file_path)
            elif file_ext in ['.doc', '.docx']:
                return self._extract_from_word(file_path)
            elif file_ext in ['.png', '.jpg', '.jpeg']:
                return self._extract_from_image(file_path)
            elif file_ext == '.txt':
                return self._extract_from_text(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")
        except Exception as e:
            print(f"Document processing error: {e}")
            return f"Error processing document: {str(e)}"
    
    def enhance_proposal(self, raw_text: str, file_path: str) -> str:
        """Enhance and correct uploaded business proposal with formatting, details, and structure"""
        
        try:
            # Clean and format the raw text
            cleaned_text = self._clean_and_format_text(raw_text)
            
            # Parse and structure the content
            structured_content = self._parse_and_structure_content(cleaned_text)
            
            # Enhance with missing sections and details
            enhanced_content = self._enhance_with_missing_sections(structured_content)
            
            # Format as professional business proposal
            formatted_proposal = self._format_as_professional_proposal(enhanced_content)
            
            return formatted_proposal
            
        except Exception as e:
            print(f"Proposal enhancement error: {e}")
            return raw_text  # Return original if enhancement fails
    
    def _clean_and_format_text(self, text: str) -> str:
        """Clean and format the extracted text"""
        
        # Basic text cleaning
        text = re.sub(r'\s+', ' ', text)  # Remove extra whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)  # Normalize paragraph breaks
        text = text.strip()
        
        # Fix common OCR/formatting issues
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)  # Fix missing spaces between words
        text = re.sub(r'([.!?])([A-Z])', r'\1 \2', text)  # Fix missing spaces after sentences
        
        return text
    
    def _parse_and_structure_content(self, text: str) -> Dict[str, str]:
        """Parse text and structure it into business plan sections"""
        
        # Define section patterns
        section_patterns = {
            'executive_summary': r'(?i)(executive\s+summary|summary|overview)',
            'company_description': r'(?i)(company\s+description|business\s+description|about\s+us|organization)',
            'market_analysis': r'(?i)(market\s+analysis|market\s+research|industry\s+analysis)',
            'organization_management': r'(?i)(management|team|organization|personnel)',
            'service_product': r'(?i)(product|service|offering|solution|what\s+we\s+do)',
            'marketing_sales': r'(?i)(marketing|sales|strategy|promotion|business\s+development)',
            'funding_request': r'(?i)(funding|investment|capital|loan|financial\s+request)',
            'financial_projections': r'(?i)(financial|projection|budget|revenue|cost|profit)'
        }
        
        sections = {}
        remaining_text = text
        
        # Extract sections using patterns
        for section_key, pattern in section_patterns.items():
            match = re.search(pattern, remaining_text)
            if match:
                start_pos = match.end()
                
                # Find the end of this section (start of next section or end of text)
                next_section_pos = len(remaining_text)
                for other_pattern in section_patterns.values():
                    next_match = re.search(other_pattern, remaining_text[start_pos:])
                    if next_match:
                        next_section_pos = min(next_section_pos, start_pos + next_match.start())
                
                section_content = remaining_text[start_pos:next_section_pos].strip()
                if section_content:
                    sections[section_key] = section_content
        
        # If no sections found, treat entire text as content
        if not sections:
            sections['content'] = text
        
        return sections
    
    def _enhance_with_missing_sections(self, structured_content: Dict[str, str]) -> Dict[str, str]:
        """Add missing sections and enhance existing ones with necessary details"""
        
        enhanced_content = structured_content.copy()
        
        # Required sections for a comprehensive business proposal
        required_sections = {
            'executive_summary': 'Executive Summary',
            'company_description': 'Company Description',
            'market_analysis': 'Market Analysis',
            'organization_management': 'Organization & Management',
            'service_product': 'Products & Services',
            'marketing_sales': 'Marketing & Sales Strategy',
            'funding_request': 'Funding Request',
            'financial_projections': 'Financial Projections'
        }
        
        # Add missing sections with template content
        for section_key, section_title in required_sections.items():
            if section_key not in enhanced_content:
                enhanced_content[section_key] = self._generate_section_template(section_key, section_title, enhanced_content)
            else:
                # Enhance existing content
                enhanced_content[section_key] = self._enhance_existing_section(section_key, enhanced_content[section_key])
        
        return enhanced_content
    
    def _generate_section_template(self, section_key: str, section_title: str, existing_content: Dict[str, str]) -> str:
        """Generate template content for missing sections"""
        
        current_date = datetime.now().strftime("%B %d, %Y")
        
        templates = {
            'executive_summary': f"""
COMPANY OVERVIEW
Our company is a South African business seeking funding to expand operations and achieve growth objectives. This executive summary provides a high-level overview of our business model, market opportunity, and funding requirements.

BUSINESS OBJECTIVE
We aim to establish a successful operation that contributes to the South African economy while providing value to our target market. Our business model is designed for sustainable growth and profitability.

FUNDING OVERVIEW
We are seeking funding to support our business growth and operational expansion. The requested funds will be utilized for [to be specified based on business type].

CONTACT INFORMATION
Generated on: {current_date}
Location: South Africa
            """,
            
            'company_description': f"""
BUSINESS DESCRIPTION
This section outlines the nature of our business, our mission, and the value we provide to our customers and stakeholders.

MISSION STATEMENT
Our mission is to deliver exceptional value while contributing positively to the South African business landscape.

BUSINESS REGISTRATION
[To be completed - CIPC registration required for South African businesses]
B-BBEE Compliance: [To be determined based on business structure]

LEGAL STRUCTURE
Business Type: [To be specified]
Registration: [Pending completion]

Generated: {current_date}
            """,
            
            'market_analysis': f"""
MARKET OVERVIEW
South African market analysis and competitive landscape assessment.

TARGET MARKET
Primary and secondary target markets within South Africa.

COMPETITIVE ANALYSIS
Key competitors and our competitive advantages.

MARKET SIZE & OPPORTUNITY
Market size estimation and growth projections for the South African market.

Analysis Date: {current_date}
            """,
            
            'funding_request': f"""
FUNDING REQUIREMENTS
Total Funding Required: [To be specified in South African Rand (ZAR)]

FUNDING ALLOCATION
- Operations: [Percentage]%
- Equipment/Assets: [Percentage]%
- Marketing: [Percentage]%
- Working Capital: [Percentage]%

USE OF FUNDS
Detailed breakdown of how the requested funding will be utilized to support business growth.

Generated: {current_date}
            """,
            
            'financial_projections': f"""
FINANCIAL PROJECTIONS (SOUTH AFRICAN RAND - ZAR)

Year 1 Projections:
Revenue: R [Amount]
Expenses: R [Amount]
Net Profit: R [Amount]

Year 2 Projections:
Revenue: R [Amount]
Expenses: R [Amount]
Net Profit: R [Amount]

Year 3 Projections:
Revenue: R [Amount]
Expenses: R [Amount]
Net Profit: R [Amount]

Generated: {current_date}
            """
        }
        
        return templates.get(section_key, f"\n{section_title}\n\nThis section is currently being developed as part of the business proposal enhancement process. Additional details will be added based on the specific business requirements.\n\nGenerated: {current_date}")
    
    def _enhance_existing_section(self, section_key: str, content: str) -> str:
        """Enhance existing section content with additional details"""
        
        # Add South African context and formatting
        enhanced_content = content.strip()
        
        # Add section header if missing
        section_headers = {
            'executive_summary': 'EXECUTIVE SUMMARY',
            'company_description': 'COMPANY DESCRIPTION',
            'market_analysis': 'MARKET ANALYSIS',
            'organization_management': 'ORGANIZATION & MANAGEMENT',
            'service_product': 'PRODUCTS & SERVICES',
            'marketing_sales': 'MARKETING & SALES STRATEGY',
            'funding_request': 'FUNDING REQUEST',
            'financial_projections': 'FINANCIAL PROJECTIONS'
        }
        
        header = section_headers.get(section_key, 'SECTION')
        
        # Ensure proper formatting
        if not enhanced_content.upper().startswith(header):
            enhanced_content = f"{header}\n\n{enhanced_content}"
        
        # Add South African context for relevant sections
        if section_key == 'funding_request' and 'ZAR' not in enhanced_content.upper():
            enhanced_content += f"\n\nNote: All financial amounts should be specified in South African Rand (ZAR)."
        
        if section_key == 'company_description' and 'south africa' not in enhanced_content.lower():
            enhanced_content += f"\n\nBusiness Registration: This business operates within South Africa and will comply with all local regulations and CIPC requirements."
        
        return enhanced_content
    
    def _format_as_professional_proposal(self, enhanced_content: Dict[str, str]) -> str:
        """Format the enhanced content as a professional business proposal"""
        
        current_date = datetime.now().strftime("%B %d, %Y")
        
        # Create professional header
        proposal = f"""
BUSINESS PROPOSAL
Generated: {current_date}
Prepared for: Funding Application
Location: South Africa

{'='*60}

"""
        
        # Add sections in logical order
        section_order = [
            'executive_summary',
            'company_description', 
            'market_analysis',
            'service_product',
            'organization_management',
            'marketing_sales',
            'funding_request',
            'financial_projections'
        ]
        
        for section_key in section_order:
            if section_key in enhanced_content:
                proposal += f"\n{'-'*40}\n"
                proposal += f"{enhanced_content[section_key]}\n"
        
        # Add footer with South African context
        proposal += f"""

{'='*60}

PROPOSAL FOOTER
This business proposal has been enhanced and formatted for funding applications within South Africa.
Generated on: {current_date}
Location: South Africa

Note: This proposal contains enhanced content and formatting to ensure compliance with South African business standards and funding requirements.
"""
        
        return proposal.strip()
    
    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF files"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            return f"PDF extraction error: {str(e)}"
    
    def _extract_from_word(self, file_path: str) -> str:
        """Extract text from Word documents"""
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            return f"Word document extraction error: {str(e)}"
    
    def _extract_from_image(self, file_path: str) -> str:
        """Extract text from images using OCR"""
        try:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            return f"OCR extraction error: {str(e)}"
    
    def _extract_from_text(self, file_path: str) -> str:
        """Extract text from plain text files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            return f"Text file reading error: {str(e)}"
    
    def analyze_proposal(self, content: str) -> Dict[str, Any]:
        """Analyze business proposal content and provide feedback"""
        
        try:
            # Basic analysis metrics
            word_count = len(content.split())
            char_count = len(content)
            
            # Check for common business plan sections
            sections_found = self._identify_sections(content)
            
            # Calculate completeness score
            completeness_score = self._calculate_completeness(sections_found)
            
            # Generate feedback
            feedback = self._generate_feedback(content, sections_found, completeness_score)
            
            return {
                "score": completeness_score,
                "word_count": word_count,
                "character_count": char_count,
                "sections_found": sections_found,
                "feedback": feedback,
                "strengths": self._identify_strengths(content),
                "improvements": self._identify_improvements(content, sections_found)
            }
            
        except Exception as e:
            return {
                "score": 0,
                "error": f"Analysis error: {str(e)}",
                "feedback": {"error": "Unable to analyze document"}
            }
    
    def _identify_sections(self, content: str) -> List[str]:
        """Identify business plan sections in the content"""
        
        section_keywords = {
            'executive_summary': ['executive summary', 'summary', 'overview'],
            'company_description': ['company description', 'business description', 'about us'],
            'market_analysis': ['market analysis', 'market research', 'industry analysis'],
            'organization': ['organization', 'management', 'team', 'structure'],
            'products_services': ['product', 'service', 'offering', 'solution'],
            'marketing': ['marketing', 'sales', 'strategy', 'promotion'],
            'financial': ['financial', 'budget', 'projection', 'revenue', 'cost'],
            'funding': ['funding', 'investment', 'capital', 'loan', 'grant']
        }
        
        found_sections = []
        content_lower = content.lower()
        
        for section, keywords in section_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                found_sections.append(section)
        
        return found_sections
    
    def _calculate_completeness(self, sections_found: List[str]) -> float:
        """Calculate completeness score based on sections found"""
        
        total_sections = 8  # Expected number of sections
        found_count = len(sections_found)
        
        return min(100, (found_count / total_sections) * 100)
    
    def _generate_feedback(self, content: str, sections_found: List[str], score: float) -> Dict[str, str]:
        """Generate detailed feedback based on analysis"""
        
        feedback = {}
        
        # Overall score feedback
        if score >= 80:
            feedback['overall'] = "Excellent business plan with comprehensive coverage"
        elif score >= 60:
            feedback['overall'] = "Good business plan with most sections covered"
        elif score >= 40:
            feedback['overall'] = "Basic business plan with some sections missing"
        else:
            feedback['overall'] = "Incomplete business plan requiring significant additions"
        
        # Missing sections feedback
        expected_sections = ['executive_summary', 'company_description', 'market_analysis', 
                           'organization', 'products_services', 'marketing', 'financial', 'funding']
        missing_sections = [s for s in expected_sections if s not in sections_found]
        
        if missing_sections:
            feedback['missing_sections'] = f"Consider adding: {', '.join(missing_sections)}"
        
        return feedback
    
    def _identify_strengths(self, content: str) -> List[str]:
        """Identify strengths in the business plan"""
        
        strengths = []
        
        if len(content.split()) > 1000:
            strengths.append("Comprehensive content with good detail")
        
        if any(word in content.lower() for word in ['market', 'customer', 'target']):
            strengths.append("Market and customer focus evident")
        
        if any(word in content.lower() for word in ['revenue', 'profit', 'financial']):
            strengths.append("Financial considerations included")
        
        return strengths if strengths else ["Document structure is present"]
    
    def _identify_improvements(self, content: str, sections_found: List[str]) -> List[str]:
        """Identify areas for improvement"""
        
        improvements = []
        
        if len(content.split()) < 500:
            improvements.append("Expand content for better detail and comprehensiveness")
        
        if 'financial' not in sections_found:
            improvements.append("Add detailed financial projections and budget")
        
        if 'market_analysis' not in sections_found:
            improvements.append("Include thorough market analysis and competitive research")
        
        if len(sections_found) < 5:
            improvements.append("Add more business plan sections for completeness")
        
        return improvements


class FundingMatcher:
    """AI-powered funding source matching and recommendations"""
    
    def __init__(self):
        self.funding_sources = []
        self.load_sample_funding_sources()
    
    def load_sample_funding_sources(self):
        """Load sample funding sources (in production, this would come from database)"""
        
        self.funding_sources = [
            {
                "name": "National Empowerment Fund (NEF)",
                "description": "Funding for black-owned businesses in South Africa",
                "amount_range": "R 50,000 - R 150,000,000",
                "eligibility_criteria": ["Black ownership required", "South African registration", "B-BBEE compliance"],
                "industry_focus": ["Technology", "Manufacturing", "Agribusiness", "Tourism", "Education"],
                "contact_website": "https://www.nefcorp.co.za"
            },
            {
                "name": "IDC - Industrial Development Corporation",
                "description": "Development finance for industrial and manufacturing projects in South Africa",
                "amount_range": "R 500,000 - R 1,000,000,000",
                "eligibility_criteria": ["Business plan required", "Sustainable business model", "Job creation potential"],
                "industry_focus": ["Manufacturing", "Mining", "Infrastructure", "Energy", "Agro-processing"],
                "contact_website": "https://www.idc.co.za"
            },
            {
                "name": "Technology Innovation Agency (TIA)",
                "description": "Support for technology and innovation projects in South Africa",
                "amount_range": "R 100,000 - R 50,000,000",
                "eligibility_criteria": ["Technology focus", "Innovation required", "Commercial potential"],
                "industry_focus": ["Technology", "Innovation", "R&D", "Biotechnology", "ICT"],
                "contact_website": "https://www.tia.org.za"
            },
            {
                "name": "Small Enterprise Development Agency (SEDA)",
                "description": "Business development support and funding for small enterprises",
                "amount_range": "R 10,000 - R 5,000,000",
                "eligibility_criteria": ["Small business registration", "Business plan", "Growth potential"],
                "industry_focus": ["All sectors", "Small business", "Entrepreneurship", "Micro-enterprises"],
                "contact_website": "https://www.seda.org.za"
            },
            {
                "name": "Land Bank of South Africa",
                "description": "Agricultural and agribusiness finance solutions",
                "amount_range": "R 25,000 - R 500,000,000",
                "eligibility_criteria": ["Agriculture focus", "Farm ownership or lease", "Viable business plan"],
                "industry_focus": ["Agriculture", "Agribusiness", "Farming", "Food processing"],
                "contact_website": "https://www.landbank.co.za"
            }
        ]
    
    def get_recommendations(self, proposal_content: str) -> List[Dict[str, Any]]:
        """Get funding recommendations based on proposal content"""
        
        try:
            # Extract key information from proposal
            proposal_keywords = self._extract_proposal_keywords(proposal_content)
            
            # Match with funding sources
            recommendations = []
            
            for source in self.funding_sources:
                match_score = self._calculate_match_score(proposal_keywords, source)
                
                if match_score > 30:  # Minimum threshold for inclusion
                    recommendations.append({
                        "source": source,
                        "match_score": match_score,
                        "eligibility_status": self._determine_eligibility_status(match_score),
                        "rationale": self._generate_rationale(proposal_keywords, source, match_score)
                    })
            
            # Sort by match score (highest first)
            recommendations.sort(key=lambda x: x['match_score'], reverse=True)
            
            return recommendations[:5]  # Return top 5 matches
            
        except Exception as e:
            print(f"Funding matching error: {e}")
            return [{
                "error": f"Matching error: {str(e)}",
                "source": {"name": "System Error", "description": "Unable to process funding matching"}
            }]
    
    def _extract_proposal_keywords(self, content: str) -> Dict[str, Any]:
        """Extract relevant keywords and information from proposal"""
        
        content_lower = content.lower()
        
        keywords = {
            "industries": [],
            "business_type": "",
            "funding_amount": "",
            "ownership": "",
            "location": ""
        }
        
        # Extract industries
        industry_keywords = ['technology', 'manufacturing', 'agriculture', 'healthcare', 
                           'education', 'retail', 'finance', 'mining', 'infrastructure']
        for industry in industry_keywords:
            if industry in content_lower:
                keywords["industries"].append(industry)
        
        # Extract business type
        if any(word in content_lower for word in ['startup', 'small business', 'enterprise']):
            keywords["business_type"] = "startup"
        elif any(word in content_lower for word in ['corporation', 'company', 'business']):
            keywords["business_type"] = "established"
        
        # Extract ownership information
        if any(word in content_lower for word in ['black owned', 'black ownership', 'b-bbee']):
            keywords["ownership"] = "black"
        
        # Extract location
        if 'south africa' in content_lower or 'sa' in content_lower:
            keywords["location"] = "south_africa"
        
        return keywords
    
    def _calculate_match_score(self, proposal_keywords: Dict[str, Any], 
                             funding_source: Dict[str, Any]) -> float:
        """Calculate match score between proposal and funding source"""
        
        score = 0
        
        # Industry match (40 points)
        proposal_industries = proposal_keywords.get("industries", [])
        funding_industries = funding_source.get("industry_focus", [])
        
        industry_matches = len(set(proposal_industries) & set([ind.lower() for ind in funding_industries]))
        if funding_industries:
            score += (industry_matches / len(funding_industries)) * 40
        
        # Eligibility criteria match (30 points)
        eligibility_criteria = funding_source.get("eligibility_criteria", [])
        for criterion in eligibility_criteria:
            if self._check_criterion_match(proposal_keywords, criterion):
                score += 30 / len(eligibility_criteria)
        
        # Business type and location match (30 points)
        if proposal_keywords.get("business_type") and proposal_keywords.get("location"):
            score += 15
        
        # Ownership match for specific programs
        if proposal_keywords.get("ownership") == "black" and "black ownership" in str(eligibility_criteria).lower():
            score += 15
        
        return min(100, score)
    
    def _check_criterion_match(self, proposal_keywords: Dict[str, Any], criterion: str) -> bool:
        """Check if proposal meets a specific eligibility criterion"""
        
        criterion_lower = criterion.lower()
        
        if "business plan" in criterion_lower:
            return True  # Assume business plan exists if we're analyzing it
        
        if "black ownership" in criterion_lower and proposal_keywords.get("ownership") == "black":
            return True
        
        if "south africa" in criterion_lower and proposal_keywords.get("location") == "south_africa":
            return True
        
        return False
    
    def _determine_eligibility_status(self, match_score: float) -> str:
        """Determine eligibility status based on match score"""
        
        if match_score >= 70:
            return "eligible"
        elif match_score >= 40:
            return "partially_eligible"
        else:
            return "not_eligible"
    
    def _generate_rationale(self, proposal_keywords: Dict[str, Any], 
                          funding_source: Dict[str, Any], match_score: float) -> str:
        """Generate rationale for funding recommendation"""
        
        rationale_parts = []
        
        # Industry alignment
        proposal_industries = proposal_keywords.get("industries", [])
        funding_industries = funding_source.get("industry_focus", [])
        
        if proposal_industries and funding_industries:
            common_industries = set(proposal_industries) & set([ind.lower() for ind in funding_industries])
            if common_industries:
                rationale_parts.append(f"Business operates in {', '.join(common_industries)} which aligns with funder's focus areas.")
        
        # Eligibility
        eligibility_criteria = funding_source.get("eligibility_criteria", [])
        for criterion in eligibility_criteria:
            if self._check_criterion_match(proposal_keywords, criterion):
                rationale_parts.append(f"Meets criterion: {criterion}")
        
        # Score-based rationale
        if match_score >= 70:
            rationale_parts.append("Strong match with funding requirements.")
        elif match_score >= 40:
            rationale_parts.append("Moderate match - some requirements may need attention.")
        
        return " ".join(rationale_parts) if rationale_parts else "Standard business funding consideration."


class PDFGenerator:
    """Generate professional PDF documents for business proposals"""
    
    def __init__(self):
        self.use_reportlab = self._check_reportlab_availability()
    
    def _check_reportlab_availability(self):
        """Check if reportlab is available for PDF generation"""
        try:
            import reportlab
            return True
        except ImportError:
            print("ReportLab not available. Using HTML-to-PDF fallback.")
            return False
    
    def generate_proposal_pdf(self, title: str, business_plan: Dict[str, Any], created_date) -> bytes:
        """Generate a professional PDF from business plan data with enhanced formatting and diagrams"""
        
        # Handle both dictionary and string content
        if isinstance(business_plan, str):
            # If content is string (enhanced proposal), parse it
            business_plan = self._parse_enhanced_proposal_content(business_plan)
        
        if self.use_reportlab:
            return self._generate_with_reportlab(title, business_plan, created_date)
        else:
            return self._generate_html_fallback(title, business_plan, created_date)
    
    def _parse_enhanced_proposal_content(self, content: str) -> Dict[str, Any]:
        """Parse enhanced proposal content into structured sections"""
        
        sections = {}
        
        # Define section patterns for enhanced proposals
        section_patterns = {
            'executive_summary': r'(?i)executive\s+summary|summary.*?',
            'company_description': r'(?i)company\s+description|business\s+description.*?',
            'market_analysis': r'(?i)market\s+analysis|market\s+overview.*?',
            'organization_management': r'(?i)organization.*?management|management.*?',
            'service_product': r'(?i)products.*?services|service.*?product.*?',
            'marketing_sales': r'(?i)marketing.*?sales|sales.*?strategy.*?',
            'funding_request': r'(?i)funding\s+request|funding\s+requirements.*?',
            'financial_projections': r'(?i)financial\s+projections|financial.*?'
        }
        
        # Split content into sections
        for section_name, pattern in section_patterns.items():
            match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            if match:
                start_pos = match.start()
                # Find the end of this section
                remaining_text = content[start_pos:]
                
                # Look for next section header
                next_section_pos = len(remaining_text)
                for other_name, other_pattern in section_patterns.items():
                    if other_name != section_name:
                        next_match = re.search(other_pattern, remaining_text[50:], re.IGNORECASE)
                        if next_match:
                            next_section_pos = min(next_section_pos, 50 + next_match.start())
                
                section_content = remaining_text[:next_section_pos].strip()
                if section_content:
                    sections[section_name] = section_content
        
        # If no sections found, return as content
        if not sections:
            sections['content'] = content
        
        return sections
    
    def _generate_with_reportlab(self, title: str, business_plan: Dict[str, Any], created_date) -> bytes:
        """Generate PDF using ReportLab library"""
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
            from reportlab.platypus.tableofcontents import TableOfContents
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors
            from io import BytesIO
            
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, 
                                  topMargin=72, bottomMargin=18)
            
            # Get styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                textColor=colors.darkblue,
                alignment=1  # Center alignment
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=16,
                spaceAfter=12,
                spaceBefore=20,
                textColor=colors.darkblue
            )
            
            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontSize=11,
                spaceAfter=12,
                leftIndent=20
            )
            
            # Build content
            story = []
            
            # Title page
            story.append(Paragraph("BUSINESS PROPOSAL", title_style))
            story.append(Spacer(1, 20))
            story.append(Paragraph(f"<b>{title}</b>", title_style))
            story.append(Spacer(1, 40))
            
            # Date and location
            date_str = created_date.strftime("%B %d, %Y") if created_date else datetime.now().strftime("%B %d, %Y")
            story.append(Paragraph(f"<b>Generated:</b> {date_str}", normal_style))
            story.append(Paragraph("<b>Location:</b> South Africa", normal_style))
            story.append(PageBreak())
            
            # Business plan sections
            sections = [
                ("executive_summary", "EXECUTIVE SUMMARY"),
                ("company_description", "COMPANY DESCRIPTION"),
                ("market_analysis", "MARKET ANALYSIS"),
                ("organization_management", "ORGANIZATION & MANAGEMENT"),
                ("service_product", "PRODUCTS & SERVICES"),
                ("marketing_sales", "MARKETING & SALES STRATEGY"),
                ("funding_request", "FUNDING REQUEST"),
                ("financial_projections", "FINANCIAL PROJECTIONS")
            ]
            
            for section_key, section_title in sections:
                if section_key in business_plan and business_plan[section_key]:
                    content = business_plan[section_key]
                    
                    # Clean and format content
                    if isinstance(content, str):
                        # Escape HTML and format text
                        content = content.replace('\n', '<br/>')
                        content = content.replace('&', '&amp;')
                        content = content.replace('<', '&lt;').replace('>', '&gt;')
                        
                        story.append(Paragraph(f"<b>{section_title}</b>", heading_style))
                        story.append(Paragraph(content, normal_style))
                        story.append(Spacer(1, 20))
            
            # Build PDF
            doc.build(story)
            buffer.seek(0)
            return buffer.getvalue()
            
        except Exception as e:
            print(f"ReportLab PDF generation error: {e}")
            return self._generate_html_fallback(title, business_plan, created_date)
    
    def _generate_html_fallback(self, title: str, business_plan: Dict[str, Any], created_date) -> bytes:
        """Generate HTML content that can be printed to PDF"""
        
        date_str = created_date.strftime("%B %d, %Y") if created_date else datetime.now().strftime("%B %d, %Y")
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title} - Business Proposal</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    margin: 40px;
                    color: #333;
                    max-width: 800px;
                    margin: 40px auto;
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 40px;
                    padding-bottom: 20px;
                    border-bottom: 3px solid #0066cc;
                }}
                .title {{
                    font-size: 28px;
                    font-weight: bold;
                    color: #0066cc;
                    margin-bottom: 10px;
                }}
                .subtitle {{
                    font-size: 18px;
                    color: #666;
                    margin-bottom: 20px;
                }}
                .date-info {{
                    font-size: 14px;
                    color: #888;
                    margin-bottom: 30px;
                }}
                .section {{
                    margin-bottom: 30px;
                    page-break-inside: avoid;
                }}
                .section-title {{
                    font-size: 18px;
                    font-weight: bold;
                    color: #0066cc;
                    margin-bottom: 15px;
                    padding-bottom: 5px;
                    border-bottom: 2px solid #0066cc;
                }}
                .content {{
                    font-size: 12px;
                    line-height: 1.8;
                    text-align: justify;
                    white-space: pre-wrap;
                }}
                .footer {{
                    margin-top: 50px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                    font-size: 10px;
                    color: #888;
                    text-align: center;
                }}
                @media print {{
                    body {{ margin: 20px; }}
                    .section {{ page-break-inside: avoid; }}
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="title">BUSINESS PROPOSAL</div>
                <div class="subtitle">{title}</div>
                <div class="date-info">
                    <strong>Generated:</strong> {date_str}<br/>
                    <strong>Location:</strong> South Africa
                </div>
            </div>
        """
        
        # Add business plan sections
        sections = [
            ("executive_summary", "EXECUTIVE SUMMARY"),
            ("company_description", "COMPANY DESCRIPTION"),
            ("market_analysis", "MARKET ANALYSIS"),
            ("organization_management", "ORGANIZATION & MANAGEMENT"),
            ("service_product", "PRODUCTS & SERVICES"),
            ("marketing_sales", "MARKETING & SALES STRATEGY"),
            ("funding_request", "FUNDING REQUEST"),
            ("financial_projections", "FINANCIAL PROJECTIONS")
        ]
        
        for section_key, section_title in sections:
            if section_key in business_plan and business_plan[section_key]:
                content = business_plan[section_key]
                if isinstance(content, str):
                    # Clean content for HTML
                    content = content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    
                    html_content += f"""
                    <div class="section">
                        <div class="section-title">{section_title}</div>
                        <div class="content">{content}</div>
                    </div>
                    """
        
        html_content += """
            <div class="footer">
                <p>This business proposal was generated by the AI-Powered Business Proposal Generator for South African entrepreneurs.</p>
                <p>For more information, visit your business dashboard or contact support.</p>
            </div>
        </body>
        </html>
        """
        
        return html_content.encode('utf-8')
