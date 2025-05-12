# Proof of Concept: Terminal-Based Neural Network Trainer

## 1. Introduction

This document outlines a proof of concept (PoC) implementation for the Terminal-Based Neural Network Trainer application. The PoC aims to demonstrate the feasibility of developing a user-friendly, terminal-based application that enables users to load CSV files, preprocess data, train neural network models, and make predictions without requiring extensive technical knowledge.

## 2. Objectives

The primary objectives of this PoC are to:

1. Validate that the proposed architecture can support the intended functionality
2. Demonstrate the user interface experience using `simple-term-menu`
3. Prove that the core components (data handling, model training, and prediction) can integrate seamlessly
4. Identify potential challenges or limitations before full-scale development

## 3. Scope

The PoC will include a minimal viable implementation of:

- CSV file loading and parsing
- Target feature selection
- Basic data preprocessing (handling missing values, scaling, encoding)
- Simple neural network model generation and training
- Model saving and loading
- Basic prediction functionality

Out of scope for the PoC (to be addressed in the full implementation):
- Advanced data preprocessing techniques
- Optimized neural network architectures
- Performance optimization for large datasets
- Extensive error handling
- Comprehensive testing

## 4. PoC Implementation

### 4.1 Technology Stack

- **Python 3.8+**: Core programming language
- **simple-term-menu**: For terminal-based menu interface
- **pandas**: For data handling and manipulation
- **scikit-learn**: For data preprocessing
- **TensorFlow/Keras**: For neural network implementation
- **pytest**: For basic testing

### 4.2 Core Components Implementation

#### 4.2.1 User Interface Component

```python
# ui.py
from simple_term_menu import TerminalMenu

class UserInterface:
    def show_main_menu(self):
        """Display the main menu options."""
        options = ["Train New Model", "Load Existing Model", "Exit"]
        terminal_menu = TerminalMenu(options, title="Neural Network Trainer")
        menu_entry_index = terminal_menu.show()
        return options[menu_entry_index]
    
    def get_csv_filename(self):
        """Get CSV filename from user."""
        return input("Enter CSV filename: ")
    
    def select_target_feature(self, columns):
        """Allow user to select a target feature from available columns."""
        terminal_menu = TerminalMenu(columns, title="Select Target Feature")
        menu_entry_index = terminal_menu.show()
        return columns[menu_entry_index]
    
    def confirm_action(self, message):
        """Ask for user confirmation."""
        options = ["Yes", "No"]
        terminal_menu = TerminalMenu(options, title=message)
        menu_entry_index = terminal_menu.show()
        return menu_entry_index == 0
    
    def display_message(self, message):
        """Display a message to the user."""
        print(message)
```

#### 4.2.2 Data Handling Component

```python
# data_handler.py
import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

class DataHandler:
    def __init__(self):
        self.df = None
        self.target_feature = None
        self.preprocessing_pipeline = None
        
    def load_csv(self, filename):
        """Load a CSV file into a DataFrame."""
        try:
            self.df = pd.read_csv(filename)
            return True, list(self.df.columns)
        except Exception as e:
            return False, str(e)
    
    def set_target_feature(self, target_feature):
        """Set the target feature for model training."""
        if target_feature in self.df.columns:
            self.target_feature = target_feature
            return True
        return False
    
    def preprocess_data(self):
        """Preprocess the data for model training."""
        # Separate features and target
        X = self.df.drop(columns=[self.target_feature])
        y = self.df[self.target_feature]
        
        # Identify numeric and categorical columns
        numeric_features = X.select_dtypes(include=['int64', 'float64']).columns
        categorical_features = X.select_dtypes(include=['object', 'category']).columns
        
        # Create preprocessing pipeline
        numeric_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='mean')),
            ('scaler', StandardScaler())
        ])
        
        categorical_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='most_frequent')),
            ('encoder', OneHotEncoder(handle_unknown='ignore'))
        ])
        
        self.preprocessing_pipeline = ColumnTransformer(
            transformers=[
                ('num', numeric_transformer, numeric_features),
                ('cat', categorical_transformer, categorical_features)
            ])
        
        # Fit and transform the data
        X_processed = self.preprocessing_pipeline.fit_transform(X)
        
        return X_processed, y
```

#### 4.2.3 Model Training Component

```python
# model_trainer.py
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import Adam
import numpy as np
import pickle
import os

class ModelTrainer:
    def __init__(self):
        self.model = None
        
    def generate_model(self, input_shape, output_shape):
        """Generate a simple neural network model."""
        self.model = Sequential()
        
        # Add layers to the model
        self.model.add(Dense(64, activation='relu', input_shape=(input_shape,)))
        self.model.add(Dropout(0.2))
        self.model.add(Dense(32, activation='relu'))
        self.model.add(Dropout(0.2))
        
        # Output layer
        if output_shape == 1:  # Binary classification or regression
            self.model.add(Dense(1, activation='sigmoid'))
            self.model.compile(optimizer=Adam(), loss='binary_crossentropy', metrics=['accuracy'])
        else:  # Multi-class classification
            self.model.add(Dense(output_shape, activation='softmax'))
            self.model.compile(optimizer=Adam(), loss='categorical_crossentropy', metrics=['accuracy'])
        
        return self.model
    
    def train_model(self, X, y, epochs=100, batch_size=32):
        """Train the neural network model."""
        # Convert to numpy arrays if needed
        if not isinstance(X, np.ndarray):
            X = X.toarray()  # In case of sparse matrix
            
        # Handle output shape
        if len(np.unique(y)) == 2:  # Binary classification
            output_shape = 1
        else:  # Multi-class classification
            output_shape = len(np.unique(y))
            # One-hot encode the target
            y = tf.keras.utils.to_categorical(y)
        
        # Generate model if not already done
        if self.model is None:
            self.generate_model(X.shape[1], output_shape)
        
        # Train the model
        history = self.model.fit(X, y, epochs=epochs, batch_size=batch_size, validation_split=0.2, verbose=1)
        
        return history
    
    def save_model(self, model_path, preprocessing_pipeline=None):
        """Save the trained model and preprocessing pipeline."""
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        # Save the Keras model
        self.model.save(model_path)
        
        # Save the preprocessing pipeline if provided
        if preprocessing_pipeline is not None:
            with open(f"{model_path}_pipeline.pkl", 'wb') as f:
                pickle.dump(preprocessing_pipeline, f)
        
        return True
```

#### 4.2.4 Prediction Component

```python
# predictor.py
import tensorflow as tf
import pickle
import numpy as np

class Predictor:
    def __init__(self):
        self.model = None
        self.preprocessing_pipeline = None
    
    def load_model(self, model_path):
        """Load a trained model and preprocessing pipeline."""
        try:
            # Load the Keras model
            self.model = tf.keras.models.load_model(model_path)
            
            # Load the preprocessing pipeline
            with open(f"{model_path}_pipeline.pkl", 'rb') as f:
                self.preprocessing_pipeline = pickle.load(f)
            
            return True
        except Exception as e:
            return False, str(e)
    
    def predict(self, data):
        """Make predictions using the loaded model."""
        if self.model is None or self.preprocessing_pipeline is None:
            return False, "Model or preprocessing pipeline not loaded."
        
        try:
            # Preprocess the data using the pipeline
            processed_data = self.preprocessing_pipeline.transform(data)
            
            # Convert to numpy array if needed
            if not isinstance(processed_data, np.ndarray):
                processed_data = processed_data.toarray()
            
            # Make predictions
            predictions = self.model.predict(processed_data)
            
            return True, predictions
        except Exception as e:
            return False, str(e)
```

#### 4.2.5 Main Application

```python
# app.py
from ui import UserInterface
from data_handler import DataHandler
from model_trainer import ModelTrainer
from predictor import Predictor
import pandas as pd

def main():
    ui = UserInterface()
    data_handler = DataHandler()
    model_trainer = ModelTrainer()
    predictor = Predictor()
    
    while True:
        # Show main menu
        choice = ui.show_main_menu()
        
        if choice == "Train New Model":
            # Get CSV filename
            filename = ui.get_csv_filename()
            
            # Load CSV file
            success, columns_or_error = data_handler.load_csv(filename)
            if not success:
                ui.display_message(f"Error loading CSV file: {columns_or_error}")
                continue
            
            # Select target feature
            target_feature = ui.select_target_feature(columns_or_error)
            
            # Set target feature
            if not data_handler.set_target_feature(target_feature):
                ui.display_message("Invalid target feature.")
                continue
            
            # Preprocess data
            X_processed, y = data_handler.preprocess_data()
            
            # Train model
            if ui.confirm_action("Start training with default parameters?"):
                history = model_trainer.train_model(X_processed, y)
                ui.display_message("Model training completed.")
                
                # Save model
                if ui.confirm_action("Save the trained model?"):
                    model_path = input("Enter model save path: ")
                    model_trainer.save_model(model_path, data_handler.preprocessing_pipeline)
                    ui.display_message(f"Model saved to {model_path}")
            
        elif choice == "Load Existing Model":
            # Get model path
            model_path = input("Enter model path: ")
            
            # Load model
            success, error = predictor.load_model(model_path)
            if not success:
                ui.display_message(f"Error loading model: {error}")
                continue
            
            ui.display_message("Model loaded successfully.")
            
            # Get prediction data
            try:
                pred_filename = ui.get_csv_filename()
                pred_data = pd.read_csv(pred_filename)
                
                # Make predictions
                success, predictions = predictor.predict(pred_data)
                if not success:
                    ui.display_message(f"Error making predictions: {predictions}")
                    continue
                
                ui.display_message("Predictions:")
                ui.display_message(str(predictions))
            except Exception as e:
                ui.display_message(f"Error processing prediction data: {str(e)}")
        
        elif choice == "Exit":
            break

if __name__ == "__main__":
    main()
```

### 4.3 PoC Testing Plan

1. **Unit Testing**
   - Test CSV loading with valid and invalid files
   - Test feature selection functionality
   - Test data preprocessing pipeline
   - Test model generation and training with sample data
   - Test model saving and loading

2. **Integration Testing**
   - Test the interaction between UI and data handling components
   - Test the flow from data loading to model training
   - Test the prediction workflow

3. **User Interface Testing**
   - Test menu navigation
   - Test user input handling
   - Test error message display

## 5. Demonstration Scenario

To demonstrate the proof of concept, we will prepare a simple end-to-end scenario using the Iris dataset:

1. Load the Iris dataset CSV file
2. Select 'species' as the target feature
3. Preprocess the data automatically
4. Train a neural network model with default parameters
5. Save the trained model
6. Load the model
7. Make predictions on new data

## 6. PoC Success Criteria

The proof of concept will be considered successful if:

1. Users can load a CSV file and select a target feature through the terminal interface
2. Data preprocessing is performed automatically
3. A neural network model is generated and trained successfully
4. The trained model can be saved and loaded
5. The loaded model can make predictions on new data
6. The user experience is intuitive and straightforward

## 7. Implementation Timeline

| Phase | Task | Duration |
|-------|------|----------|
| 1 | Set up development environment | 1 day |
| 2 | Implement UI component | 2 days |
| 3 | Implement data handling component | 2 days |
| 4 | Implement model training component | 3 days |
| 5 | Implement prediction component | 2 days |
| 6 | Integrate components | 2 days |
| 7 | Testing and bug fixing | 3 days |
| 8 | Documentation | 1 day |

Total: 16 days (approximately 3 working weeks)

## 8. Required Resources

- **Development Environment**: Python 3.8+ with required libraries
- **Test Data**: Sample CSV datasets for testing (e.g., Iris, Boston Housing)
- **Development Team**: One Python developer with machine learning experience
- **Testing Team**: One QA engineer for testing

## 9. Risks and Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|------------|------------|
| Performance issues with large datasets | High | Medium | Implement data chunking or sampling for the PoC |
| User interface limitations in terminal | Medium | High | Focus on core functionality with clear instructions |
| Integration challenges between components | Medium | Medium | Use dependency injection and loose coupling |
| Insufficient error handling | Medium | Low | Implement basic error handling for critical functions |

## 10. Conclusion

This proof of concept will demonstrate the feasibility of developing a terminal-based neural network trainer application that allows users to easily load CSV files, preprocess data, train models, and make predictions. The implementation will focus on core functionality using the `simple-term-menu` library for terminal interactions, pandas for data handling, and TensorFlow/Keras for neural network implementation.

Upon successful completion of this PoC, we will have validated the architectural approach and can proceed with full-scale development, incorporating more advanced features and optimizations as outlined in the system design document.

## 11. Next Steps After PoC

1. Evaluate PoC results against success criteria
2. Gather feedback from test users
3. Refine architecture based on findings
4. Develop full implementation plan
5. Address any technical debt from the PoC
6. Implement additional features and optimizations
