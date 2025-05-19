# Prompt for Envision Neural POC Frontend

## Project Overview

Create a modern, intuitive frontend for the Envision Neural API - a transportation logistics prediction system that provides insights on order volumes, tender performance, and carrier performance. The frontend should enable logistics professionals to easily upload data, train models, and visualize predictions in a user-friendly interface.

## Business Context

Envision Neural helps logistics professionals make data-driven decisions by:
- Predicting order volumes between specific locations
- Analyzing tender performance across different lanes and carriers
- Evaluating carrier on-time performance for various routes

## Technical Requirements

### Technology Stack
- React 18+ with TypeScript
- Material UI or Tailwind CSS for UI components
- Recharts or Chart.js for data visualization
- React Router for navigation
- Axios for API communication

### Core Features

1. **Dashboard**
   - Overview of existing models with performance metrics
   - Quick access to recent predictions
   - Summary statistics and key performance indicators

2. **Data Management**
   - Drag-and-drop file upload for CSV data
   - Data preview functionality showing sample rows and column information
   - Data validation and error reporting

3. **Model Management**
   - Model listing with filtering options (by type, creation date, performance)
   - Model detail view showing training parameters and evaluation metrics
   - Model training interface with parameter configuration

4. **Prediction Generation & Visualization**
   - Interfaces for generating predictions for each model type
   - Interactive visualization of predictions with filtering capabilities
   - Ability to download predictions in CSV/JSON formats

5. **Lane Analysis**
   - Interactive views for analyzing predictions by specific lanes
   - Comparison of carriers for specific routes
   - Visualization of predicted vs. actual performance (where applicable)

### API Integration

The frontend should integrate with the following API endpoints:

1. **File Management**
   - `POST /api/files/upload` - Upload files
   - `POST /api/data/upload` - Upload CSV data
   - `GET /api/data/preview/{file_id}` - Preview uploaded data

2. **Model Management**
   - `GET /api/models` - List models with filtering
   - `GET /api/models/latest` - Get latest model by type
   - `GET /api/models/{model_id}` - Get model details
   - `POST /api/models/train/order-volume` - Train order volume model
   - `POST /api/models/train/tender-performance` - Train tender performance model
   - `POST /api/models/train/carrier-performance` - Train carrier performance model

3. **Prediction Management**
   - Order Volume Prediction endpoints
   - Tender Performance Prediction endpoints
   - Carrier Performance Prediction endpoints

## UI/UX Requirements

1. **Design System**
   - Clean, modern interface with a professional color scheme
   - Responsive design that works on desktop and tablets
   - Consistent typography and spacing throughout

2. **Navigation**
   - Intuitive sidebar navigation with clear categorization
   - Breadcrumb navigation for deep linking
   - Persistent access to key actions from any screen

3. **Data Visualization**
   - Interactive charts showing prediction results
   - Ability to filter and sort data on visualizations
   - Export options for charts and data

4. **User Experience**
   - Loading states for all async operations
   - Error handling with clear user feedback
   - Form validation with helpful error messages
   - Confirmation for destructive actions

## Key Screens

1. **Dashboard**
   - Models overview section with performance metrics
   - Recent predictions with quick links
   - System status and notifications

2. **Data Upload & Preview**
   - File upload zone with progress indicator
   - Data preview table with pagination
   - Column statistics and data quality indicators

3. **Model Listing**
   - Filterable table of models with key metrics
   - Comparison view for models of the same type
   - Actions to view details, generate predictions, etc.

4. **Model Detail**
   - Performance metrics visualization
   - Training parameters and dataset information
   - Actions to generate predictions or export model details

5. **Prediction Generation**
   - Form to configure prediction parameters
   - Preview of expected outputs
   - Progress indicator for prediction generation

6. **Prediction Results**
   - Interactive data tables with filtering options
   - Visualizations of prediction results by different dimensions
   - Export and download options

7. **Lane Analysis**
   - Search interface for selecting lanes
   - Comparative visualization of carriers for a lane
   - Historical performance vs. predicted performance charts

## Technical Considerations

1. **State Management**
   - Use React Context or Redux for global state management
   - Implement data caching for improved performance
   - Handle optimistic UI updates where appropriate

2. **Error Handling**
   - Comprehensive error handling for API failures
   - Graceful degradation for unavailable features
   - Clear user feedback for validation errors

3. **Performance**
   - Optimize for large datasets with virtualized lists/tables
   - Implement pagination for data-heavy screens
   - Use memoization for expensive calculations

4. **Testing**
   - Include unit tests for core components
   - Implement integration tests for key user flows
   - Set up visual regression testing

## Deliverables

1. Complete React/TypeScript application source code
2. README with setup and development instructions
3. Simple deployment instructions
4. Basic user documentation

## Example User Stories

1. As a logistics analyst, I want to upload my carrier performance CSV and train a model so I can predict on-time performance for specific lanes.

2. As a route planner, I want to compare predicted order volumes across different lanes so I can allocate resources efficiently.

3. As a carrier manager, I want to view predicted performance metrics for different carriers on specific lanes so I can make better carrier assignment decisions.

4. As a data scientist, I want to see model evaluation metrics so I can assess model quality and determine if retraining is needed.

## Design Inspiration

The frontend should have a professional, enterprise feel with:
- Clean, uncluttered layouts
- Data-forward design that emphasizes visualization
- Clear information hierarchy
- Accessibility considerations for all users

## Priority Features for POC

For the initial POC, focus on these core features:
1. Data upload and preview
2. Model listing and detail views
3. Basic prediction generation for all three model types
4. Simple visualization of prediction results
5. Lane-based filtering and analysis

Additional features can be implemented in future iterations. 