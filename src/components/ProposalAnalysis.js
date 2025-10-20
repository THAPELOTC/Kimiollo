import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  Button,
  LinearProgress,
  Chip,
  Alert,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  AccordionActions,
} from '@mui/material';
import {
  Assessment,
  TrendingUp,
  CheckCircle,
  Warning,
  Error,
  GetApp,
  Visibility,
  Description,
  ExpandMore,
  ExpandLess,
} from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';

const ProposalAnalysis = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [proposal, setProposal] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [businessPlanContent, setBusinessPlanContent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [showBusinessPlan, setShowBusinessPlan] = useState(false);
  const { token, logout } = useAuth();

  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

  useEffect(() => {
    if (token) {
      fetchProposalData();
    }
  }, [id, token]);

  const fetchProposalData = async () => {
    try {
      if (!token) {
        toast.error('Authentication required');
        navigate('/login');
        return;
      }

      const response = await axios.get(`${API_BASE_URL}/user-proposals`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      const userProposals = response.data.proposals || [];
      const currentProposal = userProposals.find(p => p.id === parseInt(id));
      
      if (currentProposal) {
        setProposal(currentProposal);
        
        // If proposal is already analyzed, we might need to fetch analysis details
        if (currentProposal.status === 'analyzed') {
          // Try to get analysis data - you might need to create this endpoint
          // For now, we'll simulate the analysis based on the score
          setAnalysis({
            score: currentProposal.score,
            status: currentProposal.status,
          });
        }
        
        // Fetch business plan content
        fetchBusinessPlanContent(parseInt(id));
      } else {
        toast.error('Proposal not found');
        navigate('/dashboard');
      }
    } catch (error) {
      console.log('Fetch proposal data error:', error.response?.data);
      
      // Handle authentication errors
      if (error.response?.status === 401) {
        toast.error('Session expired. Please login again.');
        logout();
        navigate('/login');
        return;
      }
      
      toast.error('Failed to fetch proposal data');
      navigate('/dashboard');
    } finally {
      setLoading(false);
    }
  };

  const fetchBusinessPlanContent = async (proposalId) => {
    try {
      if (!token) {
        return;
      }

      const response = await axios.get(`${API_BASE_URL}/proposal-content/${proposalId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      setBusinessPlanContent(response.data.business_plan);
    } catch (error) {
      console.log('Fetch business plan content error:', error.response?.data);
    }
  };

  const analyzeProposal = async () => {
    setAnalyzing(true);
    try {
      if (!token) {
        toast.error('Authentication required');
        return;
      }

      const response = await axios.post(`${API_BASE_URL}/analyze-proposal/${id}`, {}, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      setAnalysis(response.data.analysis);
      toast.success('Proposal analyzed successfully!');
      // Refresh proposal data
      fetchProposalData();
    } catch (error) {
      // Handle authentication errors
      if (error.response?.status === 401) {
        toast.error('Session expired. Please login again.');
        logout();
        navigate('/login');
        return;
      }
      
      toast.error(error.response?.data?.error || 'Failed to analyze proposal');
    } finally {
      setAnalyzing(false);
    }
  };

  const downloadProposalPDF = async () => {
    try {
      if (!token) {
        toast.error('Authentication required');
        return;
      }

      const response = await axios.get(`${API_BASE_URL}/download-proposal/${id}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        },
        responseType: 'blob'
      });

      // Check content type to determine file type
      const contentType = response.headers['content-type'];
      const isHTML = contentType && contentType.includes('text/html');
      
      // Create blob with proper MIME type
      const blob = new Blob([response.data], { 
        type: isHTML ? 'text/html' : 'application/pdf' 
      });
      
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      
      // Extract filename from response headers or use default
      const contentDisposition = response.headers['content-disposition'];
      let filename = `${proposal.title}_Business_Proposal.${isHTML ? 'html' : 'pdf'}`;
      
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
        if (filenameMatch && filenameMatch[1]) {
          filename = filenameMatch[1].replace(/['"]/g, '');
        }
      }
      
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      toast.success('Business proposal downloaded successfully!');
    } catch (error) {
      console.log('Download error:', error.response?.data);
      
      // Handle authentication errors
      if (error.response?.status === 401) {
        toast.error('Session expired. Please login again.');
        logout();
        navigate('/login');
        return;
      }
      
      toast.error(error.response?.data?.error || 'Failed to download proposal');
    }
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'success';
    if (score >= 60) return 'info';
    if (score >= 40) return 'warning';
    return 'error';
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
      case 'analyzed':
        return <CheckCircle color="success" />;
      case 'processing':
        return <Assessment color="info" />;
      default:
        return <Warning color="warning" />;
    }
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <LinearProgress />
        <Typography>Loading proposal...</Typography>
      </Container>
    );
  }

  if (!proposal) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error">Proposal not found</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" component="h1">
            Proposal Analysis
          </Typography>
          <Box sx={{ display: 'flex', gap: 2 }}>
            {proposal.status !== 'analyzed' && (
              <Button
                variant="contained"
                startIcon={<Assessment />}
                onClick={analyzeProposal}
                disabled={analyzing}
              >
                {analyzing ? 'Analyzing...' : 'Analyze Proposal'}
              </Button>
            )}
            <Button
              variant="outlined"
              startIcon={<Visibility />}
              onClick={() => navigate('/dashboard')}
            >
              Back to Dashboard
            </Button>
          </Box>
        </Box>

        {/* Proposal Overview */}
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              {proposal.title}
            </Typography>
            <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
              <Chip
                label={proposal.type}
                size="small"
                variant="outlined"
              />
              <Chip
                label={proposal.status}
                size="small"
                color="primary"
              />
              <Chip
                icon={getStatusIcon(proposal.status)}
                label={`Created: ${new Date(proposal.created_at).toLocaleDateString()}`}
                size="small"
                variant="outlined"
              />
            </Box>
          </CardContent>
        </Card>

        {/* Analysis Results */}
        {analysis && (
          <Grid container spacing={3}>
            {/* Score Overview */}
            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Overall Score
                  </Typography>
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography
                      variant="h2"
                      color={`${getScoreColor(analysis.score)}.main`}
                      sx={{ fontWeight: 'bold' }}
                    >
                      {Math.round(analysis.score || 0)}%
                    </Typography>
                    <LinearProgress
                      variant="determinate"
                      value={analysis.score || 0}
                      color={getScoreColor(analysis.score)}
                      sx={{ mt: 2, height: 8, borderRadius: 4 }}
                    />
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            {/* Analysis Details */}
            <Grid item xs={12} md={8}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Analysis Overview
                  </Typography>
                  
                  {analysis.feedback && (
                    <Box sx={{ mb: 3 }}>
                      <Typography variant="subtitle2" gutterBottom>
                        Feedback:
                      </Typography>
                      <Alert severity="info">
                        {analysis.feedback.overall || 'Analysis completed successfully'}
                      </Alert>
                    </Box>
                  )}

                  {analysis.strengths && analysis.strengths.length > 0 && (
                    <Box sx={{ mb: 3 }}>
                      <Typography variant="subtitle2" gutterBottom>
                        Strengths:
                      </Typography>
                      <List dense>
                        {analysis.strengths.map((strength, index) => (
                          <ListItem key={index}>
                            <ListItemIcon>
                              <CheckCircle color="success" />
                            </ListItemIcon>
                            <ListItemText primary={strength} />
                          </ListItem>
                        ))}
                      </List>
                    </Box>
                  )}

                  <Divider sx={{ my: 2 }} />

                  {analysis.improvements && analysis.improvements.length > 0 && (
                    <Box>
                      <Typography variant="subtitle2" gutterBottom>
                        Areas for Improvement:
                      </Typography>
                      <List dense>
                        {analysis.improvements.map((improvement, index) => (
                          <ListItem key={index}>
                            <ListItemIcon>
                              <Warning color="warning" />
                            </ListItemIcon>
                            <ListItemText primary={improvement} />
                          </ListItem>
                        ))}
                      </List>
                    </Box>
                  )}
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}

        {/* Business Plan Content */}
        {businessPlanContent && (
          <Card sx={{ mt: 3 }}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6" gutterBottom>
                  Business Plan Content
                </Typography>
                <Button
                  variant="outlined"
                  startIcon={showBusinessPlan ? <ExpandLess /> : <ExpandMore />}
                  onClick={() => setShowBusinessPlan(!showBusinessPlan)}
                >
                  {showBusinessPlan ? 'Hide Content' : 'View Business Plan'}
                </Button>
              </Box>
              
              {showBusinessPlan && (
                <Box>
                  {typeof businessPlanContent === 'object' ? (
                    <Box>
                      {Object.entries(businessPlanContent).map(([sectionKey, content]) => (
                        <Accordion key={sectionKey} sx={{ mb: 2 }}>
                          <AccordionSummary expandIcon={<ExpandMore />}>
                            <Typography variant="h6" sx={{ textTransform: 'capitalize' }}>
                              {sectionKey.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                            </Typography>
                          </AccordionSummary>
                          <AccordionDetails>
                            <Typography
                              variant="body2"
                              sx={{ 
                                whiteSpace: 'pre-wrap',
                                lineHeight: 1.6,
                                maxHeight: '400px',
                                overflow: 'auto'
                              }}
                            >
                              {content}
                            </Typography>
                          </AccordionDetails>
                        </Accordion>
                      ))}
                    </Box>
                  ) : (
                    <Typography
                      variant="body2"
                      sx={{ 
                        whiteSpace: 'pre-wrap',
                        lineHeight: 1.6,
                        maxHeight: '400px',
                        overflow: 'auto',
                        p: 2,
                        backgroundColor: 'grey.50',
                        borderRadius: 1
                      }}
                    >
                      {businessPlanContent}
                    </Typography>
                  )}
                </Box>
              )}
            </CardContent>
          </Card>
        )}

        {/* Action Buttons */}
        <Box sx={{ display: 'flex', gap: 2, mt: 4, justifyContent: 'center' }}>
          {proposal.status === 'analyzed' && (
            <Button
              variant="contained"
              startIcon={<TrendingUp />}
              onClick={() => navigate(`/funding/${id}`)}
              size="large"
            >
              View Funding Recommendations
            </Button>
          )}
          <Button
            variant="contained"
            startIcon={<GetApp />}
            onClick={downloadProposalPDF}
            disabled={!proposal}
            size="large"
            color="secondary"
          >
            Download Business Proposal PDF
          </Button>
        </Box>
      </Paper>
    </Container>
  );
};

export default ProposalAnalysis;
