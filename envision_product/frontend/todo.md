# Frontend Combination To-Do List

This document outlines the steps to combine the Neural POC and Chat POC frontends into a unified frontend application running on the same port, using an iframe-based approach with query parameter navigation.

**Target Directory for all new/modified files:** `envision_product/frontend/`

## Phase 1: Prepare Individual Page Assets

1.  **Neural App Assets:**
    *   **Create `neural.js`:**
        *   Copy the entire content from `envision_product/neural/poc_frontend/script.js` into `envision_product/frontend/neural.js`.
    *   **Create `neural.html`:**
        *   Copy the entire content from `envision_product/neural/poc_frontend/index.html` into `envision_product/frontend/neural.html`.
        *   **Modify `neural.html`:**
            *   In the `<head>`, remove the line: `<link rel="stylesheet" href="./dist/output.css">`.
            *   Add the Tailwind CSS CDN script and the Tailwind configuration script (copy from `<head>` of `envision_product/chat/poc_frontend/index.html`).
                *   Ensure `<script src="https://cdn.tailwindcss.com"></script>` is present.
                *   Ensure the `tailwind.config` script block is present.
            *   Ensure the Font Awesome CDN link (`<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">`) is present in the `<head>`.
            *   At the end of the `<body>`, change the script tag to `<script src="neural.js"></script>`.

2.  **Chat App Assets:**
    *   **Create `chat.js`:**
        *   Copy the entire content from `envision_product/chat/poc_frontend/script.js` into `envision_product/frontend/chat.js`.
    *   **Create `chat.html`:**
        *   Copy the entire content from `envision_product/chat/poc_frontend/index.html` into `envision_product/frontend/chat.html`.
        *   **Modify `chat.html`:**
            *   Ensure Tailwind CSS CDN and Font Awesome CDN links are correctly placed in the `<head>` (should already be there).
            *   At the end of the `<body>`, change the script tag to `<script src="chat.js"></script>`.

## Phase 2: Create the Main Shell Application

3.  **Create `index.html` (Main Shell):**
    *   This will be a new file.
    *   **HTML Structure:**
        *   Standard HTML5 boilerplate.
        *   **`<head>`:**
            *   `<meta charset="UTF-8">`
            *   `<meta name="viewport" content="width=device-width, initial-scale=1.0">`
            *   `<title>Envision Unified Frontend</title>`
            *   Tailwind CSS CDN script: `<script src="https://cdn.tailwindcss.com"></script>`
            *   Tailwind configuration script (copy from `chat.html` or modified `neural.html`).
            *   Font Awesome CDN: `<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">`
            *   *(Optional: Link to a `style.css` if any custom shell styles are needed beyond Tailwind)*
        *   **`<body>` (Use Tailwind classes for styling):**
            *   A main container `div` using Flexbox (`<div class="flex h-screen">`).
            *   **Sidebar `div` (`id="app-sidebar"`):**
                *   Fixed width (e.g., `w-64`).
                *   Background color (e.g., `bg-gray-800 text-white`).
                *   Full height (`h-full`).
                *   Padding (e.g., `p-4`).
                *   **Navigation Links:**
                    *   Logo/Title area (e.g., `<h1 class="text-xl font-bold mb-4">Envision</h1>`).
                    *   `<a href="?page=neural" id="nav-neural" class="block py-2 px-4 rounded hover:bg-gray-700">Neural AI</a>`
                    *   `<a href="?page=chat" id="nav-chat" class="block py-2 px-4 rounded hover:bg-gray-700">Chat AI</a>`
            *   **Content Area `div` (`class="flex-1 h-full"`):**
                *   This div will host the iframe.
                *   `<iframe id="content-frame" class="w-full h-full border-0"></iframe>` (no `src` initially).

4.  **Create `script.js` (Main Shell Logic):**
    *   This will be a new file.
    *   **JavaScript Logic:**
        *   Wrap code in `document.addEventListener('DOMContentLoaded', () => { ... });`.
        *   Get references to DOM elements: `navNeural` (using `document.getElementById('nav-neural')`), `navChat` (using `document.getElementById('nav-chat')`), `contentFrame` (using `document.getElementById('content-frame')`).
        *   `function loadPage(pageName)`:
            *   Sets `contentFrame.src = pageName + '.html';`
            *   Visually updates active class on sidebar links. Remove active class from all links, then add to the current one.
        *   `function handleRouteChange()`:
            *   `const params = new URLSearchParams(window.location.search);`
            *   `const page = params.get('page') || 'neural'; // Default to 'neural'`
            *   `loadPage(page);`
        *   Add event listeners to `navNeural` and `navChat`:
            *   On click: `event.preventDefault();`
            *   Determine `targetPage` ("neural" or "chat") from the link clicked (e.g., from `event.currentTarget.id`).
            *   `history.pushState({ page: targetPage }, '', '?page=' + targetPage);`
            *   `loadPage(targetPage);`
        *   `window.addEventListener('popstate', handleRouteChange);` (to handle browser back/forward buttons).
        *   Initial call: `handleRouteChange();` to load content based on the initial URL.

5.  **(Optional) Create `style.css`:**
    *   If custom styles are needed for the shell beyond Tailwind. Aim to minimize or avoid. Link in `index.html`'s `<head>`.

---
*This to-do list will guide the development process.* 

---

## Implementation Plan

We will proceed with the tasks in the following order:

**Step 1: Neural App Asset Preparation (Phase 1, Item 1)**
    1. Create `envision_product/frontend/neural.js`.
    2. Create `envision_product/frontend/neural.html`.
    3. Modify `neural.html` (CDN links, script tag).

**Step 2: Chat App Asset Preparation (Phase 1, Item 2)**
    1. Create `envision_product/frontend/chat.js`.
    2. Create `envision_product/frontend/chat.html`.
    3. Modify `chat.html` (script tag, verify CDNs).

**Step 3: Main Shell HTML Structure (Phase 2, Item 3)**
    1. Create `envision_product/frontend/index.html` with the basic layout, sidebar, and iframe.

**Step 4: Main Shell JavaScript Logic (Phase 2, Item 4)**
    1. Create `envision_product/frontend/script.js` to handle page loading via query parameters and iframe src updates.

**Step 5: Testing and Refinement**
    1. Test navigation between Neural and Chat pages.
    2. Verify that both applications function correctly within the iframe.
    3. Check console for errors and resolve any issues.
    4. Ensure styling is consistent with expectations (Tailwind CDN).

**(Optional) Step 6: Custom Shell Styling (Phase 2, Item 5)**
    1. Create `style.css` only if necessary for shell-specific styles not achievable with Tailwind directly.

This phased approach ensures that individual components are correctly prepared before integrating them into the main shell. 