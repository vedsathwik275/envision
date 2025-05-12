import React from 'react';
import { AppBar, Toolbar, Typography, Box } from '@mui/material';

interface HeaderProps {
  title?: string;
}

const Header: React.FC<HeaderProps> = ({ title = 'Neural Network Training Platform' }) => {
  return (
    <AppBar position="static">
      <Toolbar>
        <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
          <Typography variant="h6" component="div">
            {title}
          </Typography>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Header; 