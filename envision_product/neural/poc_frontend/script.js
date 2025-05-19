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
    const predictionTableContainer = document.getElementById('prediction-table-container');
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
            // Convert frontend model type format to API format if needed (order-volume → order_volume)
            const apiModelType = modelType.replace('-', '_');
            
            // Fetch models of the selected type
            const url = `${API_BASE_URL}/models?model_type=${apiModelType}`;
            const response = await fetch(url);
            const data = await response.json();
            
            if (response.ok && data.models && data.models.length > 0) {
                // Sort models by creation date (newest first)
                const sortedModels = [...data.models].sort((a, b) => {
                    return new Date(b.created_at) - new Date(a.created_at);
                });
                
                // Take only the 3 most recent models
                const recentModels = sortedModels.slice(0, 3);
                
                // Add model options to the dropdown
                recentModels.forEach(model => {
                    const option = document.createElement('option');
                    option.value = model.model_id;
                    
                    // Format the creation date
                    const creationDate = new Date(model.created_at);
                    const formattedDate = creationDate.toLocaleDateString() + ' ' + 
                                         creationDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
                    
                    option.textContent = `${model.model_id} (${formattedDate})`;
                    predictionModelSelect.appendChild(option);
                });
                
                // If there are options, select the first one (most recent)
                if (predictionModelSelect.options.length > 1) {
                    predictionModelSelect.selectedIndex = 1;
                }
            } else {
                // Add a disabled option indicating no models available
                const option = document.createElement('option');
                option.disabled = true;
                option.textContent = 'No models available for this type';
                predictionModelSelect.appendChild(option);
            }
        } catch (error) {
            console.error('Error loading models for prediction:', error);
            
            // Add an error option
            const option = document.createElement('option');
            option.disabled = true;
            option.textContent = 'Error loading models';
            predictionModelSelect.appendChild(option);
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
        document.querySelector('.nav-link[data-section="predictions"]').click();
        
        // Convert API model type to form format (order_volume → order-volume)
        const formattedType = modelType.replace('_', '-');
        
        // Set the model type
        predictionModelType.value = formattedType;
        
        // Trigger model type change event
        const event = new Event('change');
        predictionModelType.dispatchEvent(event);
        
        // Set the model ID after models are loaded (with a slight delay)
        setTimeout(() => {
            // Try to find and select the specific model
            for (let i = 0; i < predictionModelSelect.options.length; i++) {
                if (predictionModelSelect.options[i].value === modelId) {
                    predictionModelSelect.selectedIndex = i;
                    break;
                }
            }
            
            // If the specific model isn't in the dropdown (it might be older than the top 3),
            // we'll stick with the default behavior of selecting the most recent model
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
            
            console.log(`Step 1: Sending prediction request to ${endpoint}`, requestBody);
            
            // Step 1: Generate the predictions
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestBody)
            });
            
            const data = await response.json();
            
            console.log('Step 1 Response:', data);
            
            if (!response.ok) {
                const errorMsg = data.error || data.message || 'Unknown error occurred';
                console.error('Prediction API error:', errorMsg);
                showError(predictionResult, `Prediction failed: ${errorMsg}`);
                return;
            }
            
            // Store the prediction metadata for summary
            const predictionMetadata = data;
            
            // Step 2: Fetch the actual prediction data using a separate API call
            console.log(`Step 2: Fetching prediction results for model ${modelId}`);
            
            // Important: Keep the hyphens in the URL path! The API endpoints use hyphens.
            // Only the model ID itself uses underscores, but the endpoint path should have hyphens.
            const fetchEndpoint = `${API_BASE_URL}/predictions/${modelType}/${modelId}?simplified=true`;
            
            console.log(`Using fetch endpoint: ${fetchEndpoint}`);
            
            try {
                const predictionResponse = await fetch(fetchEndpoint);
                
                // Check response content type
                const contentType = predictionResponse.headers.get('content-type');
                console.log(`Response content type: ${contentType}`);
                
                let predictionData;
                
                if (contentType && contentType.includes('application/json')) {
                    predictionData = await predictionResponse.json();
                    console.log('Step 2 Response (JSON):', predictionData);
                    
                    // Debug the structure of the prediction data
                    console.log('Prediction data type:', typeof predictionData);
                    console.log('Is array?', Array.isArray(predictionData));
                    if (Array.isArray(predictionData)) {
                        console.log('Array length:', predictionData.length);
                        if (predictionData.length > 0) {
                            console.log('First item:', predictionData[0]);
                        }
                    } else {
                        console.log('Object keys:', Object.keys(predictionData));
                    }
                } else {
                    // If not JSON, try to get the text response
                    const textResponse = await predictionResponse.text();
                    console.log('Step 2 Response (Text):', textResponse);
                    predictionData = [];
                    showError(predictionResult, `Received non-JSON response: ${textResponse.substring(0, 100)}...`);
                    return;
                }
                
                if (!predictionResponse.ok) {
                    showError(predictionResult, `Failed to fetch prediction results: ${predictionData.error || 'Unknown error'}`);
                    return;
                }
                
                // If predictionData is empty or not useful, show a message
                if (!predictionData || 
                    (Array.isArray(predictionData) && predictionData.length === 0) ||
                    (typeof predictionData === 'object' && Object.keys(predictionData).length === 0)) {
                    showError(predictionResult, 'Received empty prediction results from the API.');
                    return;
                }
                
                // Make sure predictionData is in a usable format for our display functions
                let combinedData;
                
                if (Array.isArray(predictionData)) {
                    // If it's an array of predictions, wrap it properly
                    combinedData = {
                        ...predictionMetadata,
                        predictions: predictionData
                    };
                } else {
                    // If it's already an object, merge with metadata
                    combinedData = {
                        ...predictionMetadata,
                        ...predictionData
                    };
                }
                
                console.log('Combined prediction data:', combinedData);
                
                // Display the combined results
                displayPredictionResults(combinedData, modelType);
            } catch (fetchError) {
                console.error('Error fetching prediction results:', fetchError);
                showError(predictionResult, `Error fetching prediction results: ${fetchError.message}`);
            }
        } catch (error) {
            console.error('Prediction generation error:', error);
            showError(predictionResult, `Prediction error: ${error.message}`);
        }
    }
    
    function displayPredictionResults(predictionData, modelType) {
        console.log('Displaying prediction results for:', predictionData);
        
        // Check if predictionResult exists
        if (!predictionResult) {
            console.error('ERROR: predictionResult element not found in the DOM!');
            return;
        }
        
        console.log('DOM structure check:');
        console.log('- predictionResult parent:', predictionResult.parentElement);
        
        // IMPORTANT: Instead of clearing the entire container which removes all child elements,
        // find the loading indicator and only clear that
        const loadingElement = predictionResult.querySelector('.loading');
        if (loadingElement) {
            console.log('Removing loading indicator');
            loadingElement.remove();
        } else {
            console.log('No loading indicator found to remove');
        }
        
        // First make sure the summary, table, and download elements exist
        // If they don't exist, we need to recreate them
        let summaryElement = document.getElementById('prediction-summary');
        let tableContainerElement = document.getElementById('prediction-table-container');
        let tableElement = document.getElementById('prediction-table');
        let downloadElement = document.getElementById('prediction-download');
        
        // If any of these are missing, recreate the entire structure
        if (!summaryElement || !tableContainerElement || !tableElement || !downloadElement) {
            console.log('Recreating prediction result structure because elements are missing');
            
            // Create the full structure
            predictionResult.innerHTML = `
                <div id="prediction-summary"></div>
                <div id="prediction-table-container">
                    <table id="prediction-table"></table>
                </div>
                <div id="prediction-download" class="download-area"></div>
            `;
            
            // Get the newly created elements
            summaryElement = document.getElementById('prediction-summary');
            tableContainerElement = document.getElementById('prediction-table-container');
            tableElement = document.getElementById('prediction-table');
            downloadElement = document.getElementById('prediction-download');
        }
        
        // First extract all possible metadata we need
        const modelId = predictionData.model_id;
        const predictionId = predictionData.prediction_id;
        
        // Handle nested data structure for metrics
        const metrics = predictionData.metrics || 
                       (predictionData.data && predictionData.data.metrics) || {};
        
        // Handle nested data structure for timestamps
        const predictionTime = predictionData.created_at || 
                              predictionData.prediction_time || 
                              (predictionData.data && predictionData.data.prediction_time) || 
                              new Date().toISOString();
        
        // Determine prediction count from various possible sources
        let predictionCount = 0;
        if (Array.isArray(predictionData.predictions)) {
            predictionCount = predictionData.predictions.length;
        } else if (Array.isArray(predictionData)) {
            predictionCount = predictionData.length;
        } else if (predictionData.prediction_count) {
            predictionCount = predictionData.prediction_count;
        } else if (predictionData.data && predictionData.data.predictions) {
            predictionCount = predictionData.data.predictions.length;
        }
        
        // Display prediction summary
        let summaryHTML = `
            <div class="prediction-summary">
                <p><strong>Prediction ID:</strong> ${predictionId || 'N/A'}</p>
                <p><strong>Model ID:</strong> ${modelId || 'N/A'}</p>
                <p><strong>Created:</strong> ${new Date(predictionTime).toLocaleString()}</p>
                <p><strong>Total Predictions:</strong> ${predictionCount}</p>
        `;
        
        // Add model-specific metrics if available
        if (Object.keys(metrics).length > 0) {
            summaryHTML += '<div class="metrics"><h4>Metrics:</h4><ul>';
            for (const [key, value] of Object.entries(metrics)) {
                const formattedValue = typeof value === 'number' ? 
                    (Math.abs(value) < 0.0001 ? value.toExponential(2) : value.toFixed(4)) : 
                    value;
                summaryHTML += `<li>${formatColumnHeader(key)}: ${formattedValue}</li>`;
            }
            summaryHTML += '</ul></div>';
        }
        
        summaryHTML += '</div>';
        console.log('Setting summary HTML');
        summaryElement.innerHTML = summaryHTML;
        
        // Create download links - only if we have a model ID
        if (modelId) {
            // Important: Keep hyphens in the URL path for API endpoints
            const downloadHTML = `
                <p>Download predictions:</p>
                <a href="${API_BASE_URL}/predictions/${modelType}/${modelId}/download?format=csv" class="btn secondary" target="_blank">CSV</a>
                <a href="${API_BASE_URL}/predictions/${modelType}/${modelId}/download?format=json" class="btn secondary" target="_blank">JSON</a>
            `;
            console.log('Setting download HTML');
            downloadElement.innerHTML = downloadHTML;
        } else {
            downloadElement.innerHTML = '';
        }
        
        // Now display the prediction table with the updated references
        console.log('Displaying prediction table');
        displayPredictionTable(predictionData, modelType, tableElement, tableContainerElement);
    }
    
    function displayPredictionTable(predictionData, modelType, tableElement, tableContainerElement) {
        console.log('Displaying prediction table for data:', predictionData);
        
        // First check if relevant DOM elements exist
        if (!tableContainerElement) {
            console.error('ERROR: predictionTableContainer element not found in the DOM!');
            return;
        }
        
        if (!tableElement) {
            console.error('ERROR: predictionTable element not found in the DOM!');
            return;
        }
        
        console.log('DOM elements found:', {
            tableContainerElement, 
            tableElement,
            containerParent: tableContainerElement.parentElement,
            tableParent: tableElement.parentElement
        });
        
        // Extract predictions from different possible response formats
        let predictions = [];
        
        // Debug the structure of the prediction data
        console.log('Prediction table data type:', typeof predictionData);
        console.log('Is prediction data an array?', Array.isArray(predictionData));
        
        if (Array.isArray(predictionData)) {
            // Case 1: The predictionData itself is an array of predictions (direct API response)
            console.log('predictionData itself is an array of predictions, length:', predictionData.length);
            predictions = predictionData;
        } else if (predictionData.predictions && Array.isArray(predictionData.predictions)) {
            // Case 2: The predictions are in the predictions property as an array
            console.log('Found predictions as array in predictionData.predictions, length:', predictionData.predictions.length);
            predictions = predictionData.predictions;
        } else if (predictionData.data && predictionData.data.predictions && Array.isArray(predictionData.data.predictions)) {
            // Case 3: The predictions are nested in data.predictions
            console.log('Found predictions inside data.predictions, length:', predictionData.data.predictions.length);
            predictions = predictionData.data.predictions;
        } else {
            // Try to find any array in the object
            console.log('Searching for array data in prediction object...');
            for (const key in predictionData) {
                if (Array.isArray(predictionData[key]) && predictionData[key].length > 0) {
                    console.log(`Found array in property "${key}" with length ${predictionData[key].length}`);
                    // Only use this if it looks like prediction data (has objects with properties)
                    if (typeof predictionData[key][0] === 'object') {
                        predictions = predictionData[key];
                        console.log('Using this array as predictions');
                        break;
                    }
                }
            }
        }
        
        // Make sure container is visible
        tableContainerElement.style.display = 'block';
        
        // Clear any previous content
        console.log('Clearing predictionTable');               
        tableElement.innerHTML = '';
                       
        if (!predictions || !predictions.length) {
            console.warn('No predictions found in the response data');
            tableElement.innerHTML = '<tr><td><p>No prediction data available.</p></td></tr>';
            return;
        }
        
        console.log(`Found ${predictions.length} predictions to display`);
        console.log('First prediction:', predictions[0]);
        
        try {
            // Get all column headers from the first prediction
            const columnHeaders = Object.keys(predictions[0]);
            console.log('Column headers:', columnHeaders);
            
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
                    const cellValue = predictions[i][header];
                    // Format numbers to 4 decimal places if they're numeric
                    const formattedValue = typeof cellValue === 'number' ? 
                        (Math.abs(cellValue) < 0.0001 ? cellValue.toExponential(2) : cellValue.toFixed(4)) : 
                        (cellValue || '');
                    tableHTML += `<td>${formattedValue}</td>`;
                });
                tableHTML += '</tr>';
            }
            
            if (predictions.length > displayLimit) {
                tableHTML += `<tr><td colspan="${columnHeaders.length}">Showing ${displayLimit} of ${predictions.length} predictions. Download the full dataset to see all.</td></tr>`;
            }
            
            tableHTML += '</tbody>';
            
            // Set the table HTML with better error handling
            try {
                console.log('Setting table HTML:', tableHTML.substring(0, 200) + '...');
                tableElement.innerHTML = tableHTML;
                
                // Show the table with some animation to ensure it's visible
                tableContainerElement.style.opacity = '0';
                tableContainerElement.style.display = 'block';
                
                // Force reflow
                void tableContainerElement.offsetHeight;
                
                // Fade in
                tableContainerElement.style.transition = 'opacity 0.3s ease-in-out';
                tableContainerElement.style.opacity = '1';
                
                console.log('Table displayed successfully');
            } catch (innerError) {
                console.error('Error setting table HTML:', innerError);
                tableElement.innerHTML = `<tr><td><p class="error">Error displaying table: ${innerError.message}</p></td></tr>`;
            }
            
            // Verify the table was populated
            console.log('After update, predictionTable.innerHTML length:', tableElement.innerHTML.length);
            console.log('After update, predictionTable children count:', tableElement.childNodes.length);
            
        } catch (error) {
            console.error('Error displaying prediction table:', error);
            tableElement.innerHTML = `<tr><td><p class="error">Error displaying predictions: ${error.message}</p></td></tr>`;
        }
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

// Color Scheme Demo Toggle
document.addEventListener('DOMContentLoaded', function() {
    const toggleColorDemoBtn = document.getElementById('toggle-color-demo');
    const colorSchemeDemo = document.getElementById('color-scheme-demo');
    const closeColorDemo = document.getElementById('close-color-demo');
    
    if (toggleColorDemoBtn && colorSchemeDemo && closeColorDemo) {
        toggleColorDemoBtn.addEventListener('click', function() {
            colorSchemeDemo.style.display = 'block';
            // Prevent scrolling on the body when demo is visible
            document.body.style.overflow = 'hidden';
        });
        
        closeColorDemo.addEventListener('click', function() {
            colorSchemeDemo.style.display = 'none';
            // Re-enable scrolling
            document.body.style.overflow = '';
        });
        
        // Close on click outside the demo content
        window.addEventListener('click', function(event) {
            if (event.target === colorSchemeDemo) {
                colorSchemeDemo.style.display = 'none';
                document.body.style.overflow = '';
            }
        });
        
        // Allow escape key to close
        document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape' && colorSchemeDemo.style.display === 'block') {
                colorSchemeDemo.style.display = 'none';
                document.body.style.overflow = '';
            }
        });
    }
}); 