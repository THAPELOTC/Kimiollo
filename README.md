# AI-Powered Business Proposal Generator & Funding Finder

A comprehensive web application that helps entrepreneurs and small business owners create professional business proposals and find suitable funding sources using AI technology.

## Features

### Core Functionality (FR1-FR7)
- **FR1**: User Authentication & Profile Management
- **FR2**: Guided Business Plan Generation through AI-powered questionnaires
- **FR3**: Document Upload & Refinement (PDF/Word/Images with OCR)
- **FR4**: Proposal Analysis & Scoring with detailed feedback
- **FR5**: AI-powered Funding Recommendations
- **FR6**: Professional PDF Export
- **FR7**: Admin Management Interface

## Technology Stack

### Backend (Python/Flask)
- Flask web framework
- SQLAlchemy for database management
- JWT authentication
- OCR processing (Tesseract)
- Document processing (PyPDF2, python-docx)
- AI/ML integration (OpenAI API, scikit-learn)

### Frontend (React)
- React 18 with Material-UI
- React Router for navigation
- Axios for API calls
- React Hook Form for form management
- Styled Components

### Database
- SQLite (development) / PostgreSQL (production)
- User management
- Business proposal storage
- Funding source database

## Installation & Setup

### Backend Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install system dependencies for OCR:**
   ```bash
   # For Windows (using Chocolatey)
   choco install tesseract
   
   # For Ubuntu/Debian
   sudo apt-get install tesseract-ocr
   
   # For macOS
   brew install tesseract
   ```

3. **Set up environment variables:**
   Create a `.env` file:
   ```
   SECRET_KEY=your-secret-key
   JWT_SECRET_KEY=your-jwt-secret
   OPENAI_API_KEY=your-openai-api-key
   DATABASE_URL=sqlite:///business_proposal.db
   ```

4. **Run the Flask application:**
   ```bash
   python app.py
   ```
   The backend will run on `http://localhost:5000`

### Frontend Setup

1. **Install Node.js dependencies:**
   ```bash
   npm install
   ```

2. **Set up environment variables:**
   Create a `.env` file in the root directory:
   ```
   REACT_APP_API_URL=http://localhost:5000/api
   ```

3. **Start the React development server:**
   ```bash
   npm start
   ```
   The frontend will run on `http://localhost:3000`

## API Endpoints

### Authentication
- `POST /api/register` - User registration
- `POST /api/login` - User login

### Business Plans
- `POST /api/generate-business-plan` - Generate AI business plan
- `POST /api/upload-proposal` - Upload document for analysis
- `POST /api/analyze-proposal/<id>` - Analyze uploaded proposal
- `GET /api/user-proposals` - Get user's proposals

### Funding
- `GET /api/funding-recommendations/<id>` - Get funding recommendations

## Usage

1. **Register/Login**: Create an account or login to access the platform
2. **Generate Business Plan**: Complete a guided questionnaire to generate a comprehensive business plan
3. **Upload Existing Proposal**: Upload PDF, Word, or image documents for AI analysis
4. **Review Analysis**: Get detailed feedback and scoring on your proposal
5. **Find Funding**: Receive personalized funding recommendations based on your business profile

## Project Structure

```
kimiollo/
├── app.py                 # Flask backend application
├── models.py              # Database models
├── services.py            # AI and processing services
├── requirements.txt       # Python dependencies
├── package.json           # Node.js dependencies
├── src/                   # React frontend source
│   ├── components/        # React components
│   ├── contexts/          # React contexts (Auth)
│   └── App.js            # Main React app
├── public/               # Static assets
└── uploads/              # File upload directory
```

## Development Status

- ✅ Backend API structure
- ✅ Database models
- ✅ AI services (Business plan generation, Document processing, Funding matching)
- ✅ Frontend authentication
- ✅ Dashboard interface
- 🔄 Business plan generator UI
- 🔄 Document upload interface
- 🔄 Analysis results display
- 🔄 Funding recommendations UI

## Contributing

This project was developed as part of ISJ107V - Assignment 1, 2025 by Hlakola K.

## Deployment

### GitHub Pages (Frontend Only)
This repository is configured for automatic deployment to GitHub Pages.

1. **Set up GitHub repository:**
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/kimiollo.git
   git branch -M main
   git push -u origin main
   ```

2. **Enable GitHub Pages:**
   - Go to repository Settings → Pages
   - Source: "GitHub Actions"
   - Your site will be available at: `https://YOUR_USERNAME.github.io/kimiollo`

3. **Configure API URL:**
   - Go to repository Settings → Secrets → Actions
   - Add secret named "API_URL" with your backend API URL

### Full Stack Deployment
For complete functionality, deploy both frontend and backend:

**Backend Options:**
- Heroku (free tier available)
- Railway
- Render
- Python Anywhere

**Frontend:** GitHub Pages (this repository)

## Live Demo
- Frontend: https://thapelo01.github.io/kimiollo
- Backend: (Deploy separately using options above)

## License

This project is for educational purposes as part of the university assignment.
