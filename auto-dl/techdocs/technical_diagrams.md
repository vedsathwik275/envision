# Technical Diagrams

## User Flow Diagram

```mermaid
flowchart TD
    A[Start] --> B[Input CSV File Name]
    B --> C[Parse CSV Columns]
    C --> D{Choose Target Feature?}
    D -->|Yes| E[Select Target Feature]
    E --> F[Automate Preprocessing]
    F --> G[Find Best Input Features]
    G --> H[Generate Neural Network]
    H --> I[Train Neural Network]
    I --> J[Save Trained Model]
    J --> K{Run Predictions?}
    K -->|Yes| L[Input New Data]
    L --> M[Preprocess Input Data]
    M --> N[Load Trained Model]
    N --> O[Make Predictions]
    O --> P[Display Predictions]
    K -->|No| Q[End]
```

## System Sequence Diagram

```mermaid
sequenceDiagram
    participant User
    participant TerminalApp as Terminal-Based Neural Network Trainer
    participant CSVFile as CSV File
    participant ModelStorage as Model Storage
    User ->> TerminalApp: Input CSV File Name
    TerminalApp ->> CSVFile: Parse CSV Columns
    CSVFile -->> TerminalApp: Return Columns
    User ->> TerminalApp: Choose Target Feature
    TerminalApp ->> TerminalApp: Automate Preprocessing
    TerminalApp ->> TerminalApp: Find Best Input Features
    TerminalApp ->> TerminalApp: Generate Neural Network
    User ->> TerminalApp: Train Neural Network
    TerminalApp ->> ModelStorage: Save Trained Model
    User ->> TerminalApp: Run Predictions
    TerminalApp ->> ModelStorage: Load Trained Model
    User ->> TerminalApp: Input New Data
    TerminalApp ->> TerminalApp: Preprocess Input Data
    TerminalApp ->> TerminalApp: Make Predictions
    TerminalApp ->> User: Display Predictions
```

## Decision Tree

```mermaid
graph TD
    A[Start] --> B{Is CSV File Valid?}
    B -->|Yes| C{Is Target Feature Selected?}
    B -->|No| D[Request New CSV File]
    C -->|Yes| E{Is Preprocessing Complete?}
    C -->|No| F[Request Target Feature Selection]
    E -->|Yes| G{Train Neural Network?}
    E -->|No| H[Preprocess Data]
    G -->|Yes| I[Train and Save Model]
    G -->|No| J{Run Predictions?}
    J -->|Yes| K[Input New Data]
    J -->|No| L[End]
    K --> M{Data Preprocessed?}
    M -->|Yes| N[Make Predictions]
    M -->|No| O[Preprocess New Data]
```

## State Diagram

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> CSVInput: Waiting for CSV Input
    CSVInput --> Parsing: CSV File Input Received
    Parsing --> FeatureSelection: Columns Parsed
    FeatureSelection --> Preprocessing: Target Feature Selected
    Preprocessing --> NNGeneration: Data Preprocessed
    NNGeneration --> Training: Neural Network Generated
    Training --> ModelSaving: Model Trained
    ModelSaving --> PredictionReady: Model Saved
    PredictionReady --> Prediction: Run Predictions
    Prediction --> End[End]
    End --> [*]
```

This set of diagrams provides a comprehensive visualization of the terminal-based Python application for training and deploying neural networks using CSV data. Each diagram covers different aspects of the system, ensuring clarity and understanding of user interactions, system sequences, decision points, and state transitions.