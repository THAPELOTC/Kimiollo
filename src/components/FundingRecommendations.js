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
  Chip,
  Alert,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Link,
} from '@mui/material';
import {
  TrendingUp,
  CheckCircle,
  Warning,
  Error,
  OpenInNew,
  Business,
  AttachMoney,
  Schedule,
  Search,
} from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';

const FundingRecommendations = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searching, setSearching] = useState(false);
  const [searchResults, setSearchResults] = useState([]);
  const [proposalData, setProposalData] = useState(null);
  const { token, logout } = useAuth();

  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

  useEffect(() => {
    fetchRecommendations();
  }, [id]);

  const fetchRecommendations = async () => {
    try {
      if (!token) {
        toast.error('Authentication required');
        navigate('/login');
        return;
      }

      const response = await axios.get(`${API_BASE_URL}/funding-recommendations/${id}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      setRecommendations(response.data.recommendations || []);

      // Also fetch proposal data for search parameters
      await fetchProposalData();
    } catch (error) {
      console.log('Fetch recommendations error:', error.response?.data);
      
      if (error.response?.status === 401) {
        toast.error('Session expired. Please login again.');
        logout();
        navigate('/login');
        return;
      }
      
      toast.error(error.response?.data?.error || 'Failed to fetch funding recommendations');
    } finally {
      setLoading(false);
    }
  };

  const fetchProposalData = async () => {
    try {
      if (!token) return;

      const response = await axios.get(`${API_BASE_URL}/user-proposals`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      // Find the specific proposal
      const proposal = response.data.proposals.find(p => p.id === parseInt(id));
      if (proposal) {
        setProposalData(proposal);
      }
    } catch (error) {
      console.log('Fetch proposal data error:', error.response?.data);
    }
  };

  const searchFundersRealtime = async () => {
    setSearching(true);
    try {
      if (!token) {
        toast.error('Authentication required');
        navigate('/login');
        return;
      }

      // Send proposal ID to backend for extraction
      const searchParams = {
        proposal_id: parseInt(id)  // Use the proposal ID from URL params
      };

      const response = await axios.post(`${API_BASE_URL}/search-funders`, searchParams, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      setSearchResults(response.data.funders || []);
      toast.success(`Found ${response.data.total_found} additional funding opportunities!`);
      
    } catch (error) {
      console.log('Real-time search error:', error.response?.data);
      
      if (error.response?.status === 401) {
        toast.error('Session expired. Please login again.');
        logout();
        navigate('/login');
        return;
      }
      
      toast.error(error.response?.data?.error || 'Failed to search for funders');
    } finally {
      setSearching(false);
    }
  };

  const getEligibilityColor = (status) => {
    switch (status) {
      case 'eligible':
        return 'success';
      case 'partially_eligible':
        return 'warning';
      case 'not_eligible':
        return 'error';
      default:
        return 'default';
    }
  };

  const getEligibilityIcon = (status) => {
    switch (status) {
      case 'eligible':
        return <CheckCircle />;
      case 'partially_eligible':
        return <Warning />;
      case 'not_eligible':
        return <Error />;
      default:
        return <Warning />;
    }
  };

  const formatCurrency = (range) => {
    if (!range) return 'Contact for details';
    return range;
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'No deadline specified';
    return new Date(dateString).toLocaleDateString();
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <LinearProgress />
        <Typography>Loading funding recommendations...</Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" component="h1">
            Funding Recommendations
          </Typography>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button
              variant="contained"
              startIcon={<Search />}
              onClick={searchFundersRealtime}
              disabled={searching}
              color="primary"
            >
              {searching ? 'Searching...' : 'Search Real-time Funders'}
            </Button>
            <Button
              variant="outlined"
              onClick={() => navigate('/dashboard')}
            >
              Back to Dashboard
            </Button>
          </Box>
        </Box>

        {recommendations.length === 0 ? (
          <Alert severity="info">
            No funding recommendations found for this proposal. This could be due to incomplete proposal analysis or no matching funding sources in our database.
          </Alert>
        ) : (
          <>
            <Typography variant="body1" color="text.secondary" paragraph>
              Based on your business proposal analysis, we've found {recommendations.length} funding opportunity(ies) that match your business profile.
            </Typography>

            <Grid container spacing={3}>
              {recommendations.map((rec, index) => (
                <Grid item xs={12} key={index}>
                  <Card sx={{ mb: 2 }}>
                    <CardContent>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                        <Box>
                          <Typography variant="h6" gutterBottom>
                            {rec.source?.name || 'Funding Source'}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            {rec.source?.description || 'No description available'}
                          </Typography>
                        </Box>
                        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 1 }}>
                          <Chip
                            icon={getEligibilityIcon(rec.eligibility_status)}
                            label={rec.eligibility_status?.replace('_', ' ').toUpperCase()}
                            color={getEligibilityColor(rec.eligibility_status)}
                            size="small"
                          />
                          {rec.match_score && (
                            <Typography variant="body2" color="text.secondary">
                              Match Score: {Math.round(rec.match_score)}%
                            </Typography>
                          )}
                        </Box>
                      </Box>

                      <Grid container spacing={2} sx={{ mb: 2 }}>
                        <Grid item xs={12} sm={6} md={3}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <AttachMoney color="primary" />
                            <Box>
                              <Typography variant="caption" color="text.secondary">
                                Amount Range
                              </Typography>
                              <Typography variant="body2">
                                {formatCurrency(rec.source?.amount_range)}
                              </Typography>
                            </Box>
                          </Box>
                        </Grid>

                        <Grid item xs={12} sm={6} md={3}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Schedule color="primary" />
                            <Box>
                              <Typography variant="caption" color="text.secondary">
                                Deadline
                              </Typography>
                              <Typography variant="body2">
                                {formatDate(rec.source?.application_deadline)}
                              </Typography>
                            </Box>
                          </Box>
                        </Grid>

                        <Grid item xs={12} sm={6} md={3}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Business color="primary" />
                            <Box>
                              <Typography variant="caption" color="text.secondary">
                                Industries
                              </Typography>
                              <Typography variant="body2">
                                {rec.source?.industry_focus?.join(', ') || 'Various'}
                              </Typography>
                            </Box>
                          </Box>
                        </Grid>
                      </Grid>

                      {rec.rationale && (
                        <Box sx={{ mb: 2 }}>
                          <Typography variant="subtitle2" gutterBottom>
                            Why This Match:
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            {rec.rationale}
                          </Typography>
                        </Box>
                      )}

                      {rec.source?.eligibility_criteria && rec.source.eligibility_criteria.length > 0 && (
                        <Box sx={{ mb: 2 }}>
                          <Typography variant="subtitle2" gutterBottom>
                            Eligibility Criteria:
                          </Typography>
                          <List dense>
                            {rec.source.eligibility_criteria.map((criterion, idx) => (
                              <ListItem key={idx} sx={{ py: 0 }}>
                                <ListItemIcon>
                                  <CheckCircle color="success" fontSize="small" />
                                </ListItemIcon>
                                <ListItemText primary={criterion} />
                              </ListItem>
                            ))}
                          </List>
                        </Box>
                      )}

                      <Divider sx={{ my: 2 }} />

                      <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
                        {rec.source?.contact_website && (
                          <Button
                            variant="outlined"
                            endIcon={<OpenInNew />}
                            href={rec.source.contact_website}
                            target="_blank"
                            rel="noopener noreferrer"
                          >
                            Visit Website
                          </Button>
                        )}
                        {rec.source?.contact_email && (
                          <Button
                            variant="outlined"
                            href={`mailto:${rec.source.contact_email}`}
                          >
                            Contact Email
                          </Button>
                        )}
                        <Button
                          variant="contained"
                          disabled={rec.eligibility_status === 'not_eligible'}
                        >
                          Apply Now
                        </Button>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>

            <Alert severity="success" sx={{ mt: 3 }}>
              <Typography variant="body2">
                <strong>Next Steps:</strong> Review each funding opportunity carefully. 
                Ensure your business proposal meets all eligibility criteria before applying. 
                Consider reaching out to funding providers for additional guidance on the application process.
              </Typography>
            </Alert>
          </>
        )}

        {/* Real-time Search Results */}
        {searchResults.length > 0 && (
          <Box sx={{ mt: 4 }}>
            <Divider sx={{ mb: 3 }} />
            <Typography variant="h5" gutterBottom sx={{ color: 'primary.main' }}>
              🌐 Real-time Search Results ({searchResults.length} found)
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Additional funding opportunities found through real-time internet search:
            </Typography>

            <Grid container spacing={3}>
              {searchResults.map((funder, index) => (
                <Grid item xs={12} key={`search-${index}`}>
                  <Card sx={{ mb: 2, border: '1px solid', borderColor: 'primary.main' }}>
                    <CardContent>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                        <Box>
                          <Typography variant="h6" gutterBottom sx={{ color: 'primary.main' }}>
                            {funder.name}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            {funder.description}
                          </Typography>
                          <Chip 
                            label={funder.source || 'Web Search'} 
                            size="small" 
                            variant="outlined" 
                            sx={{ mt: 1 }}
                          />
                        </Box>
                        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 1 }}>
                          {funder.match_score && (
                            <Chip
                              label={`${Math.round(funder.match_score)}% Match`}
                              size="small"
                              color="primary"
                              variant="outlined"
                            />
                          )}
                          {funder.eligibility_status && (
                            <Chip
                              icon={getEligibilityIcon(funder.eligibility_status)}
                              label={funder.eligibility_status.replace('_', ' ').toUpperCase()}
                              color={getEligibilityColor(funder.eligibility_status)}
                              size="small"
                            />
                          )}
                        </Box>
                      </Box>

                      <Grid container spacing={2} sx={{ mb: 2 }}>
                        {funder.amount_range && (
                          <Grid item xs={12} sm={6} md={4}>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <AttachMoney color="primary" />
                              <Box>
                                <Typography variant="caption" color="text.secondary">
                                  Amount Range
                                </Typography>
                                <Typography variant="body2">
                                  {funder.amount_range}
                                </Typography>
                              </Box>
                            </Box>
                          </Grid>
                        )}
                      </Grid>

                      <Divider sx={{ my: 2 }} />

                      <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
                        {funder.website && (
                          <Button
                            variant="outlined"
                            endIcon={<OpenInNew />}
                            href={funder.website}
                            target="_blank"
                            rel="noopener noreferrer"
                          >
                            Visit Website
                          </Button>
                        )}
                        <Button
                          variant="contained"
                          color="secondary"
                        >
                          Learn More
                        </Button>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>

            <Alert severity="info" sx={{ mt: 3 }}>
              <Typography variant="body2">
                <strong>Real-time Results:</strong> These funding opportunities were found through real-time internet search 
                based on your proposal details. Information may need verification directly with the funding provider.
              </Typography>
            </Alert>
          </Box>
        )}
      </Paper>
    </Container>
  );
};

export default FundingRecommendations;
