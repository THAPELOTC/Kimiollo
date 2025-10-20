import React, { useState } from 'react';
import {
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Box,
  Stepper,
  Step,
  StepLabel,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  CircularProgress,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';

const steps = ['Business Overview', 'Market Information', 'Financial Requirements'];

const BusinessPlanGenerator = () => {
  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    business_type: '',
    industry: '',
    target_market: '',
    funding_requirements: '',
    business_description: '',
  });

  const navigate = useNavigate();
  const { token, logout } = useAuth();
  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

  const businessTypes = [
    'Sole Proprietorship',
    'Partnership',
    'Corporation',
    'Startup',
    'Small Business',
    'Non-Profit',
  ];

  const industries = [
    'Technology',
    'Manufacturing',
    'Healthcare',
    'Education',
    'Agriculture',
    'Retail',
    'Financial Services',
    'Construction',
    'Consulting',
    'Other',
  ];

  const handleChange = (name, value) => {
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handleNext = () => {
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  const handleSubmit = async () => {
    setLoading(true);
    try {
      if (!token) {
        toast.error('Authentication required');
        return;
      }

      const response = await axios.post(`${API_BASE_URL}/generate-business-plan`, formData, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      toast.success('Business plan generated successfully!');
      navigate(`/analyze/${response.data.proposal_id}`);
    } catch (error) {
      console.log('Generate business plan error:', error.response?.data);
      
      // Handle authentication errors
      if (error.response?.status === 401) {
        toast.error('Session expired. Please login again.');
        logout();
        navigate('/login');
        return;
      }
      
      toast.error(error.response?.data?.error || 'Failed to generate business plan');
    } finally {
      setLoading(false);
    }
  };

  const getStepContent = (step) => {
    switch (step) {
      case 0:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Business Type</InputLabel>
                <Select
                  value={formData.business_type}
                  label="Business Type"
                  onChange={(e) => handleChange('business_type', e.target.value)}
                >
                  {businessTypes.map((type) => (
                    <MenuItem key={type} value={type}>
                      {type}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Industry</InputLabel>
                <Select
                  value={formData.industry}
                  label="Industry"
                  onChange={(e) => handleChange('industry', e.target.value)}
                >
                  {industries.map((industry) => (
                    <MenuItem key={industry} value={industry}>
                      {industry}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Business Description"
                multiline
                rows={4}
                value={formData.business_description}
                onChange={(e) => handleChange('business_description', e.target.value)}
                placeholder="Describe your business idea, products, or services..."
              />
            </Grid>
          </Grid>
        );
      case 1:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Target Market"
                multiline
                rows={3}
                value={formData.target_market}
                onChange={(e) => handleChange('target_market', e.target.value)}
                placeholder="Describe your ideal customers, market size, and demographics..."
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Funding Requirements"
                value={formData.funding_requirements}
                onChange={(e) => handleChange('funding_requirements', e.target.value)}
                placeholder="e.g., R500,000 for initial setup and working capital"
              />
            </Grid>
          </Grid>
        );
      case 2:
        return (
          <Box>
            <Alert severity="info" sx={{ mb: 3 }}>
              Review your information before generating the business plan. You can go back to make changes.
            </Alert>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <Typography variant="subtitle2" color="text.secondary">
                  Business Type:
                </Typography>
                <Typography variant="body1">{formData.business_type}</Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="subtitle2" color="text.secondary">
                  Industry:
                </Typography>
                <Typography variant="body1">{formData.industry}</Typography>
              </Grid>
              <Grid item xs={12}>
                <Typography variant="subtitle2" color="text.secondary">
                  Business Description:
                </Typography>
                <Typography variant="body1">{formData.business_description}</Typography>
              </Grid>
              <Grid item xs={12}>
                <Typography variant="subtitle2" color="text.secondary">
                  Target Market:
                </Typography>
                <Typography variant="body1">{formData.target_market}</Typography>
              </Grid>
              <Grid item xs={12}>
                <Typography variant="subtitle2" color="text.secondary">
                  Funding Requirements:
                </Typography>
                <Typography variant="body1">{formData.funding_requirements}</Typography>
              </Grid>
            </Grid>
          </Box>
        );
      default:
        return 'Unknown step';
    }
  };

  const isStepValid = () => {
    switch (activeStep) {
      case 0:
        return formData.business_type && formData.industry && formData.business_description;
      case 1:
        return formData.target_market && formData.funding_requirements;
      case 2:
        return true;
      default:
        return false;
    }
  };

  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom align="center">
          Generate Business Plan
        </Typography>
        <Typography variant="body1" color="text.secondary" align="center" paragraph>
          Answer a few questions to generate a comprehensive business plan powered by AI
        </Typography>

        <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        <Box sx={{ mb: 4 }}>
          {getStepContent(activeStep)}
        </Box>

        <Box sx={{ display: 'flex', flexDirection: 'row', pt: 2 }}>
          <Button
            color="inherit"
            disabled={activeStep === 0}
            onClick={handleBack}
            sx={{ mr: 1 }}
          >
            Back
          </Button>
          <Box sx={{ flex: '1 1 auto' }} />
          {activeStep === steps.length - 1 ? (
            <Button
              onClick={handleSubmit}
              variant="contained"
              disabled={!isStepValid() || loading}
            >
              {loading ? (
                <>
                  <CircularProgress size={20} sx={{ mr: 1 }} />
                  Generating...
                </>
              ) : (
                'Generate Business Plan'
              )}
            </Button>
          ) : (
            <Button
              onClick={handleNext}
              variant="contained"
              disabled={!isStepValid()}
            >
              Next
            </Button>
          )}
        </Box>
      </Paper>
    </Container>
  );
};

export default BusinessPlanGenerator;
