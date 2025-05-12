import glob
import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
import matplotlib.pyplot as plt
from datetime import datetime

class OrderVolumeDataset(Dataset):
    """
    Custom dataset class for handling order volume data.
    Converts features and targets into PyTorch tensors and provides
    necessary methods for DataLoader compatibility.
    """
    def __init__(self, features, targets):
        self.features = torch.FloatTensor(features)
        self.targets = torch.FloatTensor(targets)
    
    def __len__(self):
        return len(self.features)
    
    def __getitem__(self, idx):
        return self.features[idx], self.targets[idx]

class ResidualBlock(nn.Module):
    """
    Residual block implementation for deep neural networks.
    Helps prevent vanishing gradients through skip connections.
    
    Args:
        dim (int): The dimension of the input and output features
    """
    def __init__(self, dim):
        super(ResidualBlock, self).__init__()
        self.block = nn.Sequential(
            nn.Linear(dim, dim),
            nn.BatchNorm1d(dim),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(dim, dim),
            nn.BatchNorm1d(dim)
        )
        self.relu = nn.ReLU()

    def forward(self, x):
        residual = x
        out = self.block(x)
        out += residual  # Skip connection
        return self.relu(out)

class ImprovedOrderVolumePredictor(nn.Module):
    """
    Enhanced neural network for order volume prediction.
    Features a deep architecture with residual connections and sophisticated regularization.
    
    Args:
        input_dim (int): Dimension of input features
        hidden_dims (list): List of hidden layer dimensions
    """
    def __init__(self, input_dim, hidden_dims=[128, 256, 512, 256, 128]):
        super(ImprovedOrderVolumePredictor, self).__init__()
        
        layers = []
        
        # Initial feature extraction layers
        layers.extend([
            nn.Linear(input_dim, hidden_dims[0]),
            nn.BatchNorm1d(hidden_dims[0]),
            nn.ReLU(),
            nn.Dropout(0.1)
        ])
        
        # Deep architecture with residual connections
        for i in range(len(hidden_dims) - 1):
            layers.extend([
                nn.Linear(hidden_dims[i], hidden_dims[i + 1]),
                nn.BatchNorm1d(hidden_dims[i + 1]),
                nn.ReLU(),
                nn.Dropout(0.2)
            ])
            
            # Add residual blocks for deeper layers
            if i >= 1:
                layers.append(ResidualBlock(hidden_dims[i + 1]))
        
        # Additional processing layers before final prediction
        layers.extend([
            nn.Linear(hidden_dims[-1], 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(64, 32),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.Dropout(0.1)
        ])
        
        # Final prediction layer
        layers.append(nn.Linear(32, 1))
        
        self.model = nn.Sequential(*layers)
        
        # Initialize weights using He initialization
        self.apply(self._init_weights)
    
    def _init_weights(self, module):
        """Initialize network weights using He initialization"""
        if isinstance(module, nn.Linear):
            nn.init.kaiming_normal_(module.weight, mode='fan_in', nonlinearity='relu')
            if module.bias is not None:
                nn.init.constant_(module.bias, 0)
    
    def forward(self, x):
        return self.model(x)

def prepare_data(csv_path, test_size=0.2, random_state=42):
    """
    Prepare the data for training by reading CSV, encoding features,
    and splitting into train/test sets.
    
    Args:
        csv_path (str): Path to the CSV file
        test_size (float): Proportion of data to use for testing
        random_state (int): Random seed for reproducibility
    
    Returns:
        tuple: Training and test data splits, and the scaler used for target normalization
    """
    # Read and process the CSV file
    df = pd.read_csv(csv_path, encoding='utf-8', quotechar='"', encoding_errors='ignore')
    
    # Separate features and target
    target = df['ORDERVOLUME'].values
    
    # Select categorical columns for encoding
    categorical_columns = ['CUSTOMER_NAME', 'ORDERTYPE', 'WAREHOUSE', 'CITY', 'ORDERWEEK']
    categorical_data = df[categorical_columns]
    
    # Perform one-hot encoding
    encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
    features = encoder.fit_transform(categorical_data)
    
    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(
        features, target, test_size=test_size, random_state=random_state
    )
    
    # Scale the target variable
    scaler = StandardScaler()
    y_train_scaled = scaler.fit_transform(y_train.reshape(-1, 1)).ravel()
    y_test_scaled = scaler.transform(y_test.reshape(-1, 1)).ravel()
    
    return X_train, X_test, y_train_scaled, y_test_scaled, scaler

def train_model(model, train_loader, val_loader, num_epochs=150, learning_rate=0.0005,
                patience=15, max_grad_norm=1.0, device='cuda' if torch.cuda.is_available() else 'cpu'):
    """
    Train the neural network with advanced features including gradient clipping
    and learning rate scheduling.
    
    Args:
        model: The neural network model
        train_loader: DataLoader for training data
        val_loader: DataLoader for validation data
        num_epochs (int): Maximum number of training epochs
        learning_rate (float): Initial learning rate
        patience (int): Number of epochs to wait before early stopping
        max_grad_norm (float): Maximum norm for gradient clipping
        device (str): Device to train on ('cuda' or 'cpu')
    
    Returns:
        tuple: Lists of training and validation losses
    """
    print(f"Training on device: {device}")
    model = model.to(device)
    
    # Initialize optimizer with weight decay for regularization
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=0.01)
    
    # Use a more sophisticated learning rate scheduler
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='min', factor=0.5, patience=5, verbose=True,
        min_lr=1e-6
    )
    
    # Use Huber loss for better handling of outliers
    criterion = nn.HuberLoss(delta=1.0)
    
    # Early stopping and tracking variables
    best_val_loss = float('inf')
    early_stopping_counter = 0
    train_losses = []
    val_losses = []
    
    # Create timestamp for model saves
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
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
            
            # Clip gradients to prevent explosive gradients
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_grad_norm)
            
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
        
        # Print progress with current learning rate
        if (epoch + 1) % 10 == 0:
            current_lr = optimizer.param_groups[0]['lr']
            print(f'Epoch [{epoch+1}/{num_epochs}], LR: {current_lr:.6f}, '
                  f'Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}')
        
        # Early stopping check
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            early_stopping_counter = 0
            # Save best model with timestamp
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'train_loss': train_loss,
                'val_loss': val_loss,
            }, f'best_model_{timestamp}.pth')
        else:
            early_stopping_counter += 1
            if early_stopping_counter >= patience:
                print(f'Early stopping triggered after {epoch+1} epochs')
                break
    
    return train_losses, val_losses

def evaluate_model(model, test_loader, scaler, device):
    """
    Evaluate the model on the test set and calculate various metrics.
    
    Args:
        model: The trained neural network model
        test_loader: DataLoader for test data
        scaler: The scaler used to normalize the target variable
        device (str): Device to evaluate on
    
    Returns:
        tuple: Lists of predictions and actual values, and dictionary of metrics
    """
    model.eval()
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
    
    # Calculate metrics
    test_predictions = np.array(test_predictions)
    actual_values = np.array(actual_values)
    
    mse = np.mean((test_predictions - actual_values) ** 2)
    rmse = np.sqrt(mse)
    mae = np.mean(np.abs(test_predictions - actual_values))
    mape = np.mean(np.abs((actual_values - test_predictions) / actual_values)) * 100
    
    metrics = {
        'MSE': mse,
        'RMSE': rmse,
        'MAE': mae,
        'MAPE': mape
    }
    
    return test_predictions, actual_values, metrics

def plot_training_history(train_losses, val_losses):
    """
    Plot the training and validation loss history.
    
    Args:
        train_losses (list): List of training losses
        val_losses (list): List of validation losses
    """
    plt.figure(figsize=(10, 6))
    plt.plot(train_losses, label='Training Loss')
    plt.plot(val_losses, label='Validation Loss')
    plt.title('Training History')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.grid(True)
    plt.savefig('training_history.png')
    plt.close()

def main():
    """
    Main function to run the entire training and evaluation pipeline.
    """
    # Set random seed for reproducibility
    torch.manual_seed(42)
    np.random.seed(42)
    
    # Set device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Prepare data
    X_train, X_test, y_train, y_test, scaler = prepare_data('2024_OrderVolume_AsofNow.csv')
    
    # Create datasets
    train_dataset = OrderVolumeDataset(X_train, y_train)
    test_dataset = OrderVolumeDataset(X_test, y_test)
    
    # Create data loaders
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=32)
    
    # Initialize model
    input_dim = X_train.shape[1]
    model = ImprovedOrderVolumePredictor(input_dim)
    print(f"Model architecture:\n{model}")
    
    # Train the model
    train_losses, val_losses = train_model(model, train_loader, test_loader, device=device)
    
    # Plot training history
    plot_training_history(train_losses, val_losses)
    
    # Load best model for evaluation
    latest_model_file = max(glob.glob('best_model_*.pth'), key=os.path.getctime)
    checkpoint = torch.load(latest_model_file)
    model.load_state_dict(checkpoint['model_state_dict'])
    
    # Evaluate model
    predictions, actuals, metrics = evaluate_model(model, test_loader, scaler, device)
    
    # Print metrics
    print("\nTest Set Metrics:")
    for metric_name, metric_value in metrics.items():
        print(f"{metric_name}: {metric_value:.4f}")
    
    # Plot predictions vs actuals
    plt.figure(figsize=(10, 6))
    plt.scatter(actuals, predictions, alpha=0.5)
    plt.plot([min(actuals), max(actuals)], [min(actuals), max(actuals)], 'r--')
    plt.xlabel('Actual Values')
    plt.ylabel('Predicted Values')
    plt.title('Predictions vs Actuals')
    plt.savefig('predictions_vs_actuals.png')
    plt.close()

if __name__ == "__main__":
    main()