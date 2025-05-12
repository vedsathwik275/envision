#!/usr/bin/env python3
"""
Terminal-Based Neural Network Trainer
Main Application File - Updated with better error handling
"""

from ui import UserInterface
from data_handler import DataHandler
from model_trainer import ModelTrainer
from predictor import Predictor
import pandas as pd
import os
import sys
import traceback

def main():
    """Main application entry point."""
    ui = UserInterface()
    data_handler = DataHandler()
    model_trainer = ModelTrainer()
    predictor = Predictor()
    
    ui.display_message("Welcome to the Terminal-Based Neural Network Trainer")
    
    while True:
        try:
            # Show main menu
            choice = ui.show_main_menu()
            
            if choice == "Train New Model":
                # Get CSV filename
                filename = ui.get_csv_filename()
                
                if not os.path.isfile(filename):
                    ui.display_message(f"Error: File '{filename}' not found.")
                    continue
                
                # Load CSV file
                ui.display_message(f"Loading CSV file '{filename}'...")
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
                    ui.display_message("Detailed error information:")
                    ui.display_message(traceback.format_exc())
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
                            
                            model_trainer.save_model(model_path, data_handler.preprocessing_pipeline, data_handler.label_encoder)
                            ui.display_message(f"Model saved to {model_path}")
                            
                            # Ask if user wants to make predictions right away
                            if ui.confirm_action("Would you like to make predictions with this model now?"):
                                handle_predictions(ui, predictor, model_path)
                    except Exception as e:
                        ui.display_message(f"Error training model: {str(e)}")
                        ui.display_message("Detailed error information:")
                        ui.display_message(traceback.format_exc())
                
            elif choice == "Load Existing Model":
                handle_model_loading(ui, predictor)
            
            elif choice == "Exit":
                ui.display_message("Thank you for using the Neural Network Trainer. Goodbye!")
                break
        
        except Exception as e:
            ui.display_message(f"An unexpected error occurred: {str(e)}")
            ui.display_message("Detailed error information:")
            ui.display_message(traceback.format_exc())
            if ui.confirm_action("Do you want to continue?"):
                continue
            else:
                ui.display_message("Exiting due to error.")
                break


def handle_model_loading(ui, predictor):
    """Handle loading a model and making predictions."""
    try:
        # Get model path
        model_dir = "models"
        if os.path.isdir(model_dir):
            models = [f for f in os.listdir(model_dir) if not f.endswith("_pipeline.pkl") and not f.endswith("_label_encoder.pkl") and not f.endswith("_info.json")]
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
        
        # Display model info if available
        model_info = predictor.get_model_info()
        if model_info:
            ui.display_message("Model information:")
            if 'problem_type' in model_info:
                ui.display_message(f"Problem type: {model_info['problem_type']}")
            if 'architecture' in model_info:
                ui.display_message(f"Architecture: {model_info['architecture']}")
            if 'training' in model_info and 'epochs' in model_info['training']:
                ui.display_message(f"Training epochs: {model_info['training']['epochs']}")
        
        # Handle predictions
        handle_predictions(ui, predictor, model_path)
    
    except Exception as e:
        ui.display_message(f"Error during model loading: {str(e)}")
        ui.display_message("Detailed error information:")
        ui.display_message(traceback.format_exc())


def handle_predictions(ui, predictor, model_path):
    """Handle making predictions with a loaded model."""
    try:
        # Get prediction data
        filename = ui.get_csv_filename()
        
        if not os.path.isfile(filename):
            ui.display_message(f"Error: File '{filename}' not found.")
            return
        
        # Load prediction data
        ui.display_message(f"Loading prediction data from {filename}...")
        pred_data = pd.read_csv(filename)
        # Clean column names (remove whitespace)
        pred_data.columns = pred_data.columns.str.strip()
        ui.display_message(f"Loaded prediction data with shape: {pred_data.shape}")
        
        # Make predictions
        ui.display_message("Making predictions...")
        result = predictor.predict(pred_data)
        
        if isinstance(result, tuple) and not result[0]:
            ui.display_message(f"Error making predictions: {result[1]}")
            return
        
        predictions = result[1] if isinstance(result, tuple) else result
        
        # Decode predictions if it's a classification problem
        decoded_predictions = predictor.decode_predictions(predictions)
        
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
                if predictor.label_encoder is not None:
                    original_class = predictor.label_encoder.inverse_transform([max_class])[0]
                    ui.display_message(f"    Original class: {original_class}")
        else:
            # Binary or regression predictions
            ui.display_message(f"Generated {len(predictions)} predictions.")
            sample_size = min(5, len(predictions))
            ui.display_message(f"First {sample_size} predictions:")
            for i in range(sample_size):
                ui.display_message(f"  Sample {i+1}: {float(predictions[i]):.4f}")
                if predictor.label_encoder is not None and hasattr(decoded_predictions, '__iter__'):
                    ui.display_message(f"    Original class: {decoded_predictions[i]}")
        
        # Save predictions
        if ui.confirm_action("Would you like to save the predictions to a CSV file?"):
            output_dir = "predictions"
            os.makedirs(output_dir, exist_ok=True)
            default_name = f"{os.path.splitext(os.path.basename(filename))[0]}_predictions.csv"
            output_path = os.path.join(output_dir, default_name)
            
            # Create DataFrame with predictions
            pred_df = pd.DataFrame(pred_data)  # Copy input data
            
            # Add decoded predictions if available
            if predictor.label_encoder is not None and hasattr(decoded_predictions, '__iter__'):
                pred_df['prediction_class'] = decoded_predictions
            
            # Add raw predictions
            if hasattr(predictions, 'shape') and len(predictions.shape) > 1 and predictions.shape[1] > 1:
                # Multi-class predictions
                for i in range(predictions.shape[1]):
                    class_name = f'prediction_class_{i}'
                    if predictor.label_encoder is not None:
                        try:
                            original_class = predictor.label_encoder.inverse_transform([i])[0]
                            class_name = f'prediction_{original_class}'
                        except:
                            pass
                    pred_df[class_name] = predictions[:, i]
                pred_df['predicted_class_index'] = predictions.argmax(axis=1)
            else:
                # Binary or regression predictions
                pred_df['prediction'] = predictions
            
            # Save to CSV
            pred_df.to_csv(output_path, index=False)
            ui.display_message(f"Predictions saved to {output_path}")
    
    except Exception as e:
        ui.display_message(f"Error processing prediction data: {str(e)}")
        ui.display_message("Detailed error information:")
        ui.display_message(traceback.format_exc())


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting due to user interrupt.")
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        print(traceback.format_exc())
        sys.exit(1)