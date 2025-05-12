#!/usr/bin/env python3
"""
Terminal-Based Neural Network Trainer
Main Application File
"""

from ui import UserInterface
from data_handler import DataHandler
from model_trainer import ModelTrainer
from predictor import Predictor
import pandas as pd
import os
import sys

def main():
    """Main application entry point."""
    ui = UserInterface()
    data_handler = DataHandler()
    model_trainer = ModelTrainer()
    predictor = Predictor()
    
    ui.display_message("Welcome to the Terminal-Based Neural Network Trainer")
    
    while True:
        # Show main menu
        choice = ui.show_main_menu()
        
        if choice == "Train New Model":
            # Get CSV filename
            filename = ui.get_csv_filename()
            
            if not os.path.isfile(filename):
                ui.display_message(f"Error: File '{filename}' not found.")
                continue
            
            # Load CSV file
            success, columns_or_error = data_handler.load_csv(filename)
            if not success:
                ui.display_message(f"Error loading CSV file: {columns_or_error}")
                continue
            
            ui.display_message(f"Successfully loaded CSV with {len(columns_or_error)} columns:")
            ui.display_message(", ".join(columns_or_error))
            
            # Select target feature
            target_feature = ui.select_target_feature(columns_or_error)
            
            # Set target feature
            if not data_handler.set_target_feature(target_feature):
                ui.display_message("Invalid target feature.")
                continue
            
            ui.display_message(f"Selected '{target_feature}' as target feature.")
            
            # Preprocess data
            ui.display_message("Preprocessing data...")
            try:
                X_processed, y = data_handler.preprocess_data()
                ui.display_message("Data preprocessing completed successfully.")
                
                # Show preprocessing summary
                ui.display_message(f"Processed features shape: {X_processed.shape}")
                ui.display_message(f"Target feature shape: {y.shape}")
            except Exception as e:
                ui.display_message(f"Error preprocessing data: {str(e)}")
                continue
            
            # Train model
            if ui.confirm_action("Start training with default parameters?"):
                ui.display_message("Training model with default parameters (100 epochs, batch size 32)...")
                try:
                    history = model_trainer.train_model(X_processed, y)
                    ui.display_message("Model training completed.")
                    
                    # Display training results
                    final_loss = history.history['loss'][-1]
                    final_accuracy = history.history['accuracy'][-1] if 'accuracy' in history.history else 'N/A'
                    ui.display_message(f"Final training loss: {final_loss:.4f}")
                    ui.display_message(f"Final training accuracy: {final_accuracy}")
                    
                    # Save model
                    if ui.confirm_action("Save the trained model?"):
                        model_dir = "models"
                        os.makedirs(model_dir, exist_ok=True)
                        default_name = f"{os.path.splitext(os.path.basename(filename))[0]}_model"
                        model_name = ui.get_input(f"Enter model name [default: {default_name}]: ")
                        model_name = model_name if model_name else default_name
                        model_path = os.path.join(model_dir, model_name)
                        
                        model_trainer.save_model(model_path, data_handler.preprocessing_pipeline)
                        ui.display_message(f"Model saved to {model_path}")
                        
                        # Ask if user wants to make predictions right away
                        if ui.confirm_action("Would you like to make predictions with this model now?"):
                            handle_predictions(ui, predictor, model_path)
                except Exception as e:
                    ui.display_message(f"Error training model: {str(e)}")
            
        elif choice == "Load Existing Model":
            handle_model_loading(ui, predictor)
        
        elif choice == "Exit":
            ui.display_message("Thank you for using the Neural Network Trainer. Goodbye!")
            break


def handle_model_loading(ui, predictor):
    """Handle loading a model and making predictions."""
    # Get model path
    model_dir = "models"
    if os.path.isdir(model_dir):
        models = [f for f in os.listdir(model_dir) if not f.endswith("_pipeline.pkl")]
        if models:
            ui.display_message("Available models:")
            for i, model in enumerate(models, 1):
                ui.display_message(f"{i}. {model}")
            
            model_index = ui.get_integer_input("Enter model number (or 0 to specify a custom path): ", 
                                             min_val=0, max_val=len(models))
            
            if model_index == 0:
                model_path = ui.get_input("Enter model path: ")
            else:
                model_path = os.path.join(model_dir, models[model_index-1])
        else:
            ui.display_message("No models found in the models directory.")
            model_path = ui.get_input("Enter model path: ")
    else:
        model_path = ui.get_input("Enter model path: ")
    
    # Load model
    ui.display_message(f"Loading model from {model_path}...")
    result = predictor.load_model(model_path)
    
    if isinstance(result, tuple) and not result[0]:
        ui.display_message(f"Error loading model: {result[1]}")
        return
    
    ui.display_message("Model loaded successfully.")
    
    # Handle predictions
    handle_predictions(ui, predictor, model_path)


def handle_predictions(ui, predictor, model_path):
    """Handle making predictions with a loaded model."""
    # Get prediction data
    filename = ui.get_csv_filename()
    
    if not os.path.isfile(filename):
        ui.display_message(f"Error: File '{filename}' not found.")
        return
    
    try:
        # Load prediction data
        ui.display_message(f"Loading prediction data from {filename}...")
        pred_data = pd.read_csv(filename)
        ui.display_message(f"Loaded prediction data with shape: {pred_data.shape}")
        
        # Make predictions
        ui.display_message("Making predictions...")
        result = predictor.predict(pred_data)
        
        if isinstance(result, tuple) and not result[0]:
            ui.display_message(f"Error making predictions: {result[1]}")
            return
        
        predictions = result[1] if isinstance(result, tuple) else result
        
        # Display predictions summary
        ui.display_message("Predictions:")
        if hasattr(predictions, 'shape') and len(predictions.shape) > 1 and predictions.shape[1] > 1:
            # Multi-class predictions
            ui.display_message(f"Generated {len(predictions)} multi-class predictions.")
            sample_size = min(5, len(predictions))
            ui.display_message(f"First {sample_size} predictions (showing classes with highest probability):")
            for i in range(sample_size):
                max_class = predictions[i].argmax()
                ui.display_message(f"  Sample {i+1}: Class {max_class} (Probability: {predictions[i][max_class]:.4f})")
        else:
            # Binary or regression predictions
            ui.display_message(f"Generated {len(predictions)} predictions.")
            sample_size = min(5, len(predictions))
            ui.display_message(f"First {sample_size} predictions:")
            for i in range(sample_size):
                ui.display_message(f"  Sample {i+1}: {float(predictions[i]):.4f}")
        
        # Save predictions
        if ui.confirm_action("Would you like to save the predictions to a CSV file?"):
            output_dir = "predictions"
            os.makedirs(output_dir, exist_ok=True)
            default_name = f"{os.path.splitext(os.path.basename(filename))[0]}_predictions.csv"
            output_path = os.path.join(output_dir, default_name)
            
            # Create DataFrame with predictions
            pred_df = pd.DataFrame(pred_data)  # Copy input data
            if hasattr(predictions, 'shape') and len(predictions.shape) > 1 and predictions.shape[1] > 1:
                # Multi-class predictions
                for i in range(predictions.shape[1]):
                    pred_df[f'prediction_class_{i}'] = predictions[:, i]
                pred_df['predicted_class'] = predictions.argmax(axis=1)
            else:
                # Binary or regression predictions
                pred_df['prediction'] = predictions
            
            # Save to CSV
            pred_df.to_csv(output_path, index=False)
            ui.display_message(f"Predictions saved to {output_path}")
    
    except Exception as e:
        ui.display_message(f"Error processing prediction data: {str(e)}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting due to user interrupt.")
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        sys.exit(1)