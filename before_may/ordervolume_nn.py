import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.model_selection import KFold
from torch.utils.data import SubsetRandomSampler

# Custom dataset class to handle our data
class OrderVolumeDataset(Dataset):
    def __init__(self, features, targets):
        self.features = torch.FloatTensor(features)
        self.targets = torch.FloatTensor(targets)
    
    def __len__(self):
        return len(self.features)
    
    def __getitem__(self, idx):
        return self.features[idx], self.targets[idx]

# Neural network architecture
class OrderVolumePredictor(nn.Module):
    def __init__(self, input_dim, hidden_dims=[64, 128, 256, 128, 64]):
        super(OrderVolumePredictor, self).__init__()
        
        layers = []
        prev_dim = input_dim
        
        for hidden_dim in hidden_dims:
            layers.extend([
                nn.Linear(prev_dim, hidden_dim),
                nn.BatchNorm1d(hidden_dim),
                nn.ReLU(),
                nn.Dropout(0.2),  # Increased dropout
            ])
            prev_dim = hidden_dim
        
        # Add a final layer before output
        layers.extend([
            nn.Linear(prev_dim, 32),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.Dropout(0.1)
        ])
        
        layers.append(nn.Linear(32, 1))
        
        self.model = nn.Sequential(*layers)
    
    def forward(self, x):
        return self.model(x)

def prepare_data(csv_path, test_size=0.2, random_state=42):
    """
    Prepare the data for training by reading CSV and preprocessing features
    """
    # Read the CSV file
    df = pd.read_csv(csv_path, encoding='utf-8', quotechar='"', encoding_errors='ignore')
    
    # Convert ORDERWEEK to a proper date format and extract week number
    df['ORDERWEEK'] = df['ORDERWEEK'].apply(lambda x: int(x.split()[1]))  # Extract just the week number
    
    # Create cyclical features for the week number
    # This helps the model understand the cyclical nature of weeks in a year
    df['WEEK_SIN'] = np.sin(2 * np.pi * df['ORDERWEEK']/53)  # Using 53 weeks to account for full year
    df['WEEK_COS'] = np.cos(2 * np.pi * df['ORDERWEEK']/53)
    
    # Separate features and target
    target = df['ORDERVOLUME'].values
    
    # Select features for encoding
    categorical_columns = ['CUSTOMER_NAME', 'ORDERTYPE', 'WAREHOUSE', 'CITY']
    numerical_columns = ['WEEK_SIN', 'WEEK_COS']
    
    # Process categorical features
    categorical_data = df[categorical_columns]
    encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
    categorical_features = encoder.fit_transform(categorical_data)
    
    # Process numerical features
    numerical_data = df[numerical_columns]
    scaler_features = StandardScaler()
    numerical_features = scaler_features.fit_transform(numerical_data)
    
    # Combine all features
    features = np.hstack([categorical_features, numerical_features])
    
    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(
        features, target, test_size=test_size, random_state=random_state
    )
    
    # Scale the target variable
    scaler_target = StandardScaler()
    y_train_scaled = scaler_target.fit_transform(y_train.reshape(-1, 1)).ravel()
    y_test_scaled = scaler_target.transform(y_test.reshape(-1, 1)).ravel()
    
    return X_train, X_test, y_train_scaled, y_test_scaled, scaler_target

def train_model(model, train_loader, val_loader, num_epochs=150,  # Increased epochs
                learning_rate=0.001, 
                patience=15,  # Increased patience
                device='cuda' if torch.cuda.is_available() else 'cpu'):
    """
    Train the neural network with early stopping
    """
    model = model.to(device)
    
    # Use AdamW instead of Adam and add weight decay
    optimizer = optim.AdamW(model.parameters(), 
                           lr=learning_rate,
                           weight_decay=0.01)  # L2 regularization
    
    # Modified learning rate scheduler
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, 
        mode='min',
        factor=0.5,
        patience=5,
        min_lr=1e-6,
        verbose=True
    )
    
    criterion = nn.HuberLoss(delta=1.0)  # Use Huber loss instead of MSE
    
    print(f"Training on device: {device}")
    model = model.to(device)
    
    # Early stopping variables
    best_val_loss = float('inf')
    early_stopping_counter = 0
    
    # Training history
    train_losses = []
    val_losses = []
    
    for epoch in range(num_epochs):
        # Training phase
        model.train()
        train_loss = 0.0
        for features, targets in train_loader:
            features, targets = features.to(device), targets.to(device)
            
            optimizer.zero_grad()
            outputs = model(features).squeeze()
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
        
        train_loss /= len(train_loader)
        train_losses.append(train_loss)
        
        # Validation phase
        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for features, targets in val_loader:
                features, targets = features.to(device), targets.to(device)
                outputs = model(features).squeeze()
                val_loss += criterion(outputs, targets).item()
        
        val_loss /= len(val_loader)
        val_losses.append(val_loss)
        
        # Learning rate scheduling
        scheduler.step(val_loss)
        
        # Print progress
        if (epoch + 1) % 10 == 0:
            print(f'Epoch [{epoch+1}/{num_epochs}], Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}')
        
        # Early stopping check
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            early_stopping_counter = 0
            # Save best model
            torch.save(model.state_dict(), 'best_model.pth')
        else:
            early_stopping_counter += 1
            if early_stopping_counter >= patience:
                print(f'Early stopping triggered after {epoch+1} epochs')
                break
    
    return train_losses, val_losses

def k_fold_cross_validation(dataset, k_folds, input_dim, batch_size=32, num_epochs=100):
    """
    Perform k-fold cross validation on our OrderVolumePredictor model.
    
    Args:
        dataset: The full dataset to perform cross-validation on
        k_folds: Number of folds for cross-validation
        input_dim: Input dimension for the model
        batch_size: Batch size for training
        num_epochs: Number of epochs to train each fold
    
    Returns:
        Dictionary containing training history and performance metrics for each fold
    """
    # Initialize k-fold cross validation
    kfold = KFold(n_splits=k_folds, shuffle=True, random_state=42)
    
    # Store results for each fold
    fold_results = {
        'train_losses': [],
        'val_losses': [],
        'mse_scores': [],
        'rmse_scores': [],
        'mae_scores': []
    }
    
    # Device configuration
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")

    # Perform k-fold cross validation
    for fold, (train_ids, val_ids) in enumerate(kfold.split(dataset)):
        print(f'\nFold {fold + 1}/{k_folds}')
        
        # Create data samplers for obtaining train/validation batches
        train_sampler = SubsetRandomSampler(train_ids)
        val_sampler = SubsetRandomSampler(val_ids)
        
        # Create data loaders for this fold
        train_loader = DataLoader(
            dataset,
            batch_size=batch_size,
            sampler=train_sampler,
        )
        val_loader = DataLoader(
            dataset,
            batch_size=batch_size,
            sampler=val_sampler,
        )
        
        # Initialize a fresh model for this fold
        model = OrderVolumePredictor(input_dim).to(device)
        
        # Train the model on this fold
        train_loss_history, val_loss_history = train_model(
            model=model,
            train_loader=train_loader,
            val_loader=val_loader,
            num_epochs=num_epochs,
            device=device
        )
        
        # Evaluate model on validation set
        model.eval()
        val_predictions = []
        val_actuals = []
        
        with torch.no_grad():
            for features, targets in val_loader:
                features, targets = features.to(device), targets.to(device)
                outputs = model(features).squeeze()
                val_predictions.extend(outputs.cpu().numpy())
                val_actuals.extend(targets.cpu().numpy())
        
        # Calculate metrics for this fold
        mse = np.mean((np.array(val_predictions) - np.array(val_actuals)) ** 2)
        rmse = np.sqrt(mse)
        mae = np.mean(np.abs(np.array(val_predictions) - np.array(val_actuals)))
        
        # Store results for this fold
        fold_results['train_losses'].append(train_loss_history)
        fold_results['val_losses'].append(val_loss_history)
        fold_results['mse_scores'].append(mse)
        fold_results['rmse_scores'].append(rmse)
        fold_results['mae_scores'].append(mae)
        
        print(f'Fold {fold + 1} - MSE: {mse:.4f}, RMSE: {rmse:.4f}, MAE: {mae:.4f}')

    # Calculate and print average metrics across all folds
    avg_mse = np.mean(fold_results['mse_scores'])
    avg_rmse = np.mean(fold_results['rmse_scores'])
    avg_mae = np.mean(fold_results['mae_scores'])
    
    print('\nAverage metrics across all folds:')
    print(f'MSE: {avg_mse:.4f} ± {np.std(fold_results["mse_scores"]):.4f}')
    print(f'RMSE: {avg_rmse:.4f} ± {np.std(fold_results["rmse_scores"]):.4f}')
    print(f'MAE: {avg_mae:.4f} ± {np.std(fold_results["mae_scores"]):.4f}')
    
    return fold_results

def evaluate_model(model, test_loader, scaler):
    """
    Evaluate the model on the test set and print metrics
    """
    model.eval()
    device = next(model.parameters()).device
    test_predictions = []
    actual_values = []
    
    with torch.no_grad():
        for features, targets in test_loader:
            features, targets = features.to(device), targets.to(device)
            outputs = model(features).squeeze()
            # Convert predictions back to original scale
            predictions = scaler.inverse_transform(outputs.cpu().numpy().reshape(-1, 1)).ravel()
            actual = scaler.inverse_transform(targets.cpu().numpy().reshape(-1, 1)).ravel()
            test_predictions.extend(predictions)
            actual_values.extend(actual)
    
    # Calculate and print metrics
    mse = np.mean((np.array(test_predictions) - np.array(actual_values)) ** 2)
    rmse = np.sqrt(mse)
    mae = np.mean(np.abs(np.array(test_predictions) - np.array(actual_values)))
    
    print("\nFinal Test Set Metrics:")
    print(f"MSE: {mse:.4f}")
    print(f"RMSE: {rmse:.4f}")
    print(f"MAE: {mae:.4f}")

def main():
    # Set random seed for reproducibility
    torch.manual_seed(42)
    np.random.seed(42)
    
    # Prepare all data
    X_train, X_test, y_train, y_test, scaler = prepare_data('2024_OrderVolume_AsofNow.csv')
    
    # Create full training dataset
    full_dataset = OrderVolumeDataset(X_train, y_train)
    
    # Perform k-fold cross validation
    input_dim = X_train.shape[1]
    fold_results = k_fold_cross_validation(
        dataset=full_dataset,
        k_folds=5,  # Using 5-fold cross validation
        input_dim=input_dim,
        batch_size=32,
        num_epochs=100
    )
    
    # After k-fold validation, train a final model on all training data
    # and evaluate on the test set
    final_model = OrderVolumePredictor(input_dim)
    final_train_loader = DataLoader(full_dataset, batch_size=32, shuffle=True)
    test_dataset = OrderVolumeDataset(X_test, y_test)
    test_loader = DataLoader(test_dataset, batch_size=32)
    
    # Train final model
    train_model(final_model, final_train_loader, test_loader)
    
    # Evaluate final model on test set
    evaluate_model(final_model, test_loader, scaler)

if __name__ == "__main__":
    main()