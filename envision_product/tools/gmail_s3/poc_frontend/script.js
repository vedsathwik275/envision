document.addEventListener('DOMContentLoaded', () => {
    const API_BASE_URL = 'http://localhost:8002'; // Ensure this matches your backend port

    // Auth elements
    const loginBtn = document.getElementById('login-btn');
    const logoutBtn = document.getElementById('logout-btn');
    const authStatusEl = document.getElementById('auth-status');

    // Email elements
    const emailsSection = document.getElementById('emails-section');
    const listEmailsBtn = document.getElementById('list-emails-btn');
    const emailsListEl = document.getElementById('emails-list');

    // Attachment elements
    const attachmentsSection = document.getElementById('attachments-section');
    const selectedEmailIdEl = document.getElementById('selected-email-id');
    const attachmentsListEl = document.getElementById('attachments-list');

    // Action elements
    const actionsSection = document.getElementById('actions-section');
    const selectedAttachmentInfoEl = document.getElementById('selected-attachment-info');
    const downloadBtn = document.getElementById('download-btn');
    const uploadS3Btn = document.getElementById('upload-s3-btn');

    // Status messages
    const messagesEl = document.getElementById('messages');

    let currentMessageId = null;
    let currentAttachment = null; // { id, filename, mime_type }

    function showMessage(text, isError = false) {
        messagesEl.textContent = text;
        messagesEl.style.color = isError ? 'red' : 'green';
        console.log(text);
    }

    async function checkAuthStatus() {
        try {
            const response = await fetch(`${API_BASE_URL}/auth/status`);
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: response.statusText }));
                throw new Error(errorData.detail || 'Failed to check auth status');
            }
            const data = await response.json();
            if (data.authenticated) {
                authStatusEl.textContent = 'Status: Authenticated';
                loginBtn.style.display = 'none';
                logoutBtn.style.display = 'inline-block';
                emailsSection.style.display = 'block';
            } else {
                authStatusEl.textContent = 'Status: Not Authenticated';
                loginBtn.style.display = 'inline-block';
                logoutBtn.style.display = 'none';
                emailsSection.style.display = 'none';
                attachmentsSection.style.display = 'none';
                actionsSection.style.display = 'none';
            }
        } catch (error) {
            authStatusEl.textContent = 'Status: Error checking status';
            showMessage(`Error checking auth status: ${error.message}`, true);
            loginBtn.style.display = 'inline-block'; // Show login if status check fails
        }
    }

    loginBtn.addEventListener('click', async () => {
        showMessage('Login button clicked. Fetching authorization URL...');
        try {
            const response = await fetch(`${API_BASE_URL}/auth/login`);
            showMessage(`Login API response status: ${response.status}`);
            
            if (!response.ok) {
                let errorDetail = response.statusText;
                try {
                    const errorData = await response.json();
                    errorDetail = errorData.detail || errorDetail;
                } catch (e) {
                    // If JSON parsing fails, stick with statusText
                    console.error('Failed to parse error response as JSON', e);
                }
                showMessage(`Login API call failed: ${errorDetail}`, true);
                throw new Error(errorDetail);
            }
            
            const data = await response.json();
            showMessage(`Login API response data: ${JSON.stringify(data)}`);
            
            if (data && data.authorization_url) {
                showMessage(`Opening Google login in a new tab: ${data.authorization_url}`);
                window.open(data.authorization_url, '_blank');
                // After the user authenticates, Google will redirect to your backend's /auth/callback
                // That callback then redirects to your backend's root ('/').
                // The original PoC frontend tab will not automatically know about the auth success
                // without a refresh or another status check.
                // For a PoC, the user can manually return to this tab and click "List Emails" 
                // or we can add a more explicit "Refresh Auth Status" button.
            } else {
                showMessage('Authorization URL not found in API response.', true);
                console.error('Authorization URL not found:', data);
            }
        } catch (error) {
            showMessage(`Login error: ${error.message}`, true);
            console.error('Login fetch error:', error);
        }
    });

    logoutBtn.addEventListener('click', async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/auth/logout`, { method: 'POST' });
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: response.statusText }));
                throw new Error(errorData.detail || 'Failed to logout');
            }
            const data = await response.json();
            showMessage(data.message || 'Logged out successfully');
            checkAuthStatus(); // Re-check status to update UI
        } catch (error) {
            showMessage(`Logout error: ${error.message}`, true);
        }
    });

    listEmailsBtn.addEventListener('click', async () => {
        emailsListEl.innerHTML = '<p>Loading emails...</p>';
        attachmentsSection.style.display = 'none';
        actionsSection.style.display = 'none';
        currentMessageId = null;
        currentAttachment = null;
        selectedEmailIdEl.textContent = 'None';
        selectedAttachmentInfoEl.textContent = 'None';
        try {
            const response = await fetch(`${API_BASE_URL}/api/emails`); // Add query params if needed
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: response.statusText }));
                throw new Error(errorData.detail || 'Failed to list emails');
            }
            const emails = await response.json();
            emailsListEl.innerHTML = '';
            if (emails.length === 0) {
                emailsListEl.innerHTML = '<p>No emails with target attachments found.</p>';
                return;
            }
            emails.forEach(email => {
                const item = document.createElement('div');
                item.classList.add('list-item');
                item.textContent = `Subject: ${email.subject} (From: ${email.from_email || email.from || 'N/A'}, Date: ${email.date || 'N/A'})${email.has_target_attachments ? ' [Has Target Attachments]' : ''}`;
                item.dataset.emailId = email.id;
                item.addEventListener('click', () => {
                    document.querySelectorAll('#emails-list .list-item').forEach(el => el.classList.remove('selected'));
                    item.classList.add('selected');
                    currentMessageId = email.id;
                    selectedEmailIdEl.textContent = currentMessageId;
                    attachmentsSection.style.display = 'block';
                    actionsSection.style.display = 'none';
                    currentAttachment = null;
                    selectedAttachmentInfoEl.textContent = 'None';
                    listAttachmentsForEmail(currentMessageId);
                });
                emailsListEl.appendChild(item);
            });
        } catch (error) {
            showMessage(`Error listing emails: ${error.message}`, true);
            emailsListEl.innerHTML = `<p>Error: ${error.message}</p>`;
        }
    });

    async function listAttachmentsForEmail(messageId) {
        attachmentsListEl.innerHTML = '<p>Loading attachments...</p>';
        try {
            const response = await fetch(`${API_BASE_URL}/api/emails/${messageId}/attachments`);
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: response.statusText }));
                throw new Error(errorData.detail || 'Failed to list attachments');
            }
            const attachments = await response.json();
            attachmentsListEl.innerHTML = '';
            if (attachments.length === 0) {
                attachmentsListEl.innerHTML = '<p>No attachments found for this email.</p>';
                return;
            }
            attachments.forEach(att => {
                const item = document.createElement('div');
                item.classList.add('list-item');
                item.textContent = `Filename: ${att.filename} (Type: ${att.mime_type}, Size: ${att.size} bytes)${att.is_target_file ? ' [Target File]' : ''}`;
                item.dataset.attachmentId = att.id;
                item.dataset.filename = att.filename;
                item.dataset.mimeType = att.mime_type;
                item.addEventListener('click', () => {
                    document.querySelectorAll('#attachments-list .list-item').forEach(el => el.classList.remove('selected'));
                    item.classList.add('selected');
                    currentAttachment = {
                        id: att.id,
                        filename: att.filename,
                        mime_type: att.mime_type
                    };
                    selectedAttachmentInfoEl.textContent = `${att.filename} (ID: ${att.id})`;
                    actionsSection.style.display = 'block';
                });
                attachmentsListEl.appendChild(item);
            });
        } catch (error) {
            showMessage(`Error listing attachments: ${error.message}`, true);
            attachmentsListEl.innerHTML = `<p>Error: ${error.message}</p>`;
        }
    }

    downloadBtn.addEventListener('click', () => {
        if (!currentMessageId || !currentAttachment) {
            showMessage('Please select an email and an attachment first.', true);
            return;
        }
        // Construct URL with expected_filename and expected_mime_type
        const downloadUrl = `${API_BASE_URL}/api/emails/${currentMessageId}/attachments/${currentAttachment.id}?expected_filename=${encodeURIComponent(currentAttachment.filename)}&expected_mime_type=${encodeURIComponent(currentAttachment.mime_type)}`;
        showMessage(`Attempting to download: ${currentAttachment.filename}... URL: ${downloadUrl}`);
        // Open in new tab/window to trigger download
        window.open(downloadUrl, '_blank');
    });

    uploadS3Btn.addEventListener('click', async () => {
        if (!currentMessageId || !currentAttachment) {
            showMessage('Please select an email and an attachment first.', true);
            return;
        }
        // Construct URL with expected_filename and expected_mime_type
        const uploadUrl = `${API_BASE_URL}/api/emails/${currentMessageId}/attachments/${currentAttachment.id}/upload?expected_filename=${encodeURIComponent(currentAttachment.filename)}&expected_mime_type=${encodeURIComponent(currentAttachment.mime_type)}`;
        showMessage(`Attempting to upload ${currentAttachment.filename} to S3... URL: ${uploadUrl}`);
        try {
            const response = await fetch(uploadUrl, { method: 'POST' });
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: response.statusText }));
                throw new Error(errorData.detail || 'Upload to S3 failed');
            }
            const result = await response.json();
            showMessage(`Upload successful!\nFilename: ${result.filename}\nS3 Location: ${result.s3_location}\nMetadata: ${JSON.stringify(result.metadata, null, 2)}`);
        } catch (error) {
            showMessage(`Error uploading to S3: ${error.message}`, true);
        }
    });

    // Initial check for auth status
    checkAuthStatus();
}); 