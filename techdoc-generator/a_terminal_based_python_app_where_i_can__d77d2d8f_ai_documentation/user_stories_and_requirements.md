# User Stories and Requirements Document

## User Personas

1. **Data Scientist**
   - Familiar with neural networks and data preprocessing but prefers command-line tools for efficiency.
   - Needs a straightforward way to test models quickly using CSV data.

2. **ML Enthusiast**
   - Has basic knowledge of machine learning concepts.
   - Wants to experiment with neural networks using existing data but lacks advanced technical skills.

3. **Software Developer**
   - Comfortable with coding and using terminal interfaces.
   - Interested in integrating machine learning models into larger applications.

## User Stories

1. **As a Data Scientist,**
   - I want to load a CSV file and select the target feature so that I can quickly preprocess and train a neural network model.

2. **As an ML Enthusiast,**
   - I want to easily navigate through a menu-driven interface to input data and train a model without needing deep technical knowledge.

3. **As a Software Developer,**
   - I want to load existing models and run predictions on new data so that I can integrate this functionality into applications I'm developing.

## Functional Requirements

1. **CSV File Handling**
   - The system shall allow users to input a CSV filename.
   - The system shall parse the columns of the CSV file and display them for selection.

2. **Feature Selection**
   - The system shall allow users to select a target feature from the parsed columns.
   - The system shall automatically suggest input features based on the data.

3. **Data Preprocessing**
   - The system shall handle missing values using imputation or removal.
   - The system shall scale numerical features using standardization or normalization.
   - The system shall encode categorical features using one-hot or label encoding.

4. **Model Training**
   - The system shall generate a neural network model based on preprocessed data.
   - The system shall allow the user to start training the model with customizable parameters.

5. **Model Saving and Loading**
   - The system shall save the trained model to a file.
   - The system shall load existing models from a file for predictions.

6. **Prediction**
   - The system shall allow users to input new data for prediction.
   - The system shall preprocess the input data and provide predictions using the loaded model.

## Non-Functional Requirements

1. **Usability**
   - The application shall provide a clear and intuitive interface using `simple-term-menu`.

2. **Performance**
   - The system shall efficiently handle large CSV files without significant delay.

3. **Scalability**
   - The application shall be designed to allow future enhancements and integrations.

4. **Reliability**
   - The application shall handle errors gracefully and provide meaningful error messages.

## Acceptance Criteria

1. **CSV File Handling**
   - Given a CSV filename, the system should read the file and display its columns accurately.

2. **Feature Selection**
   - When selecting a target feature, the system should display a list of columns and allow the user to choose one.

3. **Data Preprocessing**
   - The system should preprocess the data by handling missing values, scaling features, and encoding categorical data as specified.

4. **Model Training**
   - Upon starting the training, the system should configure and train a neural network, then save the model successfully.

5. **Model Saving and Loading**
   - The system should save the model in a retrievable format and allow successful loading for future use.

6. **Prediction**
   - The system should accept new data inputs, preprocess them, and return accurate predictions.

## Edge Cases

1. **CSV File Issues**
   - If the CSV file is empty or malformed, the system should notify the user and request a new file.
   - If the CSV file contains non-numeric data in numeric columns, the system should handle and notify the user.

2. **Feature Selection**
   - If the user selects an incompatible target feature (e.g., all missing values), the system should prompt for another selection.

3. **Data Preprocessing**
   - If there are columns with 100% missing values, the system should skip or remove those columns with a notification to the user.

4. **Model Training**
   - If the training data is insufficient (e.g., less than required samples), the system should alert the user and suggest adding more data.

5. **Prediction**
   - If prediction data does not match the format of training data, the system should provide an error message and guide the user to correct the input.

By addressing these user stories, requirements, acceptance criteria, and edge cases, the terminal-based Python application will meet user needs effectively, providing a robust tool for training neural networks using CSV data.