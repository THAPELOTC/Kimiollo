import React, { useState, useCallback } from 'react';
import {
  Container,
  Paper,
  Typography,
  Box,
  Button,
  Alert,
  LinearProgress,
  Grid,
  Card,
  CardContent,
} from '@mui/material';
import {
  CloudUpload,
  Description,
  CheckCircle,
} from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';

const ProposalUpload = () => {
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadedFile, setUploadedFile] = useState(null);

  const navigate = useNavigate();
  const { token, logout } = useAuth();
  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

  const onDrop = useCallback(async (acceptedFiles) => {
    const file = acceptedFiles[0];
    if (!file) return;

    setUploading(true);
    setUploadProgress(0);
    setUploadedFile(file);

    const formData = new FormData();
    formData.append('file', file);

    try {
      // Simulate progress
      const progressInterval = setInterval(() => {
        setUploadProgress((prev) => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);

      // Ensure we have a token
      if (!token) {
        throw new Error('No authentication token available');
      }

      console.log('Uploading with token:', token ? 'Token present' : 'No token');
      console.log('Axios default auth:', axios.defaults.headers.common['Authorization']);

      // Make sure the token is set in axios defaults
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;

      // Use axios defaults for auth but also pass it explicitly as fallback
      const response = await axios.post(`${API_BASE_URL}/upload-proposal`, formData, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        onUploadProgress: (progressEvent) => {
          const progress = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          setUploadProgress(progress);
        },
      });

      clearInterval(progressInterval);
      setUploadProgress(100);

      toast.success('File uploaded successfully!');
      
      // Redirect to analysis page with the proposal ID
      setTimeout(() => {
        navigate(`/analyze/${response.data.proposal_id}`);
      }, 1500);

    } catch (error) {
      console.log('Upload error:', error.response?.data);
      
      // Handle authentication errors
      if (error.response?.status === 401 && error.response?.data?.error === 'invalid_token') {
        toast.error('Session expired. Please login again.');
        logout();
        navigate('/login');
        return;
      }
      
      toast.error(error.response?.data?.error || 'Upload failed');
      setUploading(false);
      setUploadProgress(0);
      setUploadedFile(null);
    }
  }, [navigate, API_BASE_URL, token, logout]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc'],
      'image/*': ['.png', '.jpg', '.jpeg'],
      'text/plain': ['.txt'],
    },
    maxFiles: 1,
    disabled: uploading,
  });

  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom align="center">
          Upload Business Proposal
        </Typography>
        <Typography variant="body1" color="text.secondary" align="center" paragraph>
          Upload your existing business proposal for AI analysis and improvement suggestions
        </Typography>

        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card
              {...getRootProps()}
              sx={{
                p: 4,
                border: '2px dashed',
                borderColor: isDragActive ? 'primary.main' : 'grey.300',
                backgroundColor: isDragActive ? 'action.hover' : 'background.paper',
                cursor: uploading ? 'not-allowed' : 'pointer',
                transition: 'all 0.3s ease',
                '&:hover': {
                  borderColor: 'primary.main',
                  backgroundColor: 'action.hover',
                },
              }}
            >
              <input {...getInputProps()} />
              <Box
                sx={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  textAlign: 'center',
                }}
              >
                {uploading ? (
                  <>
                    <Description sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
                    <Typography variant="h6" gutterBottom>
                      Uploading {uploadedFile?.name}...
                    </Typography>
                    <Box sx={{ width: '100%', mt: 2 }}>
                      <LinearProgress variant="determinate" value={uploadProgress} />
                      <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                        {uploadProgress}%
                      </Typography>
                    </Box>
                  </>
                ) : uploadedFile ? (
                  <>
                    <CheckCircle sx={{ fontSize: 64, color: 'success.main', mb: 2 }} />
                    <Typography variant="h6" gutterBottom>
                      File Uploaded Successfully!
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {uploadedFile.name}
                    </Typography>
                  </>
                ) : (
                  <>
                    <CloudUpload sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
                    <Typography variant="h6" gutterBottom>
                      {isDragActive ? 'Drop the file here' : 'Drag & drop a file here'}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" paragraph>
                      or click to select a file
                    </Typography>
                    <Button variant="outlined" disabled={uploading}>
                      Choose File
                    </Button>
                  </>
                )}
              </Box>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Supported File Types
                </Typography>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    • PDF documents (.pdf)
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    • Microsoft Word documents (.doc, .docx)
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    • Images (.png, .jpg, .jpeg) - OCR processing
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    • Text files (.txt)
                  </Typography>
                </Box>

                <Alert severity="info" sx={{ mt: 2 }}>
                  <Typography variant="body2">
                    Your document will be analyzed for completeness, structure, and quality.
                    You'll receive detailed feedback and improvement suggestions.
                  </Typography>
                </Alert>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        <Box sx={{ mt: 4, textAlign: 'center' }}>
          <Typography variant="body2" color="text.secondary">
            Maximum file size: 10MB
          </Typography>
        </Box>
      </Paper>
    </Container>
  );
};

export default ProposalUpload;
