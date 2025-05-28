// API Base URL - Update this if your backend is running on a different host/port
const API_BASE_URL = 'http://localhost:8000/api';
// Gmail to S3 API Base URL
const GMAIL_S3_API_BASE_URL = 'http://localhost:8002';
// RIQ Rate API Base URL
const RIQ_API_BASE_URL = 'http://localhost:8006';

// Define global functions outside the document ready scope

/**
 * Toggle the visibility of a rate card's detailed content
 */
function toggleRateCard(cardId) {
    const content = document.getElementById(`${cardId}-content`);
    const icon = document.getElementById(`${cardId}-toggle-icon`);
    
    if (content && icon) {
        const isHidden = content.classList.contains('hidden');
        
        if (isHidden) {
            // Expand the card
            content.classList.remove('hidden');
            icon.innerHTML = '<i class="fas fa-chevron-up text-lg"></i>';
            icon.style.transform = 'rotate(180deg)';
        } else {
            // Collapse the card
            content.classList.add('hidden');
            icon.innerHTML = '<i class="fas fa-chevron-down text-lg"></i>';
            icon.style.transform = 'rotate(0deg)';
        }
    }
}

// Document ready function
document.addEventListener('DOMContentLoaded', () => {
    // Navigation and Sidebar
    const navLinks = document.querySelectorAll('.nav-link');
    const sections = document.querySelectorAll('#file-upload, #model-training, #model-list, #predictions, #riq-rate-quote');
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebarToggleCollapsed = document.getElementById('sidebar-toggle-collapsed');
    const sidebar = document.getElementById('sidebar');
    const sidebarToggleIcon = document.getElementById('sidebar-toggle-icon');
    const mainContent = document.getElementById('main-content');
    const header = document.getElementById('header');
    
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
    
    // Gmail Integration Elements
    const fetchEmailBtn = document.getElementById('fetch-email-btn');
    const emailAttachmentModal = document.getElementById('email-attachment-modal');
    const closeEmailModalBtn = document.getElementById('close-email-modal');
    const cancelEmailModalBtn = document.getElementById('cancel-email-modal-btn');
    const emailAuthText = document.getElementById('email-auth-text');
    const gmailLogoutBtn = document.getElementById('gmail-logout-btn');
    const emailsList = document.getElementById('emails-list');
    const attachmentsList = document.getElementById('attachments-list');
    const attachmentsSection = document.getElementById('attachments-section');
    const selectedEmailSubject = document.getElementById('selected-email-subject');
    const fetchAttachmentBtn = document.getElementById('fetch-attachment-btn');
    const emailModalStatus = document.getElementById('email-modal-status');
    const s3UploadCheckbox = document.getElementById('s3-upload-checkbox');
    const s3UploadStatus = document.getElementById('s3-upload-status');
    
    // RIQ Rate Quote Elements
    const quickQuoteToggle = document.getElementById('quick-quote-toggle');
    const fullQuoteToggle = document.getElementById('full-quote-toggle');
    const quickQuoteForm = document.getElementById('quick-quote-form');
    const fullQuoteForm = document.getElementById('full-quote-form');
    const addItemBtn = document.getElementById('add-item-btn');
    const itemsContainer = document.getElementById('items-container');
    const riqResult = document.getElementById('riq-result');
    const quoteResultsContainer = document.getElementById('quote-results-container');
    const quoteSummary = document.getElementById('quote-summary');
    const quoteOptionsContainer = document.getElementById('quote-options-container');
    
    // Gmail Integration Variables
    let currentMessageId = null;
    let currentAttachment = null;
    
    // RIQ Variables
    let itemCounter = 1;
    
    // Initialize the app
    init();
    
    // Functions
    function init() {
        console.log('Initializing application');
        
        // Debug: Check for button with ID 'fetch-email-btn'
        console.log('Looking for fetch-email-btn element');
        const fetchEmailBtnCheck = document.getElementById('fetch-email-btn');
        if (fetchEmailBtnCheck) {
            console.log('fetch-email-btn found:', fetchEmailBtnCheck);
        } else {
            console.error('fetch-email-btn NOT found!');
            console.log('All buttons on the page:');
            document.querySelectorAll('button').forEach(btn => {
                console.log(`Button: id="${btn.id}", text="${btn.textContent.trim()}", type="${btn.type}"`);
            });
        }
        
        setupNavigation();
        setupSidebar();
        setupEventListeners();
        loadUploadedFiles();
        loadModels();
        setupRIQ();
    }
    
    function setupNavigation() {
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const targetSection = link.getAttribute('data-section');
                
                // Remove active state from all nav links
                navLinks.forEach(navLink => {
                    navLink.classList.remove('bg-white/20', 'text-white');
                    navLink.classList.add('text-neutral-300');
                });
                
                // Hide all sections
                sections.forEach(section => {
                    section.classList.add('hidden');
                    section.classList.remove('block');
                });
                
                // Add active state to clicked nav link
                link.classList.remove('text-neutral-300');
                link.classList.add('bg-white/20', 'text-white');
                
                // Show target section
                const targetElement = document.getElementById(targetSection);
                if (targetElement) {
                    targetElement.classList.remove('hidden');
                    targetElement.classList.add('block');
                }
            });
        });
    }
    
    function setupSidebar() {
        if (!sidebarToggle || !sidebarToggleCollapsed || !sidebar || !sidebarToggleIcon || !mainContent || !header) {
            console.error('Some sidebar elements are missing!');
            return;
        }
        
        // Toggle sidebar between expanded and collapsed (from expanded state button)
        sidebarToggle.addEventListener('click', () => {
            collapseSidebar();
        });
        
        // Toggle sidebar between collapsed and expanded (from collapsed state button)
        sidebarToggleCollapsed.addEventListener('click', () => {
            expandSidebar();
        });
        
        // Initialize sidebar as expanded
        expandSidebar();
    }
    
    function toggleSidebar() {
        const isCollapsed = sidebar.classList.contains('w-16');
        
        if (isCollapsed) {
            expandSidebar();
        } else {
            collapseSidebar();
        }
    }
    
    function expandSidebar() {
        // Update sidebar width
        sidebar.classList.remove('w-16');
        sidebar.classList.add('w-64');
        
        // Show expanded header content and hide collapsed header
        const expandedHeader = document.querySelector('.sidebar-expanded-header');
        const collapsedHeader = document.querySelector('.sidebar-collapsed-header');
        if (expandedHeader) expandedHeader.classList.remove('hidden');
        if (collapsedHeader) collapsedHeader.classList.add('hidden');
        
        // Show text elements in navigation and footer
        const sidebarTexts = document.querySelectorAll('.sidebar-text');
        sidebarTexts.forEach(text => text.classList.remove('hidden'));
        
        // Update main content and header margins
        mainContent.classList.remove('ml-16');
        mainContent.classList.add('ml-64');
        header.classList.remove('left-16');
        header.classList.add('left-64');
    }
    
    function collapseSidebar() {
        // Update sidebar width
        sidebar.classList.remove('w-64');
        sidebar.classList.add('w-16');
        
        // Hide expanded header content and show collapsed header
        const expandedHeader = document.querySelector('.sidebar-expanded-header');
        const collapsedHeader = document.querySelector('.sidebar-collapsed-header');
        if (expandedHeader) expandedHeader.classList.add('hidden');
        if (collapsedHeader) collapsedHeader.classList.remove('hidden');
        
        // Hide text elements in navigation and footer
        const sidebarTexts = document.querySelectorAll('.sidebar-text');
        sidebarTexts.forEach(text => text.classList.add('hidden'));
        
        // Update main content and header margins
        mainContent.classList.remove('ml-64');
        mainContent.classList.add('ml-16');
        header.classList.remove('left-64');
        header.classList.add('left-16');
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
            modelDetailsModal.classList.add('hidden');
        });
        
        window.addEventListener('click', (e) => {
            if (e.target === modelDetailsModal) {
                modelDetailsModal.classList.add('hidden');
            }
        });
        
        // Predictions
        predictionModelType.addEventListener('change', handlePredictionModelTypeChange);
        predictionForm.addEventListener('submit', handlePredictionGeneration);
        
        // Gmail Integration
        console.log('Setting up Gmail integration event listeners');
        
        // Verify the fetch email button exists
        if (fetchEmailBtn) {
            console.log('Fetch Email button found, attaching click event listener');
            fetchEmailBtn.addEventListener('click', handleFetchEmailClick);
            console.log('Click event listener attached to Fetch Email button');
        } else {
            console.error('Fetch Email button not found in the DOM');
        }
        
        // Email Modal Close
        if (closeEmailModalBtn) {
            closeEmailModalBtn.addEventListener('click', () => {
                emailAttachmentModal.classList.add('hidden');
            });
        }
        
        if (cancelEmailModalBtn) {
            cancelEmailModalBtn.addEventListener('click', () => {
                emailAttachmentModal.classList.add('hidden');
            });
        }
        
        window.addEventListener('click', (e) => {
            if (e.target === emailAttachmentModal) {
                emailAttachmentModal.classList.add('hidden');
            }
        });
        
        // Gmail Logout
        if (gmailLogoutBtn) {
            gmailLogoutBtn.addEventListener('click', handleGmailLogout);
        }
        
        // Fetch Attachment Button
        if (fetchAttachmentBtn) {
            fetchAttachmentBtn.addEventListener('click', handleFetchAttachment);
        }
        
        // RIQ Rate Quote
        if (quickQuoteToggle && fullQuoteToggle) {
            quickQuoteToggle.addEventListener('click', () => switchQuoteMode('quick'));
            fullQuoteToggle.addEventListener('click', () => switchQuoteMode('full'));
        }
        
        if (quickQuoteForm) {
            quickQuoteForm.addEventListener('submit', handleQuickQuote);
        }
        
        if (fullQuoteForm) {
            fullQuoteForm.addEventListener('submit', handleFullQuote);
        }
        
        if (addItemBtn) {
            addItemBtn.addEventListener('click', addNewItem);
        }
        
        // Event delegation for remove item buttons (dynamically added)
        if (itemsContainer) {
            itemsContainer.addEventListener('click', (e) => {
                if (e.target.closest('.remove-item-btn')) {
                    removeItem(e.target.closest('.item-row'));
                }
            });
        }
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
            filePreviewContainer.classList.add('hidden');
            
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
            loadingElement.className = 'flex items-center justify-center py-4';
            loadingElement.innerHTML = '<div class="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600 mr-3"></div><span class="text-neutral-600">Loading preview...</span>';
            uploadResult.appendChild(loadingElement);
            
            // Fetch file preview data from API
            const response = await fetch(`${API_BASE_URL}/data/preview/${fileId}`);
            const data = await response.json();
            
            // Remove loading indicator
            uploadResult.querySelector('.flex.items-center.justify-center.py-4').remove();
            
            if (response.ok) {
                // Show the preview container
                filePreviewContainer.classList.remove('hidden');
                
                // Display the file preview
                displayFilePreview(data);
            } else {
                const errorMessage = document.createElement('div');
                errorMessage.className = 'bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mt-4';
                errorMessage.textContent = `Preview failed: ${data.error || data.message || 'Unknown error'}`;
                uploadResult.appendChild(errorMessage);
            }
        } catch (error) {
            const errorMessage = document.createElement('div');
            errorMessage.className = 'bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mt-4';
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
        trainingFileSelect.innerHTML = '<option value="">Select a file</option>';
        
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
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div><span class="font-medium text-neutral-700">File ID:</span> <span class="text-neutral-600">${previewData.file_id}</span></div>
                <div><span class="font-medium text-neutral-700">Total Rows:</span> <span class="text-neutral-600">${previewData.total_rows}</span></div>
                <div><span class="font-medium text-neutral-700">Total Columns:</span> <span class="text-neutral-600">${previewData.total_columns}</span></div>
                <div><span class="font-medium text-neutral-700">Missing Data:</span> <span class="text-neutral-600">${previewData.missing_data_summary.total_missing} cells (${previewData.missing_data_summary.percent_missing}%)</span></div>
            </div>
        `;
        
        // Set up table headers
        const columnHeaders = Object.keys(previewData.sample_rows[0] || {});
        let tableHTML = '<thead class="bg-neutral-50"><tr>';
        columnHeaders.forEach(header => {
            tableHTML += `<th class="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">${header}</th>`;
        });
        tableHTML += '</tr></thead><tbody class="bg-white divide-y divide-neutral-200">';
        
        // Add sample rows
        previewData.sample_rows.forEach(row => {
            tableHTML += '<tr class="hover:bg-neutral-50">';
            columnHeaders.forEach(header => {
                tableHTML += `<td class="px-6 py-4 whitespace-nowrap text-sm text-neutral-900">${row[header] || ''}</td>`;
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
        statusElement.className = 'bg-blue-50 border border-blue-200 text-blue-700 px-4 py-3 rounded-lg mt-4';
        statusElement.innerHTML = '<div class="flex items-center"><div class="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-3"></div><span>Waiting for model training to complete...</span></div>';
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
                        statusElement.className = 'bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg mt-4';
                        statusElement.innerHTML = `
                            <div class="space-y-3">
                                <p class="font-medium">Model training completed!</p>
                                <div class="text-sm space-y-1">
                                    <p><span class="font-medium">Model ID:</span> ${matchedModel.model_id}</p>
                                    <p><span class="font-medium">Created:</span> ${new Date(matchedModel.created_at).toLocaleString()}</p>
                                    <div>
                                        <p class="font-medium">Performance metrics:</p>
                                        <ul class="list-disc list-inside ml-4 space-y-1">
                                            ${Object.entries(matchedModel.evaluation || {}).map(([key, value]) => 
                                                `<li>${key}: ${typeof value === 'number' ? value.toFixed(4) : value}</li>`
                                            ).join('')}
                                        </ul>
                                    </div>
                                </div>
                                <button id="view-trained-model" class="inline-flex items-center px-4 py-2 bg-primary-600 text-white font-medium rounded-lg hover:bg-primary-700 transition-colors">View Model Details</button>
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
                                    modelRow.classList.add('bg-blue-50', 'border-l-4', 'border-blue-400');
                                    modelRow.scrollIntoView({ behavior: 'smooth', block: 'center' });
                                    
                                    // Remove highlight after a few seconds
                                    setTimeout(() => {
                                        modelRow.classList.remove('bg-blue-50', 'border-l-4', 'border-blue-400');
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
            if (statusElement.querySelector('.animate-spin')) {
                clearInterval(pollInterval);
                statusElement.className = 'bg-yellow-50 border border-yellow-200 text-yellow-700 px-4 py-3 rounded-lg mt-4';
                statusElement.innerHTML = `
                    <p>Model training is taking longer than expected. Please check the Models tab later for your trained model.</p>
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
            modelsTableBody.innerHTML = `<tr><td colspan="5" class="px-6 py-4 text-center text-neutral-500">No models available</td></tr>`;
            return;
        }
        
        models.forEach(model => {
            const row = document.createElement('tr');
            row.className = 'hover:bg-neutral-50';
            // Add data attribute for model ID to help with highlighting
            row.setAttribute('data-model-id', model.model_id);
            
            // Format metrics
            let metricsHTML = '<ul class="text-sm space-y-1">';
            for (const [key, value] of Object.entries(model.evaluation || {})) {
                const formattedValue = typeof value === 'number' ? value.toFixed(4) : value;
                metricsHTML += `<li><span class="font-medium">${key}:</span> ${formattedValue}</li>`;
            }
            metricsHTML += '</ul>';
            
            row.innerHTML = `
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-neutral-900">${model.model_id}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-neutral-500">${model.model_type}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-neutral-500">${new Date(model.created_at).toLocaleString()}</td>
                <td class="px-6 py-4 text-sm text-neutral-500">${metricsHTML}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                    <button class="view-model-btn inline-flex items-center px-3 py-1 bg-neutral-600 text-white text-sm font-medium rounded hover:bg-neutral-700 transition-colors" data-model-id="${model.model_id}">Details</button>
                    <button class="predict-model-btn inline-flex items-center px-3 py-1 bg-primary-600 text-white text-sm font-medium rounded hover:bg-primary-700 transition-colors" data-model-id="${model.model_id}" data-model-type="${model.model_type}">Predict</button>
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
            modelDetailsModal.classList.remove('hidden');
            
            const response = await fetch(`${API_BASE_URL}/models/${modelId}`);
            const data = await response.json();
            
            if (response.ok) {
                displayModelDetails(data);
            } else {
                modelDetailsContent.innerHTML = `<div class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">Failed to load model details: ${data.error || 'Unknown error'}</div>`;
            }
        } catch (error) {
            modelDetailsContent.innerHTML = `<div class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">Error loading model details: ${error.message}</div>`;
        }
    }
    
    function displayModelDetails(model) {
        // Format training parameters
        let trainingParamsHTML = '<ul class="space-y-1">';
        for (const [key, value] of Object.entries(model.training_params || {})) {
            trainingParamsHTML += `<li><span class="font-medium">${key}:</span> ${value}</li>`;
        }
        trainingParamsHTML += '</ul>';
        
        // Format evaluation metrics
        let evaluationHTML = '<ul class="space-y-1">';
        for (const [key, value] of Object.entries(model.evaluation || {})) {
            evaluationHTML += `<li><span class="font-medium">${key}:</span> ${value}</li>`;
        }
        evaluationHTML += '</ul>';
        
        modelDetailsContent.innerHTML = `
            <div class="space-y-6">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <h3 class="text-lg font-medium text-neutral-900 mb-3">Basic Information</h3>
                        <div class="space-y-2 text-sm">
                            <p><span class="font-medium text-neutral-700">Model ID:</span> <span class="text-neutral-600">${model.model_id}</span></p>
                            <p><span class="font-medium text-neutral-700">Model Type:</span> <span class="text-neutral-600">${model.model_type}</span></p>
                            <p><span class="font-medium text-neutral-700">Created:</span> <span class="text-neutral-600">${new Date(model.created_at).toLocaleString()}</span></p>
                            <p><span class="font-medium text-neutral-700">Description:</span> <span class="text-neutral-600">${model.description || 'No description provided'}</span></p>
                            <p><span class="font-medium text-neutral-700">Training Data:</span> <span class="text-neutral-600">${model.training_data || 'Unknown'}</span></p>
                        </div>
                    </div>
                    
                    <div>
                        <h3 class="text-lg font-medium text-neutral-900 mb-3">Training Parameters</h3>
                        <div class="text-sm text-neutral-600">
                            ${trainingParamsHTML}
                        </div>
                    </div>
                </div>
                
                <div>
                    <h3 class="text-lg font-medium text-neutral-900 mb-3">Evaluation Metrics</h3>
                    <div class="text-sm text-neutral-600">
                        ${evaluationHTML}
                    </div>
                </div>
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
        predictionModelSelect.innerHTML = '<option value="">Select a model</option>';
        
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
                    <div>
                        <h4 class="text-lg font-medium text-neutral-900 mb-4">Order Volume Parameters</h4>
                        <div>
                            <label for="months-ahead" class="block text-sm font-medium text-neutral-700 mb-2">Months to Predict:</label>
                            <input type="number" id="months-ahead" value="6" min="1" max="12" class="w-full px-4 py-3 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors">
                        </div>
                    </div>
                `;
                break;
                
            case 'tender-performance':
                paramsHTML = `
                    <div>
                        <h4 class="text-lg font-medium text-neutral-900 mb-4">Tender Performance Parameters</h4>
                        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div>
                                <label for="source-city" class="block text-sm font-medium text-neutral-700 mb-2">Source City (optional):</label>
                                <input type="text" id="source-city" placeholder="Filter by source city" class="w-full px-4 py-3 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors">
                            </div>
                            <div>
                                <label for="dest-city" class="block text-sm font-medium text-neutral-700 mb-2">Destination City (optional):</label>
                                <input type="text" id="dest-city" placeholder="Filter by destination city" class="w-full px-4 py-3 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors">
                            </div>
                            <div>
                                <label for="carrier" class="block text-sm font-medium text-neutral-700 mb-2">Carrier (optional):</label>
                                <input type="text" id="carrier" placeholder="Filter by carrier" class="w-full px-4 py-3 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors">
                            </div>
                        </div>
                    </div>
                `;
                break;
                
            case 'carrier-performance':
                paramsHTML = `
                    <div>
                        <h4 class="text-lg font-medium text-neutral-900 mb-4">Carrier Performance Parameters</h4>
                        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div>
                                <label for="cp-source-city" class="block text-sm font-medium text-neutral-700 mb-2">Source City (optional):</label>
                                <input type="text" id="cp-source-city" placeholder="Filter by source city" class="w-full px-4 py-3 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors">
                            </div>
                            <div>
                                <label for="cp-dest-city" class="block text-sm font-medium text-neutral-700 mb-2">Destination City (optional):</label>
                                <input type="text" id="cp-dest-city" placeholder="Filter by destination city" class="w-full px-4 py-3 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors">
                            </div>
                            <div>
                                <label for="cp-carrier" class="block text-sm font-medium text-neutral-700 mb-2">Carrier (optional):</label>
                                <input type="text" id="cp-carrier" placeholder="Filter by carrier" class="w-full px-4 py-3 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors">
                            </div>
                        </div>
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
        const loadingElement = predictionResult.querySelector('.flex.items-center.justify-center');
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
                    <table id="prediction-table" class="min-w-full bg-white border border-neutral-200 rounded-lg overflow-hidden mt-6"></table>
                </div>
                <div id="prediction-download" class="mt-6"></div>
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
            <div class="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
                <h3 class="text-lg font-medium text-blue-900 mb-4">Prediction Summary</h3>
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
                    <div><span class="font-medium text-blue-800">Prediction ID:</span> <span class="text-blue-700">${predictionId || 'N/A'}</span></div>
                    <div><span class="font-medium text-blue-800">Model ID:</span> <span class="text-blue-700">${modelId || 'N/A'}</span></div>
                    <div><span class="font-medium text-blue-800">Created:</span> <span class="text-blue-700">${new Date(predictionTime).toLocaleString()}</span></div>
                    <div><span class="font-medium text-blue-800">Total Predictions:</span> <span class="text-blue-700">${predictionCount}</span></div>
                </div>
        `;
        
        // Add model-specific metrics if available
        if (Object.keys(metrics).length > 0) {
            summaryHTML += '<div class="mt-4"><h4 class="font-medium text-blue-800 mb-2">Metrics:</h4><ul class="space-y-1 text-sm">';
            for (const [key, value] of Object.entries(metrics)) {
                const formattedValue = typeof value === 'number' ? 
                    (Math.abs(value) < 0.0001 ? value.toExponential(2) : value.toFixed(4)) : 
                    value;
                summaryHTML += `<li class="text-blue-700"><span class="font-medium">${formatColumnHeader(key)}:</span> ${formattedValue}</li>`;
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
                <div class="bg-neutral-50 border border-neutral-200 rounded-lg p-4">
                    <h4 class="font-medium text-neutral-900 mb-3">Download Predictions</h4>
                    <div class="flex space-x-3">
                        <a href="${API_BASE_URL}/predictions/${modelType}/${modelId}/download?format=csv" class="inline-flex items-center px-4 py-2 bg-neutral-600 text-white font-medium rounded-lg hover:bg-neutral-700 transition-colors" target="_blank">
                            <i class="fas fa-download mr-2"></i>
                            CSV
                        </a>
                        <a href="${API_BASE_URL}/predictions/${modelType}/${modelId}/download?format=json" class="inline-flex items-center px-4 py-2 bg-neutral-600 text-white font-medium rounded-lg hover:bg-neutral-700 transition-colors" target="_blank">
                            <i class="fas fa-download mr-2"></i>
                            JSON
                        </a>
                    </div>
                </div>
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
            tableElement.innerHTML = '<tr><td class="px-6 py-4 text-center text-neutral-500 col-span-full">No prediction data available.</td></tr>';
            return;
        }
        
        console.log(`Found ${predictions.length} predictions to display`);
        console.log('First prediction:', predictions[0]);
        
        try {
            // Get all column headers from the first prediction
            const columnHeaders = Object.keys(predictions[0]);
            console.log('Column headers:', columnHeaders);
            
            let tableHTML = '<thead class="bg-neutral-50"><tr>';
            columnHeaders.forEach(header => {
                tableHTML += `<th class="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">${formatColumnHeader(header)}</th>`;
            });
            tableHTML += '</tr></thead><tbody class="bg-white divide-y divide-neutral-200">';
            
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
                    tableHTML += `<td class="px-6 py-4 whitespace-nowrap text-sm text-neutral-900">${formattedValue}</td>`;
                });
                tableHTML += '</tr>';
            }
            
            if (predictions.length > displayLimit) {
                tableHTML += `<tr><td colspan="${columnHeaders.length}" class="px-6 py-4 text-center text-neutral-500">Showing ${displayLimit} of ${predictions.length} predictions. Download the full dataset to see all.</td></tr>`;
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
                tableElement.innerHTML = `<tr><td class="px-6 py-4 text-center text-red-600 col-span-full">Error displaying table: ${innerError.message}</td></tr>`;
            }
            
            // Verify the table was populated
            console.log('After update, predictionTable.innerHTML length:', tableElement.innerHTML.length);
            console.log('After update, predictionTable children count:', tableElement.childNodes.length);
            
        } catch (error) {
            console.error('Error displaying prediction table:', error);
            tableElement.innerHTML = `<tr><td class="px-6 py-4 text-center text-red-600 col-span-full">Error displaying predictions: ${error.message}</td></tr>`;
        }
    }
    
    // Utility Functions
    function showLoading(element) {
        element.innerHTML = '<div class="flex items-center justify-center py-8"><div class="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600 mr-3"></div><span class="text-neutral-600">Loading...</span></div>';
    }
    
    function showError(element, message) {
        element.innerHTML = `<div class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">${message}</div>`;
    }
    
    function showSuccess(element, message) {
        element.innerHTML = `<div class="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg">${message}</div>`;
    }
    
    function showInfo(element, message) {
        element.innerHTML = `<div class="bg-blue-50 border border-blue-200 text-blue-700 px-4 py-3 rounded-lg">${message}</div>`;
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
    
    // Gmail Integration Functions
    
    /**
     * Checks the authentication status with the Gmail API
     * @returns {Promise<boolean>} True if authenticated, false otherwise
     */
    async function checkGmailAuthStatus() {
        try {
            console.log('Starting checkGmailAuthStatus function');
            emailAuthText.textContent = 'Checking authentication status...';
            
            console.log('Making API request to:', `${GMAIL_S3_API_BASE_URL}/auth/status`);
            const response = await fetch(`${GMAIL_S3_API_BASE_URL}/auth/status`, {
                method: 'GET',
                mode: 'cors',
                headers: {
                    'Accept': 'application/json'
                }
            });
            console.log('API response status:', response.status);
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: response.statusText }));
                console.error('API error response:', errorData);
                throw new Error(errorData.detail || 'Failed to check auth status');
            }
            
            const data = await response.json();
            console.log('API response data:', data);
            
            if (data.authenticated) {
                console.log('User is authenticated');
                emailAuthText.textContent = 'Status: Authenticated';
                gmailLogoutBtn.classList.remove('hidden');
                return true;
            } else {
                console.log('User is not authenticated');
                emailAuthText.textContent = 'Status: Not Authenticated';
                gmailLogoutBtn.classList.add('hidden');
                return false;
            }
        } catch (error) {
            console.error('Error in checkGmailAuthStatus:', error);
            emailAuthText.textContent = `Status: Error checking authentication (${error.message})`;
            gmailLogoutBtn.classList.add('hidden');
            return false;
        }
    }
    
    /**
     * Handles click on the "Fetch Attachment from Email" button
     */
    async function handleFetchEmailClick() {
        console.log('Fetch Email button clicked!');
        
        // Reset the modal state
        resetEmailModal();
        
        try {
            console.log('Checking Gmail authentication status...');
            // Check if authenticated with Gmail
            const isAuthenticated = await checkGmailAuthStatus();
            console.log('Authentication status:', isAuthenticated);
            
            if (isAuthenticated) {
                console.log('User is authenticated, opening email selection modal');
                // Open the email selection modal and list emails
                openEmailSelectionModal();
            } else {
                console.log('User is not authenticated, opening login page');
                // Open the Gmail login page in a new tab
                window.open('gmail_login.html', '_blank');
                
                // Show a message to the user
                showInfo(uploadResult, 'Please authenticate with Gmail in the new tab. After authentication, close that tab and click "Fetch from Email" again.');
            }
        } catch (error) {
            console.error('Error in handleFetchEmailClick:', error);
            showError(uploadResult, `Error: ${error.message}`);
        }
    }
    
    /**
     * Handles Gmail logout
     */
    async function handleGmailLogout() {
        try {
            emailAuthText.textContent = 'Logging out...';
            
            const response = await fetch(`${GMAIL_S3_API_BASE_URL}/auth/logout`, {
                method: 'POST'
            });
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: response.statusText }));
                throw new Error(errorData.detail || 'Failed to logout');
            }
            
            const data = await response.json();
            
            // Update UI
            emailAuthText.textContent = 'Status: Logged out';
            gmailLogoutBtn.classList.add('hidden');
            
            // Reset modal
            resetEmailModal();
            
            // Show success message in the modal status
            showModalSuccess(data.message || 'Logged out successfully');
        } catch (error) {
            emailAuthText.textContent = 'Status: Error during logout';
            showModalError(`Logout error: ${error.message}`);
            console.error('Logout error:', error);
        }
    }
    
    /**
     * Resets the email modal to its initial state
     */
    function resetEmailModal() {
        // Reset email list
        emailsList.innerHTML = '<div class="flex items-center justify-center py-8"><div class="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600"></div><span class="ml-3 text-neutral-600">Loading emails...</span></div>';
        
        // Reset attachments section
        attachmentsSection.classList.add('hidden');
        attachmentsList.innerHTML = '<div class="flex items-center justify-center py-8"><div class="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600"></div><span class="ml-3 text-neutral-600">Loading attachments...</span></div>';
        selectedEmailSubject.textContent = 'None';
        
        // Reset status
        emailModalStatus.classList.add('hidden');
        emailModalStatus.textContent = '';
        emailModalStatus.className = 'hidden';
        
        // Reset S3 upload status
        if (s3UploadStatus) {
            s3UploadStatus.classList.add('hidden');
            s3UploadStatus.textContent = '';
            s3UploadStatus.className = 'hidden';
        }
        
        // Reset selected items
        currentMessageId = null;
        currentAttachment = null;
        
        // Disable fetch button
        fetchAttachmentBtn.disabled = true;
    }
    
    /**
     * Shows success message in the email modal status area
     */
    function showModalSuccess(message) {
        emailModalStatus.className = 'bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg mt-4';
        emailModalStatus.textContent = message;
        emailModalStatus.classList.remove('hidden');
    }
    
    /**
     * Shows error message in the email modal status area
     */
    function showModalError(message) {
        emailModalStatus.className = 'bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mt-4';
        emailModalStatus.textContent = message;
        emailModalStatus.classList.remove('hidden');
    }
    
    /**
     * Shows loading message in the email modal status area
     */
    function showModalLoading(message) {
        emailModalStatus.className = 'bg-blue-50 border border-blue-200 text-blue-700 px-4 py-3 rounded-lg mt-4';
        emailModalStatus.textContent = message;
        emailModalStatus.classList.remove('hidden');
    }
    
    /**
     * Opens the email selection modal and lists emails
     */
    function openEmailSelectionModal() {
        // Show the modal
        emailAttachmentModal.classList.remove('hidden');
        
        // List emails
        listGmailEmails();
    }
    
    /**
     * Fetches and displays emails from Gmail
     */
    async function listGmailEmails() {
        try {
            console.log('Fetching emails from Gmail API');
            showModalLoading('Fetching emails...');
            
            // Clear previous emails
            emailsList.innerHTML = '<div class="flex items-center justify-center py-8"><div class="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600"></div><span class="ml-3 text-neutral-600">Loading emails...</span></div>';
            
            // Fetch emails from the API
            const response = await fetch(`${GMAIL_S3_API_BASE_URL}/api/emails`, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json'
                }
            });
            
            console.log('API response status:', response.status);
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: response.statusText }));
                console.error('API error response:', errorData);
                throw new Error(errorData.detail || 'Failed to fetch emails');
            }
            
            const data = await response.json();
            console.log('Emails fetched:', data);
            
            // Check if we have emails
            // The API returns an array directly, not an object with an 'emails' property
            const emails = Array.isArray(data) ? data : (data.emails || []);
            
            if (emails.length === 0) {
                emailsList.innerHTML = '<div class="bg-blue-50 border border-blue-200 text-blue-700 px-4 py-3 rounded-lg">No emails found with attachments.</div>';
                showModalInfo('No emails found with attachments');
                return;
            }
            
            // Display emails
            displayEmailsList(emails);
            showModalSuccess(`Found ${emails.length} emails with attachments`);
            
        } catch (error) {
            console.error('Error fetching emails:', error);
            emailsList.innerHTML = `<div class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">Error fetching emails: ${error.message}</div>`;
            showModalError(`Error fetching emails: ${error.message}`);
        }
    }
    
    /**
     * Displays the list of emails in the modal
     * @param {Array} emails - List of emails from the API
     */
    function displayEmailsList(emails) {
        // Clear previous list
        emailsList.innerHTML = '';
        
        // Create list of emails
        const list = document.createElement('ul');
        list.className = 'divide-y divide-neutral-200';
        
        emails.forEach(email => {
            const item = document.createElement('li');
            item.className = 'p-4 hover:bg-neutral-50 cursor-pointer transition-colors';
            
            // Format the date
            const date = new Date(email.date);
            const formattedDate = date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
            
            // Create email item content
            item.innerHTML = `
                <div class="flex items-center justify-between mb-2">
                    <span class="font-medium text-neutral-900 truncate flex-1">${email.subject || 'No Subject'}</span>
                    <span class="text-sm text-neutral-500 ml-2">${formattedDate}</span>
                </div>
                <div class="flex items-center justify-between text-sm text-neutral-600">
                    <span class="truncate flex-1">From: ${email.from || 'Unknown'}</span>
                    <span class="ml-2">Attachments: ${email.attachments_count || (email.has_target_attachments ? 'Yes' : 'Unknown')}</span>
                </div>
            `;
            
            // Add click event to select this email
            item.addEventListener('click', () => selectEmail(email));
            
            // Add data attribute for message ID (handle both formats)
            const messageId = email.message_id || email.id;
            item.setAttribute('data-message-id', messageId);
            
            list.appendChild(item);
        });
        
        emailsList.appendChild(list);
    }
    
    /**
     * Handles email selection and fetches its attachments
     * @param {Object} email - The selected email object
     */
    async function selectEmail(email) {
        try {
            console.log('Email selected:', email);
            
            // Update current message ID
            currentMessageId = email.message_id || email.id; // Handle both formats
            
            // Update UI to show selected email
            selectedEmailSubject.textContent = email.subject || 'No Subject';
            
            // Highlight the selected email
            const emailItems = document.querySelectorAll('.email-item');
            emailItems.forEach(item => {
                if (item.getAttribute('data-message-id') === currentMessageId) {
                    item.classList.add('selected');
                } else {
                    item.classList.remove('selected');
                }
            });
            
            // Show attachments section
            attachmentsSection.classList.remove('hidden');
            
            // Clear previous attachments
            attachmentsList.innerHTML = '<div class="flex items-center justify-center py-8"><div class="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600"></div><span class="ml-3 text-neutral-600">Loading attachments...</span></div>';
            
            // Show loading status
            showModalLoading('Fetching attachments...');
            
            // Fetch attachments for this email
            const response = await fetch(`${GMAIL_S3_API_BASE_URL}/api/emails/${currentMessageId}/attachments`, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json'
                }
            });
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: response.statusText }));
                console.error('API error response:', errorData);
                throw new Error(errorData.detail || 'Failed to fetch attachments');
            }
            
            const data = await response.json();
            console.log('Attachments fetched:', data);
            
            // Check if we have attachments
            // The API returns an array directly, not an object with an 'attachments' property
            const attachments = Array.isArray(data) ? data : (data.attachments || []);
            
            if (attachments.length === 0) {
                attachmentsList.innerHTML = '<div class="bg-blue-50 border border-blue-200 text-blue-700 px-4 py-3 rounded-lg">No attachments found in this email.</div>';
                showModalInfo('No attachments found in this email');
                return;
            }
            
            // Display attachments
            displayAttachmentsList(attachments);
            showModalSuccess(`Found ${attachments.length} attachments`);
            
        } catch (error) {
            console.error('Error selecting email:', error);
            attachmentsList.innerHTML = `<div class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">Error fetching attachments: ${error.message}</div>`;
            showModalError(`Error fetching attachments: ${error.message}`);
        }
    }
    
    /**
     * Displays the list of attachments for the selected email
     * @param {Array} attachments - List of attachments from the API
     */
    function displayAttachmentsList(attachments) {
        // Clear previous list
        attachmentsList.innerHTML = '';
        
        // Create list of attachments
        const list = document.createElement('ul');
        list.className = 'divide-y divide-neutral-200';
        
        attachments.forEach(attachment => {
            const item = document.createElement('li');
            item.className = 'p-4 hover:bg-neutral-50 cursor-pointer transition-colors';
            
            // Format file size
            const fileSize = formatFileSize(attachment.size);
            
            // Create attachment item content
            item.innerHTML = `
                <div class="flex items-center justify-between mb-2">
                    <span class="font-medium text-neutral-900 truncate flex-1">${attachment.filename || 'Unnamed attachment'}</span>
                    <span class="text-sm text-neutral-500 ml-2">${fileSize}</span>
                </div>
                <div class="text-sm text-neutral-600">
                    <span class="italic">${attachment.mime_type || 'Unknown type'}</span>
                </div>
            `;
            
            // Add click event to select this attachment
            item.addEventListener('click', () => selectAttachment(attachment));
            
            // Add data attribute for attachment ID (handle both formats)
            const attachmentId = attachment.attachment_id || attachment.id;
            item.setAttribute('data-attachment-id', attachmentId);
            
            list.appendChild(item);
        });
        
        attachmentsList.appendChild(list);
    }
    
    /**
     * Handles attachment selection
     * @param {Object} attachment - The selected attachment object
     */
    function selectAttachment(attachment) {
        console.log('Attachment selected:', attachment);
        
        // Update current attachment
        currentAttachment = attachment;
        
        // Get the attachment ID (handle both formats)
        const attachmentId = attachment.attachment_id || attachment.id;
        
        // Highlight the selected attachment
        const attachmentItems = document.querySelectorAll('.attachment-item');
        attachmentItems.forEach(item => {
            if (item.getAttribute('data-attachment-id') === attachmentId) {
                item.classList.add('selected');
            } else {
                item.classList.remove('selected');
            }
        });
        
        // Enable the fetch attachment button
        fetchAttachmentBtn.disabled = false;
        
        // Show info about the selected attachment
        showModalInfo(`Selected: ${attachment.filename || 'Unnamed attachment'}`);
    }
    
    /**
     * Formats file size in bytes to a human-readable format
     * @param {number} bytes - File size in bytes
     * @returns {string} Formatted file size
     */
    function formatFileSize(bytes) {
        if (!bytes || isNaN(bytes)) return 'Unknown size';
        
        const units = ['B', 'KB', 'MB', 'GB', 'TB'];
        let size = bytes;
        let unitIndex = 0;
        
        while (size >= 1024 && unitIndex < units.length - 1) {
            size /= 1024;
            unitIndex++;
        }
        
        return `${size.toFixed(1)} ${units[unitIndex]}`;
    }
    
    /**
     * Handles fetching the selected attachment and uploading it to the Neural backend
     */
    async function handleFetchAttachment() {
        try {
            // Check if we have a selected attachment
            if (!currentMessageId || !currentAttachment) {
                showModalError('Please select an attachment first');
                return;
            }
            
            // Show loading status
            showModalLoading('Downloading attachment...');
            
            // Get attachment ID (handle both formats)
            const attachmentId = currentAttachment.attachment_id || currentAttachment.id;
            
            // Get attachment filename and mime type
            const filename = currentAttachment.filename || 'unnamed_attachment';
            const mimeType = currentAttachment.mime_type || 'application/octet-stream';
            
            console.log('Fetching attachment:', {
                messageId: currentMessageId,
                attachmentId: attachmentId,
                filename: filename,
                mimeType: mimeType
            });
            
            // Construct the URL with expected_filename and expected_mime_type parameters
            const downloadUrl = `${GMAIL_S3_API_BASE_URL}/api/emails/${currentMessageId}/attachments/${attachmentId}?expected_filename=${encodeURIComponent(filename)}&expected_mime_type=${encodeURIComponent(mimeType)}`;
            
            // Fetch the attachment data
            const response = await fetch(downloadUrl);
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: response.statusText }));
                console.error('API error response:', errorData);
                throw new Error(errorData.detail || 'Failed to download attachment');
            }
            
            // Get the attachment as a blob
            const blob = await response.blob();
            console.log('Attachment downloaded as blob:', blob);
            
            // Check if S3 upload is requested
            const shouldUploadToS3 = s3UploadCheckbox && s3UploadCheckbox.checked;
            
            // If S3 upload is requested, show the S3 upload status area
            if (shouldUploadToS3) {
                s3UploadStatus.classList.remove('hidden');
                showS3Loading('Preparing to upload to S3...');
            }
            
            // Update status for Neural backend upload
            showModalLoading('Uploading attachment to Neural backend...');
            
            // Create a File object from the blob
            const file = new File([blob], filename, { type: mimeType });
            
            // Create FormData for the upload
            const formData = new FormData();
            formData.append('file', file);
            
            // Upload to the Neural API
            const uploadResponse = await fetch(`${API_BASE_URL}/files/upload`, {
                method: 'POST',
                body: formData
            });
            
            if (!uploadResponse.ok) {
                const errorData = await uploadResponse.json().catch(() => ({ detail: uploadResponse.statusText }));
                console.error('Upload API error response:', errorData);
                throw new Error(errorData.detail || 'Failed to upload attachment to Neural backend');
            }
            
            const uploadData = await uploadResponse.json();
            console.log('Upload successful:', uploadData);
            
            // Show success message for Neural backend upload
            showModalSuccess(`Attachment "${filename}" uploaded successfully to Neural backend!`);
            
            // Handle S3 upload if requested
            if (shouldUploadToS3) {
                try {
                    showS3Loading('Uploading attachment to S3...');
                    
                    // Construct the S3 upload URL
                    const s3UploadUrl = `${GMAIL_S3_API_BASE_URL}/api/emails/${currentMessageId}/attachments/${attachmentId}/upload?expected_filename=${encodeURIComponent(filename)}&expected_mime_type=${encodeURIComponent(mimeType)}`;
                    
                    // Make the S3 upload request
                    const s3Response = await fetch(s3UploadUrl, {
                        method: 'POST',
                        headers: {
                            'Accept': 'application/json'
                        }
                    });
                    
                    if (!s3Response.ok) {
                        const errorData = await s3Response.json().catch(() => ({ detail: s3Response.statusText }));
                        console.error('S3 upload API error response:', errorData);
                        throw new Error(errorData.detail || 'Failed to upload attachment to S3');
                    }
                    
                    const s3Data = await s3Response.json();
                    console.log('S3 upload successful:', s3Data);
                    
                    // Show success message for S3 upload
                    showS3Success(`Attachment "${filename}" uploaded successfully to S3!`);
                    
                    // Add S3 URL information if available
                    if (s3Data.s3_url) {
                        showS3Info(`S3 URL: ${s3Data.s3_url}`);
                    }
                    
                } catch (s3Error) {
                    console.error('Error uploading to S3:', s3Error);
                    showS3Error(`S3 upload error: ${s3Error.message}`);
                }
            }
            
            // Wait a moment to let the user see the success messages
            setTimeout(() => {
                // Close the modal
                emailAttachmentModal.classList.add('hidden');
                
                // Show success message on the main page
                showSuccess(uploadResult, `Attachment "${filename}" uploaded successfully! File ID: ${uploadData.file_id}`);
                
                // Preview the file if it's a CSV
                if (mimeType.includes('csv') || filename.toLowerCase().endsWith('.csv')) {
                    previewFile(uploadData.file_id);
                }
                
                // Reload the file list
                loadUploadedFiles();
            }, 2000);
            
        } catch (error) {
            console.error('Error fetching attachment:', error);
            showModalError(`Error: ${error.message}`);
        }
    }
    
    function showModalInfo(message) {
        emailModalStatus.className = 'bg-blue-50 border border-blue-200 text-blue-700 px-4 py-3 rounded-lg mt-4';
        emailModalStatus.textContent = message;
        emailModalStatus.classList.remove('hidden');
    }
    
    function showS3Success(message) {
        s3UploadStatus.className = 'bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg mt-4';
        s3UploadStatus.textContent = message;
        s3UploadStatus.classList.remove('hidden');
    }
    
    function showS3Error(message) {
        s3UploadStatus.className = 'bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mt-4';
        s3UploadStatus.textContent = message;
        s3UploadStatus.classList.remove('hidden');
    }
    
    function showS3Loading(message) {
        s3UploadStatus.className = 'bg-blue-50 border border-blue-200 text-blue-700 px-4 py-3 rounded-lg mt-4';
        s3UploadStatus.textContent = message;
        s3UploadStatus.classList.remove('hidden');
    }
    
    function showS3Info(message) {
        // Append info to existing content
        const currentContent = s3UploadStatus.textContent;
        s3UploadStatus.textContent = `${currentContent}\n${message}`;
    }
    
    /**
     * Initialize RIQ Rate Quote section
     */
    function setupRIQ() {
        // Set default values for quick quote form
        if (document.getElementById('quick-source-city')) {
            document.getElementById('quick-source-city').value = 'Lancaster';
            document.getElementById('quick-source-state').value = 'TX';
            document.getElementById('quick-source-zip').value = '75134';
            document.getElementById('quick-dest-city').value = 'Owasso';
            document.getElementById('quick-dest-state').value = 'OK';
            document.getElementById('quick-dest-zip').value = '74055';
            document.getElementById('quick-weight').value = '2400';
            document.getElementById('quick-volume').value = '150';
        }
        
        // Set default values for full quote form
        if (document.getElementById('full-source-city')) {
            document.getElementById('full-source-city').value = 'Lancaster';
            document.getElementById('full-source-state').value = 'TX';
            document.getElementById('full-source-zip').value = '75134';
            document.getElementById('full-dest-city').value = 'Owasso';
            document.getElementById('full-dest-state').value = 'OK';
            document.getElementById('full-dest-zip').value = '74055';
            document.getElementById('servprov-gid').value = 'BSL.RYGB';
            document.getElementById('max-options').value = '99';
        }
        
        // Set default values for the first item in full quote
        const firstItemWeight = document.querySelector('.item-weight');
        const firstItemVolume = document.querySelector('.item-volume');
        const firstItemPackageCount = document.querySelector('.item-package-count');
        
        if (firstItemWeight) firstItemWeight.value = '2400';
        if (firstItemVolume) firstItemVolume.value = '150';
        if (firstItemPackageCount) firstItemPackageCount.value = '1';
        
        // Initialize remove button visibility
        updateRemoveButtons();
    }
    
    // RIQ Rate Quote Functions
    
    /**
     * Switch between quick quote and full quote modes
     */
    function switchQuoteMode(mode) {
        if (mode === 'quick') {
            // Switch to quick quote mode
            quickQuoteToggle.classList.remove('bg-neutral-200', 'text-neutral-600');
            quickQuoteToggle.classList.add('bg-primary-600', 'text-white');
            fullQuoteToggle.classList.remove('bg-primary-600', 'text-white');
            fullQuoteToggle.classList.add('bg-neutral-200', 'text-neutral-600');
            
            quickQuoteForm.classList.remove('hidden');
            fullQuoteForm.classList.add('hidden');
        } else {
            // Switch to full quote mode
            fullQuoteToggle.classList.remove('bg-neutral-200', 'text-neutral-600');
            fullQuoteToggle.classList.add('bg-primary-600', 'text-white');
            quickQuoteToggle.classList.remove('bg-primary-600', 'text-white');
            quickQuoteToggle.classList.add('bg-neutral-200', 'text-neutral-600');
            
            fullQuoteForm.classList.remove('hidden');
            quickQuoteForm.classList.add('hidden');
        }
    }
    
    /**
     * Handle quick quote form submission
     */
    async function handleQuickQuote(e) {
        e.preventDefault();
        
        try {
            showLoading(riqResult);
            
            // Get form data
            const formData = new FormData(quickQuoteForm);
            const sourceCity = formData.get('quick-source-city') || document.getElementById('quick-source-city').value;
            const sourceState = formData.get('quick-source-state') || document.getElementById('quick-source-state').value;
            const sourceZip = formData.get('quick-source-zip') || document.getElementById('quick-source-zip').value;
            const destCity = formData.get('quick-dest-city') || document.getElementById('quick-dest-city').value;
            const destState = formData.get('quick-dest-state') || document.getElementById('quick-dest-state').value;
            const destZip = formData.get('quick-dest-zip') || document.getElementById('quick-dest-zip').value;
            const weight = parseFloat(formData.get('quick-weight') || document.getElementById('quick-weight').value);
            const volume = parseFloat(formData.get('quick-volume') || document.getElementById('quick-volume').value) || 0;
            
            // Validate required fields
            if (!sourceCity || !sourceState || !sourceZip || !destCity || !destState || !destZip || !weight) {
                throw new Error('Please fill in all required fields');
            }
            
            // Create query parameters
            const params = new URLSearchParams({
                source_city: sourceCity,
                source_state: sourceState,
                source_zip: sourceZip,
                dest_city: destCity,
                dest_state: destState,
                dest_zip: destZip,
                weight: weight,
                volume: volume
            });
            
            // Make API call
            const response = await fetch(`${RIQ_API_BASE_URL}/quick-quote?${params}`, {
                method: 'POST',
                headers: {
                    'Accept': 'application/json'
                }
            });
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: response.statusText }));
                throw new Error(errorData.detail || 'Failed to get rate quote');
            }
            
            const result = await response.json();
            
            if (result.success) {
                displayQuoteResults(result.data, 'quick');
                showSuccess(riqResult, 'Rate quote retrieved successfully!');
            } else {
                throw new Error(result.error || 'Failed to get rate quote');
            }
            
        } catch (error) {
            console.error('Error getting quick quote:', error);
            showError(riqResult, `Error: ${error.message}`);
        }
    }
    
    /**
     * Handle full quote form submission
     */
    async function handleFullQuote(e) {
        e.preventDefault();
        
        try {
            showLoading(riqResult);
            
            // Get form data
            const sourceLocation = {
                city: document.getElementById('full-source-city').value,
                province_code: document.getElementById('full-source-state').value,
                postal_code: document.getElementById('full-source-zip').value,
                country_code: document.getElementById('full-source-country').value
            };
            
            const destinationLocation = {
                city: document.getElementById('full-dest-city').value,
                province_code: document.getElementById('full-dest-state').value,
                postal_code: document.getElementById('full-dest-zip').value,
                country_code: document.getElementById('full-dest-country').value
            };
            
            // Get items
            const items = [];
            const itemRows = itemsContainer.querySelectorAll('.item-row');
            
            for (const row of itemRows) {
                const weight = parseFloat(row.querySelector('.item-weight').value);
                const weightUnit = row.querySelector('.item-weight-unit').value;
                const volume = parseFloat(row.querySelector('.item-volume').value) || 0;
                const volumeUnit = row.querySelector('.item-volume-unit').value;
                const declaredValue = parseFloat(row.querySelector('.item-declared-value').value) || 0;
                const currency = row.querySelector('.item-currency').value;
                const packageCount = parseInt(row.querySelector('.item-package-count').value) || 1;
                
                if (weight > 0) {
                    items.push({
                        weight_value: weight,
                        weight_unit: weightUnit,
                        volume_value: volume,
                        volume_unit: volumeUnit,
                        declared_value: declaredValue,
                        currency: currency,
                        package_count: packageCount
                    });
                }
            }
            
            // Validate
            if (!sourceLocation.city || !sourceLocation.province_code || !sourceLocation.postal_code ||
                !destinationLocation.city || !destinationLocation.province_code || !destinationLocation.postal_code ||
                items.length === 0) {
                throw new Error('Please fill in all required fields and add at least one item');
            }
            
            // Get advanced options
            const servprovGid = document.getElementById('servprov-gid').value || 'BSL.RYGB';
            const requestType = document.getElementById('request-type').value || 'AllOptions';
            const maxOptions = document.getElementById('max-options').value || '99';
            
            // Create request payload
            const requestPayload = {
                source_location: sourceLocation,
                destination_location: destinationLocation,
                items: items,
                servprov_gid: servprovGid,
                request_type: requestType,
                max_primary_options: maxOptions,
                primary_option_definition: 'BY_ITINERARY'
            };
            
            // Make API call
            const response = await fetch(`${RIQ_API_BASE_URL}/rate-quote`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify(requestPayload)
            });
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: response.statusText }));
                throw new Error(errorData.detail || 'Failed to get rate quote');
            }
            
            const result = await response.json();
            
            if (result.success) {
                displayQuoteResults(result.data, 'full');
                showSuccess(riqResult, 'Rate quote retrieved successfully!');
            } else {
                throw new Error(result.error || 'Failed to get rate quote');
            }
            
        } catch (error) {
            console.error('Error getting full quote:', error);
            showError(riqResult, `Error: ${error.message}`);
        }
    }
    
    /**
     * Add a new item to the full quote form
     */
    function addNewItem() {
        itemCounter++;
        
        const newItemHtml = `
            <div class="item-row border border-neutral-200 rounded-lg p-4 mb-4">
                <div class="flex items-center justify-between mb-4">
                    <h5 class="text-sm font-medium text-neutral-700">Item ${itemCounter}</h5>
                    <button type="button" class="remove-item-btn text-red-500 hover:text-red-700 transition-colors">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
                <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-neutral-700 mb-2">Weight</label>
                        <div class="flex">
                            <input type="number" class="item-weight w-full px-3 py-2 border border-neutral-300 rounded-l-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors" placeholder="0" min="0" step="0.1">
                            <select class="item-weight-unit px-3 py-2 border-t border-r border-b border-neutral-300 rounded-r-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors">
                                <option value="LB">LB</option>
                                <option value="KG">KG</option>
                            </select>
                        </div>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-neutral-700 mb-2">Volume</label>
                        <div class="flex">
                            <input type="number" class="item-volume w-full px-3 py-2 border border-neutral-300 rounded-l-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors" placeholder="0" min="0" step="0.1">
                            <select class="item-volume-unit px-3 py-2 border-t border-r border-b border-neutral-300 rounded-r-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors">
                                <option value="CUFT">CUFT</option>
                                <option value="CBM">CBM</option>
                            </select>
                        </div>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-neutral-700 mb-2">Declared Value</label>
                        <div class="flex">
                            <input type="number" class="item-declared-value w-full px-3 py-2 border border-neutral-300 rounded-l-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors" placeholder="0" min="0" step="0.01">
                            <select class="item-currency px-3 py-2 border-t border-r border-b border-neutral-300 rounded-r-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors">
                                <option value="USD">USD</option>
                                <option value="CAD">CAD</option>
                                <option value="EUR">EUR</option>
                            </select>
                        </div>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-neutral-700 mb-2">Package Count</label>
                        <input type="number" class="item-package-count w-full px-3 py-2 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors" placeholder="1" min="1" step="1">
                    </div>
                </div>
            </div>
        `;
        
        itemsContainer.insertAdjacentHTML('beforeend', newItemHtml);
        updateRemoveButtons();
    }
    
    /**
     * Remove an item from the full quote form
     */
    function removeItem(itemRow) {
        itemRow.remove();
        updateRemoveButtons();
        renumberItems();
    }
    
    /**
     * Update visibility of remove buttons based on item count
     */
    function updateRemoveButtons() {
        const itemRows = itemsContainer.querySelectorAll('.item-row');
        const removeButtons = itemsContainer.querySelectorAll('.remove-item-btn');
        
        if (itemRows.length <= 1) {
            // Hide remove button if only one item
            removeButtons.forEach(btn => btn.classList.add('hidden'));
        } else {
            // Show remove buttons if more than one item
            removeButtons.forEach(btn => btn.classList.remove('hidden'));
        }
    }
    
    /**
     * Renumber items after removal
     */
    function renumberItems() {
        const itemRows = itemsContainer.querySelectorAll('.item-row');
        itemRows.forEach((row, index) => {
            const header = row.querySelector('h5');
            header.textContent = `Item ${index + 1}`;
        });
        itemCounter = itemRows.length;
    }
    
    /**
     * Display quote results
     */
    function displayQuoteResults(data, quoteType) {
        const resultsContainer = document.getElementById('quote-results-container');
        const summaryContainer = document.getElementById('quote-summary');
        const optionsContainer = document.getElementById('quote-options-container');
        
        if (!data || !data.rateAndRouteResponse || !data.rateAndRouteResponse.length) {
            showError(document.getElementById('riq-result'), 'No rate quotes found in the response.');
            return;
        }
        
        const rateOptions = data.rateAndRouteResponse;
        
        // Clear previous results
        summaryContainer.innerHTML = '';
        optionsContainer.innerHTML = '';
        
        // Create summary
        const summaryCard = document.createElement('div');
        summaryCard.className = 'bg-gradient-to-r from-blue-50 to-green-50 border border-blue-200 rounded-lg p-6 mb-6';
        summaryCard.innerHTML = `
            <div class="flex items-center justify-between mb-4">
                <h4 class="text-lg font-semibold text-neutral-900 flex items-center">
                    <i class="fas fa-shipping-fast mr-2 text-blue-500"></i>
                    Quote Summary
                </h4>
                <span class="text-sm text-neutral-600">${rateOptions.length} option${rateOptions.length > 1 ? 's' : ''} found</span>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div class="text-center">
                    <div class="text-2xl font-bold text-green-600">${rateOptions.length}</div>
                    <div class="text-sm text-neutral-600">Rate Option${rateOptions.length > 1 ? 's' : ''}</div>
                </div>
                <div class="text-center">
                    <div class="text-2xl font-bold text-blue-600">$${parseFloat(rateOptions[0].totalActualCost?.value || 0).toLocaleString('en-US', {minimumFractionDigits: 2})}</div>
                    <div class="text-sm text-neutral-600">Best Rate</div>
                </div>
                <div class="text-center">
                    <div class="text-2xl font-bold text-purple-600">${rateOptions[0].transitTime?.amount || 'N/A'} ${rateOptions[0].transitTime?.type === 'H' ? 'hrs' : rateOptions[0].transitTime?.type || ''}</div>
                    <div class="text-sm text-neutral-600">Transit Time</div>
                </div>
            </div>
        `;
        summaryContainer.appendChild(summaryCard);
        
        // Display each rate option
        rateOptions.forEach((option, index) => {
            const optionCard = createDetailedRateCard(option, index);
            optionsContainer.appendChild(optionCard);
        });
        
        resultsContainer.classList.remove('hidden');
        
        // Scroll to results
        resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    function createDetailedRateCard(option, index) {
        const card = document.createElement('div');
        card.className = 'bg-white border border-neutral-200 rounded-xl shadow-sm hover:shadow-md transition-shadow';
        
        // Extract shipment details from toShipments if available
        const shipment = option.toShipments && option.toShipments[0] ? option.toShipments[0] : {};
        
        // Format dates
        const formatDateTime = (dateString) => {
            if (!dateString) return 'N/A';
            try {
                const date = new Date(dateString);
                return date.toLocaleDateString('en-US', { 
                    month: 'short', 
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                });
            } catch (e) {
                return 'N/A';
            }
        };
        
        // Get transport mode display name
        const getTransportModeDisplay = (gid) => {
            const modes = {
                'TL': 'Truck Load (TL)',
                'LTL': 'Less Than Truck Load (LTL)',
                'AIR': 'Air Freight',
                'RAIL': 'Rail',
                'OCEAN': 'Ocean'
            };
            return modes[gid] || gid || 'Unknown';
        };
        
        const cardId = `rate-card-${index}`;
        
        card.innerHTML = `
            <!-- Card Header (Always Visible) -->
            <div class="p-6 cursor-pointer rate-card-header" data-card-id="${cardId}">
                <div class="flex items-center justify-between">
                    <div class="flex items-center space-x-3">
                        <div class="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-white font-bold text-sm">
                            ${index + 1}
                        </div>
                        <div>
                            <h4 class="text-lg font-semibold text-neutral-900">Rate Option ${index + 1}</h4>
                            <p class="text-sm text-neutral-600">${getTransportModeDisplay(option.transportMode?.transportModeGid)}</p>
                        </div>
                    </div>
                    <div class="flex items-center space-x-4">
                        <div class="text-right">
                            <div class="text-2xl font-bold text-green-600">$${parseFloat(option.totalActualCost?.value || 0).toLocaleString('en-US', {minimumFractionDigits: 2})}</div>
                            <div class="text-sm text-neutral-600">${option.totalActualCost?.currency || 'USD'}</div>
                        </div>
                        <div class="text-neutral-400 transition-transform duration-200" id="${cardId}-toggle-icon">
                            <i class="fas fa-chevron-down text-lg"></i>
                        </div>
                    </div>
                </div>
                
                <!-- Quick Summary (Visible when collapsed) -->
                <div class="mt-4 grid grid-cols-1 sm:grid-cols-3 gap-4">
                    <div class="text-center bg-purple-50 rounded-lg p-3">
                        <div class="text-lg font-bold text-purple-700">${option.transitTime?.amount || 'N/A'}</div>
                        <div class="text-xs text-purple-600">Transit ${option.transitTime?.type === 'H' ? 'Hours' : (option.transitTime?.type || 'Time')}</div>
                    </div>
                    <div class="text-center bg-blue-50 rounded-lg p-3">
                        <div class="text-lg font-bold text-blue-700">${option.serviceProvider?.servprovGid || 'N/A'}</div>
                        <div class="text-xs text-blue-600">Service Provider</div>
                    </div>
                    <div class="text-center bg-orange-50 rounded-lg p-3">
                        <div class="text-lg font-bold text-orange-700">${shipment.distance?.amount ? parseFloat(shipment.distance.amount).toFixed(1) : 'N/A'}</div>
                        <div class="text-xs text-orange-600">${shipment.distance?.type === 'MI' ? 'Miles' : (shipment.distance?.type || 'Distance')}</div>
                    </div>
                </div>
            </div>
            
            <!-- Expandable Content -->
            <div class="rate-card-content hidden" id="${cardId}-content">
                <!-- Cost Breakdown -->
                <div class="px-6 pb-6">
                    <div class="border-t border-neutral-100 pt-6">
                        <h5 class="text-sm font-semibold text-neutral-900 mb-4 flex items-center">
                            <i class="fas fa-dollar-sign mr-2 text-green-500"></i>
                            Cost Breakdown
                        </h5>
                        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                            <div class="bg-green-50 border border-green-200 rounded-lg p-4 text-center">
                                <div class="text-lg font-bold text-green-700">$${parseFloat(option.totalActualCost?.value || 0).toLocaleString('en-US', {minimumFractionDigits: 2})}</div>
                                <div class="text-xs text-green-600 mt-1">Total Cost</div>
                            </div>
                            <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 text-center">
                                <div class="text-lg font-bold text-blue-700">$${parseFloat(option.costPerUnit?.value || 0).toFixed(2)}</div>
                                <div class="text-xs text-blue-600 mt-1">Cost Per Unit</div>
                            </div>
                            <div class="bg-purple-50 border border-purple-200 rounded-lg p-4 text-center">
                                <div class="text-lg font-bold text-purple-700">$${parseFloat(option.totalWeightedCost?.value || 0).toLocaleString('en-US', {minimumFractionDigits: 2})}</div>
                                <div class="text-xs text-purple-600 mt-1">Weighted Cost</div>
                            </div>
                            <div class="bg-orange-50 border border-orange-200 rounded-lg p-4 text-center">
                                <div class="text-lg font-bold text-orange-700">$${parseFloat(option.weightedCostPerUnit?.value || 0).toFixed(2)}</div>
                                <div class="text-xs text-orange-600 mt-1">Weighted Per Unit</div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Service Details -->
                    <div class="border-t border-neutral-100 pt-6 mt-6">
                        <h5 class="text-sm font-semibold text-neutral-900 mb-4 flex items-center">
                            <i class="fas fa-truck mr-2 text-neutral-600"></i>
                            Service Details
                        </h5>
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div class="space-y-3">
                                <div class="flex justify-between">
                                    <span class="text-sm text-neutral-600">Service Provider:</span>
                                    <span class="text-sm font-medium text-neutral-900">${option.serviceProvider?.servprovGid || 'N/A'}</span>
                                </div>
                                <div class="flex justify-between">
                                    <span class="text-sm text-neutral-600">Equipment:</span>
                                    <span class="text-sm font-medium text-neutral-900">${option.equipmentGroup?.equipmentGroupGid?.replace('BSL.', '') || 'N/A'}</span>
                                </div>
                                <div class="flex justify-between">
                                    <span class="text-sm text-neutral-600">Rate Offering:</span>
                                    <span class="text-sm font-medium text-neutral-900">${option.primaryRateOffering?.rateOfferingGid?.replace('BSL.', '') || 'N/A'}</span>
                                </div>
                            </div>
                            <div class="space-y-3">
                                <div class="flex justify-between">
                                    <span class="text-sm text-neutral-600">Pickup Time:</span>
                                    <span class="text-sm font-medium text-neutral-900">${formatDateTime(option.startTime?.value)}</span>
                                </div>
                                <div class="flex justify-between">
                                    <span class="text-sm text-neutral-600">Delivery Time:</span>
                                    <span class="text-sm font-medium text-neutral-900">${formatDateTime(option.endTime?.value)}</span>
                                </div>
                                <div class="flex justify-between">
                                    <span class="text-sm text-neutral-600">Itinerary:</span>
                                    <span class="text-sm font-medium text-neutral-900">${option.itinerary?.itineraryGid?.replace('BSL.', '') || 'N/A'}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Shipment Details -->
                    ${shipment.weight || shipment.volume ? `
                    <div class="border-t border-neutral-100 pt-6 mt-6">
                        <h5 class="text-sm font-semibold text-neutral-900 mb-4 flex items-center">
                            <i class="fas fa-boxes mr-2 text-neutral-600"></i>
                            Shipment Specifications
                        </h5>
                        <div class="flex items-center justify-center space-x-8">
                            ${shipment.weight ? `
                            <div class="text-center">
                                <div class="text-lg font-bold text-neutral-900">${parseFloat(shipment.weight.amount).toLocaleString()}</div>
                                <div class="text-sm text-neutral-600">${shipment.weight.type}</div>
                            </div>
                            ` : ''}
                            ${shipment.volume ? `
                            <div class="text-center">
                                <div class="text-lg font-bold text-neutral-900">${parseFloat(shipment.volume.amount).toLocaleString()}</div>
                                <div class="text-sm text-neutral-600">${shipment.volume.type}</div>
                            </div>
                            ` : ''}
                        </div>
                    </div>
                    ` : ''}
                    
                    <!-- Action Button -->
                    <div class="border-t border-neutral-100 pt-6 mt-6">
                        <button class="w-full bg-gradient-to-r from-blue-600 to-blue-600 text-white font-medium py-3 px-4 rounded-lg hover:from-blue-700 hover:to-blue-700 transition-all duration-200 transform hover:scale-105 flex items-center justify-center">
                            <i class="fas fa-check-circle mr-2"></i>
                            Select This Rate Option
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        // Add click event listener to the header
        const header = card.querySelector('.rate-card-header');
        header.addEventListener('click', function() {
            toggleRateCard(cardId);
        });
        
        return card;
    }
});