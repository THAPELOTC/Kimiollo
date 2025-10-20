import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Box,
  Chip,
  IconButton,
  Fab,
} from '@mui/material';
import {
  Add,
  Description,
  TrendingUp,
  Assessment,
  Visibility,
  GetApp,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';

const Dashboard = () => {
  const navigate = useNavigate();
  const [proposals, setProposals] = useState([]);
  const [loading, setLoading] = useState(true);
  const { token, logout } = useAuth();

  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

  useEffect(() => {
    if (token) {
      fetchProposals();
    }
  }, [token]);

  const fetchProposals = async () => {
    try {
      if (!token) {
        toast.error('Authentication required');
        return;
      }

      const response = await axios.get(`${API_BASE_URL}/user-proposals`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      setProposals(response.data.proposals || []);
    } catch (error) {
      console.log('Fetch proposals error:', error.response?.data);
      
      // Handle authentication errors
      if (error.response?.status === 401) {
        toast.error('Session expired. Please login again.');
        logout();
        navigate('/login');
        return;
      }
      
      toast.error('Failed to fetch proposals');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'analyzed':
        return 'info';
      case 'processing':
        return 'warning';
      default:
        return 'default';
    }
  };

  const getTypeIcon = (type) => {
    return type === 'generated' ? <Description /> : <Assessment />;
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  const downloadProposalPDF = async (proposalId, proposalTitle) => {
    try {
      if (!token) {
        toast.error('Authentication required');
        return;
      }

      const response = await axios.get(`${API_BASE_URL}/download-proposal/${proposalId}`, {
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
      let filename = `${proposalTitle}_Business_Proposal.${isHTML ? 'html' : 'pdf'}`;
      
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

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography variant="h4" component="h1">
          Dashboard
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="outlined"
            startIcon={<Description />}
            onClick={() => navigate('/generate-plan')}
          >
            Generate Plan
          </Button>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => navigate('/upload-proposal')}
          >
            Upload Proposal
          </Button>
        </Box>
      </Box>

      {loading ? (
        <Typography>Loading your proposals...</Typography>
      ) : proposals.length === 0 ? (
        <Card>
          <CardContent sx={{ textAlign: 'center', py: 8 }}>
            <Description sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h5" gutterBottom>
              No Proposals Yet
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
              Get started by generating a new business plan or uploading an existing proposal.
            </Typography>
            <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
              <Button
                variant="contained"
                startIcon={<Description />}
                onClick={() => navigate('/generate-plan')}
              >
                Generate New Plan
              </Button>
              <Button
                variant="outlined"
                startIcon={<Add />}
                onClick={() => navigate('/upload-proposal')}
              >
                Upload Proposal
              </Button>
            </Box>
          </CardContent>
        </Card>
      ) : (
        <Grid container spacing={3}>
          {proposals.map((proposal) => (
            <Grid item xs={12} md={6} lg={4} key={proposal.id}>
              <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                <CardContent sx={{ flexGrow: 1 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    {getTypeIcon(proposal.type)}
                    <Typography variant="h6" component="h2" sx={{ ml: 1, flexGrow: 1 }}>
                      {proposal.title}
                    </Typography>
                  </Box>
                  
                  <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                    <Chip
                      label={proposal.type}
                      size="small"
                      variant="outlined"
                    />
                    <Chip
                      label={proposal.status}
                      size="small"
                      color={getStatusColor(proposal.status)}
                    />
                    {proposal.score && (
                      <Chip
                        label={`Score: ${Math.round(proposal.score)}%`}
                        size="small"
                        color="primary"
                        variant="outlined"
                      />
                    )}
                  </Box>

                  <Typography variant="body2" color="text.secondary">
                    Created: {formatDate(proposal.created_at)}
                  </Typography>
                </CardContent>

                <CardActions>
                  <Button
                    size="small"
                    startIcon={<Visibility />}
                    onClick={() => navigate(`/analyze/${proposal.id}`)}
                  >
                    View Details
                  </Button>
                  <Button
                    size="small"
                    startIcon={<TrendingUp />}
                    onClick={() => navigate(`/funding/${proposal.id}`)}
                    disabled={proposal.status !== 'analyzed' && proposal.status !== 'completed'}
                  >
                    Funding
                  </Button>
                  <Button
                    size="small"
                    startIcon={<GetApp />}
                    onClick={() => downloadProposalPDF(proposal.id, proposal.title)}
                    disabled={!proposal}
                  >
                    Download PDF
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Floating Action Button */}
      <Fab
        color="primary"
        aria-label="add"
        sx={{ position: 'fixed', bottom: 16, right: 16 }}
        onClick={() => navigate('/generate-plan')}
      >
        <Add />
      </Fab>
    </Container>
  );
};

export default Dashboard;
