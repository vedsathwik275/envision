// API Base URL - Update this if your backend is running on a different host/port
const API_BASE_URL = 'http://localhost:8000/api';

// DOM Elements
document.addEventListener('DOMContentLoaded', () => {
    // Navigation
    const navLinks = document.querySelectorAll('.nav-link');
    const sections = document.querySelectorAll('.section');
    
    // File Upload & Preview (integrated)
    const uploadForm = document.getElementById('upload-form');
    const fileInput = document.getElementById('file-input');
    const uploadResult = document.getElementById('upload-result');
    const filePreviewContainer = document.getElementById('file-preview-container');
    const fileInfo = document.getElementById('file-info');
    const previewTable = document.getElementById('preview-table');
    
    // Model Training
    const trainingForm = document.getElementById('training-form');
    const trainingFileSelect = document.getElementById('training-file-select');
    const modelType = document.getElementById('model-type');
    const trainingResult = document.getElementById('training-result');
    
    // Model List
    const modelFilterType = document.getElementById('model-filter-type');
    const refreshModelsBtn = document.getElementById('refresh-models-btn');
    const modelsTableBody = document.getElementById('models-table-body');
    
    // Model Details Modal
    const modelDetailsModal = document.getElementById('model-details-modal');
    const modelDetailsContent = document.getElementById('model-details-content');
    const closeModalBtn = document.querySelector('.close-btn');
    
    // Predictions
    const predictionForm = document.getElementById('prediction-form');
    const predictionModelType = document.getElementById('prediction-model-type');
    const predictionModelSelect = document.getElementById('prediction-model-select');
    const predictionParams = document.getElementById('prediction-params');
    const predictionResult = document.getElementById('prediction-result');
    const predictionSummary = document.getElementById('prediction-summary');
    const predictionTable = document.getElementById('prediction-table');
    const predictionDownload = document.getElementById('prediction-download');
    
    // Initialize the app
    init();
    
    // Functions
    function init() {
        setupNavigation();
        setupEventListeners();
        loadUploadedFiles();
        loadModels();
    }
    
    function setupNavigation() {
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const targetSection = link.getAttribute('data-section');
                
                navLinks.forEach(link => link.classList.remove('active'));
                sections.forEach(section => section.classList.remove('active'));
                
                link.classList.add('active');
                document.getElementById(targetSection).classList.add('active');
            });
        });
    }
    
    function setupEventListeners() {
        // File Upload
        uploadForm.addEventListener('submit', handleFileUpload);
        
        // Model Training
        trainingForm.addEventListener('submit', handleModelTraining);
        
        // Model List
        refreshModelsBtn.addEventListener('click', loadModels);
        modelFilterType.addEventListener('change', loadModels);
        
        // Modal Close
        closeModalBtn.addEventListener('click', () => {
            modelDetailsModal.style.display = 'none';
        });
        
        window.addEventListener('click', (e) => {
            if (e.target === modelDetailsModal) {
                modelDetailsModal.style.display = 'none';
            }
        });
        
        // Predictions
        predictionModelType.addEventListener('change', handlePredictionModelTypeChange);
        predictionForm.addEventListener('submit', handlePredictionGeneration);
    }
    
    // File Management Functions
    async function handleFileUpload(e) {
        e.preventDefault();
        
        const file = fileInput.files[0];
        if (!file) {
            showError(uploadResult, 'Please select a file to upload.');
            return;
        }
        
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            // Clear previous results
            uploadResult.innerHTML = '';
            fileInfo.innerHTML = '';
            previewTable.innerHTML = '';
            filePreviewContainer.style.display = 'none';
            
            // Show loading state
            showLoading(uploadResult);
            
            // Upload the file
            const response = await fetch(`${API_BASE_URL}/files/upload`, {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                // Store the uploaded file ID for preview
                const uploadedFileId = data.file_id;
                const uploadedFileName = data.filename;
                
                // Display success message
                showSuccess(uploadResult, `File "${uploadedFileName}" uploaded successfully! File ID: ${uploadedFileId}`);
                
                // Immediately fetch and display the file preview
                await previewFile(uploadedFileId);
                
                // Reload the file list for training dropdowns
                loadUploadedFiles();
            } else {
                showError(uploadResult, `Upload failed: ${data.error || 'Unknown error'}`);
            }
        } catch (error) {
            showError(uploadResult, `Upload error: ${error.message}`);
        }
    }
    
    // Function to preview a file by ID
    async function previewFile(fileId) {
        try {
            // Show loading state below the upload result
            const loadingElement = document.createElement('div');
            loadingElement.className = 'loading-preview';
            loadingElement.innerHTML = '<div class="loading">Loading preview...</div>';
            uploadResult.appendChild(loadingElement);
            
            // Fetch file preview data from API
            const response = await fetch(`${API_BASE_URL}/data/preview/${fileId}`);
            const data = await response.json();
            
            // Remove loading indicator
            uploadResult.querySelector('.loading-preview').remove();
            
            if (response.ok) {
                // Show the preview container
                filePreviewContainer.style.display = 'block';
                
                // Display the file preview
                displayFilePreview(data);
            } else {
                const errorMessage = document.createElement('div');
                errorMessage.className = 'error';
                errorMessage.textContent = `Preview failed: ${data.error || data.message || 'Unknown error'}`;
                uploadResult.appendChild(errorMessage);
            }
        } catch (error) {
            const errorMessage = document.createElement('div');
            errorMessage.className = 'error';
            errorMessage.textContent = `Preview error: ${error.message}`;
            uploadResult.appendChild(errorMessage);
        }
    }
    
    async function loadUploadedFiles() {
        try {
            // Fetch files from the API
            const response = await fetch(`${API_BASE_URL}/files/`);
            const data = await response.json();
            
            if (response.ok) {
                // Check if the response data is an array
                const files = Array.isArray(data) ? data : (data.files || []);
                
                // Sort files by upload_time (newest first)
                files.sort((a, b) => {
                    return new Date(b.upload_time) - new Date(a.upload_time);
                });
                
                // Take only the 3 most recent files
                const recentFiles = files.slice(0, 3);
                
                // Map the API response to the format required by updateFileSelects
                const formattedFiles = recentFiles.map(file => ({
                    file_id: file.file_id,
                    filename: file.filename,
                    upload_time: file.upload_time
                }));
                
                updateFileSelects(formattedFiles);
                return formattedFiles; // Return the files for chaining
            } else {
                console.error('Failed to load files:', data.error || 'Unknown error');
                return []; // Return empty array on error
            }
        } catch (error) {
            console.error('Failed to load files:', error);
            return []; // Return empty array on error
        }
    }
    
    function updateFileSelects(files) {
        // Clear existing options
        trainingFileSelect.innerHTML = '<option value="">-- Select a file --</option>';
        
        // Add new options
        files.forEach(file => {
            const trainingOption = document.createElement('option');
            trainingOption.value = file.file_id;
            
            // Format the date for better readability
            const uploadDate = new Date(file.upload_time);
            const formattedDate = uploadDate.toLocaleDateString() + ' ' + 
                                 uploadDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            
            trainingOption.textContent = `${file.filename} (${formattedDate})`;
            trainingFileSelect.appendChild(trainingOption);
        });
    }
    
    function displayFilePreview(previewData) {
        // Display file info
        fileInfo.innerHTML = `
            <p><strong>File ID:</strong> ${previewData.file_id}</p>
            <p><strong>Total Rows:</strong> ${previewData.total_rows}</p>
            <p><strong>Total Columns:</strong> ${previewData.total_columns}</p>
            <p><strong>Missing Data:</strong> ${previewData.missing_data_summary.total_missing} cells (${previewData.missing_data_summary.percent_missing}%)</p>
        `;
        
        // Set up table headers
        const columnHeaders = Object.keys(previewData.sample_rows[0] || {});
        let tableHTML = '<thead><tr>';
        columnHeaders.forEach(header => {
            tableHTML += `<th>${header}</th>`;
        });
        tableHTML += '</tr></thead><tbody>';
        
        // Add sample rows
        previewData.sample_rows.forEach(row => {
            tableHTML += '<tr>';
            columnHeaders.forEach(header => {
                tableHTML += `<td>${row[header] || ''}</td>`;
            });
            tableHTML += '</tr>';
        });
        tableHTML += '</tbody>';
        
        previewTable.innerHTML = tableHTML;
    }
    
    // Model Management Functions
    async function handleModelTraining(e) {
        e.preventDefault();
        
        const fileId = trainingFileSelect.value;
        const selectedModelType = modelType.value;
        
        if (!fileId) {
            showError(trainingResult, 'Please select a file for training.');
            return;
        }
        
        if (!selectedModelType) {
            showError(trainingResult, 'Please select a model type.');
            return;
        }
        
        const trainingParams = {
            epochs: parseInt(document.getElementById('epochs').value, 10),
            batch_size: parseInt(document.getElementById('batch-size').value, 10),
            validation_split: parseFloat(document.getElementById('validation-split').value),
            description: document.getElementById('model-description').value
        };
        
        try {
            showLoading(trainingResult);
            const response = await fetch(`${API_BASE_URL}/models/train/${selectedModelType}?data_file_id=${fileId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(trainingParams)
            });
            
            const data = await response.json();
            
            if (data.status === 'success' || data.status === 'pending') {
                // Show initial success message
                showSuccess(trainingResult, `${capitalizeFirstLetter(selectedModelType)} model training started! ${data.message || ''}`);
                
                // Start polling for the completed model
                pollForTrainedModel(fileId, selectedModelType);
            } else {
                showError(trainingResult, `Training failed: ${data.error || 'Unknown error'}`);
            }
        } catch (error) {
            showError(trainingResult, `Training error: ${error.message}`);
        }
    }
    
    // Function to poll for the trained model until it appears in the models list
    async function pollForTrainedModel(fileId, modelType) {
        // Create status element
        const statusElement = document.createElement('div');
        statusElement.className = 'training-status';
        statusElement.innerHTML = '<div class="loading">Waiting for model training to complete...</div>';
        trainingResult.appendChild(statusElement);
        
        // Convert model type format if needed (order-volume → order_volume)
        const apiModelType = modelType.replace('-', '_');
        
        // Start polling
        const pollInterval = setInterval(async () => {
            try {
                const response = await fetch(`${API_BASE_URL}/models?model_type=${apiModelType}`);
                const data = await response.json();
                
                if (response.ok && data.models && data.models.length > 0) {
                    // Look for a model that was trained on our file
                    // The training_data path contains the file ID
                    const matchedModel = data.models.find(model => 
                        model.training_data && model.training_data.includes(fileId)
                    );
                    
                    if (matchedModel) {
                        clearInterval(pollInterval);
                        
                        // Update status with success
                        statusElement.innerHTML = `
                            <div class="success-message">
                                <p><strong>Model training completed!</strong></p>
                                <p>Model ID: ${matchedModel.model_id}</p>
                                <p>Created: ${new Date(matchedModel.created_at).toLocaleString()}</p>
                                <p>Performance metrics:</p>
                                <ul>
                                    ${Object.entries(matchedModel.evaluation || {}).map(([key, value]) => 
                                        `<li>${key}: ${typeof value === 'number' ? value.toFixed(4) : value}</li>`
                                    ).join('')}
                                </ul>
                                <button id="view-trained-model" class="btn primary">View Model Details</button>
                            </div>
                        `;
                        
                        // Add event listener to the view model button
                        document.getElementById('view-trained-model').addEventListener('click', () => {
                            // Navigate to models tab
                            document.querySelector('.nav-link[data-section="model-list"]').click();
                            
                            // Refresh models and highlight the new one
                            loadModels().then(() => {
                                // Find and highlight the row with our model
                                const modelRow = document.querySelector(`tr[data-model-id="${matchedModel.model_id}"]`);
                                if (modelRow) {
                                    modelRow.classList.add('highlight-row');
                                    modelRow.scrollIntoView({ behavior: 'smooth', block: 'center' });
                                    
                                    // Remove highlight after a few seconds
                                    setTimeout(() => {
                                        modelRow.classList.remove('highlight-row');
                                    }, 5000);
                                }
                            });
                        });
                    }
                }
            } catch (error) {
                console.error('Error polling for model:', error);
            }
        }, 5000); // Poll every 5 seconds
        
        // Stop polling after 5 minutes (prevent infinite polling)
        setTimeout(() => {
            if (statusElement.querySelector('.loading')) {
                clearInterval(pollInterval);
                statusElement.innerHTML = `
                    <div class="warning">
                        Model training is taking longer than expected. 
                        Please check the Models tab later for your trained model.
                    </div>
                `;
            }
        }, 5 * 60 * 1000); // 5 minutes
    }
    
    async function loadModels() {
        try {
            showLoading(modelsTableBody);
            const filterType = modelFilterType.value;
            let url = `${API_BASE_URL}/models`;
            
            if (filterType) {
                url += `?model_type=${filterType}`;
            }
            
            const response = await fetch(url);
            const data = await response.json();
            
            if (response.ok) {
                displayModels(data.models);
            } else {
                showError(modelsTableBody, `Failed to load models: ${data.error || 'Unknown error'}`);
            }
        } catch (error) {
            showError(modelsTableBody, `Error loading models: ${error.message}`);
        }
    }
    
    function displayModels(models) {
        modelsTableBody.innerHTML = '';
        
        if (!models || models.length === 0) {
            modelsTableBody.innerHTML = `<tr><td colspan="5">No models available</td></tr>`;
            return;
        }
        
        models.forEach(model => {
            const row = document.createElement('tr');
            // Add data attribute for model ID to help with highlighting
            row.setAttribute('data-model-id', model.model_id);
            
            // Format metrics
            let metricsHTML = '<ul>';
            for (const [key, value] of Object.entries(model.evaluation || {})) {
                const formattedValue = typeof value === 'number' ? value.toFixed(4) : value;
                metricsHTML += `<li>${key}: ${formattedValue}</li>`;
            }
            metricsHTML += '</ul>';
            
            row.innerHTML = `
                <td>${model.model_id}</td>
                <td>${model.model_type}</td>
                <td>${new Date(model.created_at).toLocaleString()}</td>
                <td>${metricsHTML}</td>
                <td>
                    <button class="btn secondary view-model-btn" data-model-id="${model.model_id}">Details</button>
                    <button class="btn primary predict-model-btn" data-model-id="${model.model_id}" data-model-type="${model.model_type}">Predict</button>
                </td>
            `;
            
            modelsTableBody.appendChild(row);
        });
        
        // Add event listeners to the buttons
        document.querySelectorAll('.view-model-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const modelId = btn.getAttribute('data-model-id');
                viewModelDetails(modelId);
            });
        });
        
        document.querySelectorAll('.predict-model-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const modelId = btn.getAttribute('data-model-id');
                const modelType = btn.getAttribute('data-model-type');
                setupPrediction(modelId, modelType);
            });
        });
    }
    
    async function viewModelDetails(modelId) {
        try {
            showLoading(modelDetailsContent);
            modelDetailsModal.style.display = 'block';
            
            const response = await fetch(`${API_BASE_URL}/models/${modelId}`);
            const data = await response.json();
            
            if (response.ok) {
                displayModelDetails(data);
            } else {
                modelDetailsContent.innerHTML = `<p class="error">Failed to load model details: ${data.error || 'Unknown error'}</p>`;
            }
        } catch (error) {
            modelDetailsContent.innerHTML = `<p class="error">Error loading model details: ${error.message}</p>`;
        }
    }
    
    function displayModelDetails(model) {
        // Format training parameters
        let trainingParamsHTML = '<ul>';
        for (const [key, value] of Object.entries(model.training_params || {})) {
            trainingParamsHTML += `<li>${key}: ${value}</li>`;
        }
        trainingParamsHTML += '</ul>';
        
        // Format evaluation metrics
        let evaluationHTML = '<ul>';
        for (const [key, value] of Object.entries(model.evaluation || {})) {
            evaluationHTML += `<li>${key}: ${value}</li>`;
        }
        evaluationHTML += '</ul>';
        
        modelDetailsContent.innerHTML = `
            <div class="model-details">
                <p><strong>Model ID:</strong> ${model.model_id}</p>
                <p><strong>Model Type:</strong> ${model.model_type}</p>
                <p><strong>Created:</strong> ${new Date(model.created_at).toLocaleString()}</p>
                <p><strong>Description:</strong> ${model.description || 'No description provided'}</p>
                <p><strong>Training Data:</strong> ${model.training_data || 'Unknown'}</p>
                
                <h3>Training Parameters</h3>
                ${trainingParamsHTML}
                
                <h3>Evaluation Metrics</h3>
                ${evaluationHTML}
            </div>
        `;
    }
    
    // Prediction Functions
    function handlePredictionModelTypeChange() {
        const selectedType = predictionModelType.value;
        loadModelsForPrediction(selectedType);
        updatePredictionParams(selectedType);
    }
    
    async function loadModelsForPrediction(modelType) {
        // Clear existing options
        predictionModelSelect.innerHTML = '<option value="">-- Select a model --</option>';
        
        if (!modelType) return;
        
        try {
            const url = `${API_BASE_URL}/models?model_type=${modelType}`;
            const response = await fetch(url);
            const data = await response.json();
            
            if (response.ok && data.models) {
                data.models.forEach(model => {
                    const option = document.createElement('option');
                    option.value = model.model_id;
                    option.textContent = `${model.model_id} (${new Date(model.created_at).toLocaleDateString()})`;
                    predictionModelSelect.appendChild(option);
                });
            }
        } catch (error) {
            console.error('Error loading models for prediction:', error);
        }
    }
    
    function updatePredictionParams(modelType) {
        let paramsHTML = '';
        
        switch (modelType) {
            case 'order-volume':
                paramsHTML = `
                    <h4>Order Volume Parameters</h4>
                    <div class="form-group">
                        <label for="months-ahead">Months to Predict:</label>
                        <input type="number" id="months-ahead" value="6" min="1" max="12">
                    </div>
                `;
                break;
                
            case 'tender-performance':
                paramsHTML = `
                    <h4>Tender Performance Parameters</h4>
                    <div class="form-group">
                        <label for="source-city">Source City (optional):</label>
                        <input type="text" id="source-city" placeholder="Filter by source city">
                    </div>
                    <div class="form-group">
                        <label for="dest-city">Destination City (optional):</label>
                        <input type="text" id="dest-city" placeholder="Filter by destination city">
                    </div>
                    <div class="form-group">
                        <label for="carrier">Carrier (optional):</label>
                        <input type="text" id="carrier" placeholder="Filter by carrier">
                    </div>
                `;
                break;
                
            case 'carrier-performance':
                paramsHTML = `
                    <h4>Carrier Performance Parameters</h4>
                    <div class="form-group">
                        <label for="cp-source-city">Source City (optional):</label>
                        <input type="text" id="cp-source-city" placeholder="Filter by source city">
                    </div>
                    <div class="form-group">
                        <label for="cp-dest-city">Destination City (optional):</label>
                        <input type="text" id="cp-dest-city" placeholder="Filter by destination city">
                    </div>
                    <div class="form-group">
                        <label for="cp-carrier">Carrier (optional):</label>
                        <input type="text" id="cp-carrier" placeholder="Filter by carrier">
                    </div>
                `;
                break;
        }
        
        predictionParams.innerHTML = paramsHTML;
    }
    
    function setupPrediction(modelId, modelType) {
        // Navigate to predictions tab
        document.querySelector(`.nav-link[data-section="predictions"]`).click();
        
        // Convert API model type to form format
        const formattedType = modelType.replace('_', '-');
        
        // Set the model type
        predictionModelType.value = formattedType;
        
        // Trigger model type change event
        const event = new Event('change');
        predictionModelType.dispatchEvent(event);
        
        // Set the model ID after models are loaded
        setTimeout(() => {
            predictionModelSelect.value = modelId;
        }, 500);
    }
    
    async function handlePredictionGeneration(e) {
        e.preventDefault();
        
        const modelId = predictionModelSelect.value;
        const modelType = predictionModelType.value;
        
        if (!modelId) {
            showError(predictionResult, 'Please select a model for prediction.');
            return;
        }
        
        try {
            showLoading(predictionResult);
            
            let endpoint, requestBody = { model_id: modelId };
            
            // Model-specific parameters
            switch (modelType) {
                case 'order-volume':
                    endpoint = `${API_BASE_URL}/predictions/order-volume`;
                    requestBody.months = parseInt(document.getElementById('months-ahead')?.value || 6, 10);
                    break;
                    
                case 'tender-performance':
                    endpoint = `${API_BASE_URL}/predictions/tender-performance`;
                    break;
                    
                case 'carrier-performance':
                    endpoint = `${API_BASE_URL}/predictions/carrier-performance`;
                    break;
            }
            
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestBody)
            });
            
            const data = await response.json();
            
            if (response.ok) {
                displayPredictionResults(data, modelType);
            } else {
                showError(predictionResult, `Prediction failed: ${data.error || 'Unknown error'}`);
            }
        } catch (error) {
            showError(predictionResult, `Prediction error: ${error.message}`);
        }
    }
    
    function displayPredictionResults(predictionData, modelType) {
        // Display prediction summary
        let summaryHTML = `
            <div class="prediction-summary">
                <p><strong>Prediction ID:</strong> ${predictionData.prediction_id}</p>
                <p><strong>Model ID:</strong> ${predictionData.model_id}</p>
                <p><strong>Created:</strong> ${new Date(predictionData.created_at || predictionData.prediction_time).toLocaleString()}</p>
                <p><strong>Total Predictions:</strong> ${predictionData.prediction_count}</p>
        `;
        
        // Add model-specific metrics if available
        if (predictionData.metrics) {
            summaryHTML += '<div class="metrics"><h4>Metrics:</h4><ul>';
            for (const [key, value] of Object.entries(predictionData.metrics)) {
                summaryHTML += `<li>${key}: ${value}</li>`;
            }
            summaryHTML += '</ul></div>';
        }
        
        summaryHTML += '</div>';
        predictionSummary.innerHTML = summaryHTML;
        
        // Create download links
        const downloadHTML = `
            <p>Download predictions:</p>
            <a href="${API_BASE_URL}/predictions/${modelType}/${predictionData.model_id}/download?format=csv" class="btn secondary" target="_blank">CSV</a>
            <a href="${API_BASE_URL}/predictions/${modelType}/${predictionData.model_id}/download?format=json" class="btn secondary" target="_blank">JSON</a>
        `;
        predictionDownload.innerHTML = downloadHTML;
        
        // Display prediction table
        displayPredictionTable(predictionData, modelType);
    }
    
    function displayPredictionTable(predictionData, modelType) {
        const predictions = predictionData.predictions || 
                           (predictionData.data && predictionData.data.predictions) || [];
                           
        if (!predictions.length) {
            predictionTable.innerHTML = '<p>No prediction data available.</p>';
            return;
        }
        
        // Get all column headers from the first prediction
        const columnHeaders = Object.keys(predictions[0]);
        
        let tableHTML = '<thead><tr>';
        columnHeaders.forEach(header => {
            tableHTML += `<th>${formatColumnHeader(header)}</th>`;
        });
        tableHTML += '</tr></thead><tbody>';
        
        // Add prediction rows (limit to first 20 for display)
        const displayLimit = Math.min(20, predictions.length);
        for (let i = 0; i < displayLimit; i++) {
            tableHTML += '<tr>';
            columnHeaders.forEach(header => {
                tableHTML += `<td>${predictions[i][header] || ''}</td>`;
            });
            tableHTML += '</tr>';
        }
        
        if (predictions.length > displayLimit) {
            tableHTML += `<tr><td colspan="${columnHeaders.length}">Showing ${displayLimit} of ${predictions.length} predictions. Download the full dataset to see all.</td></tr>`;
        }
        
        tableHTML += '</tbody>';
        predictionTable.innerHTML = tableHTML;
    }
    
    // Utility Functions
    function showLoading(element) {
        element.innerHTML = '<div class="loading">Loading...</div>';
    }
    
    function showError(element, message) {
        element.innerHTML = `<div class="error">${message}</div>`;
    }
    
    function showSuccess(element, message) {
        element.innerHTML = `<div class="success-message">${message}</div>`;
    }
    
    function capitalizeFirstLetter(string) {
        return string.charAt(0).toUpperCase() + string.slice(1);
    }
    
    function formatColumnHeader(header) {
        // Convert snake_case to Title Case
        return header
            .split('_')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    }
}); 