#!/usr/bin/env python3
"""
Test script for the Order Volume Neural Network Model.
This script demonstrates loading the model, training it, and generating predictions.
"""

from order_volume_model import OrderVolumeModel
import argparse

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Order Volume Model Testing')
    parser.add_argument('--data', type=str, default='data/OrderVolume_ByMonth_v2.csv',
                        help='Path to the data file')
    parser.add_argument('--load', type=str, default=None,
                        help='Path to load a pre-trained model')
    parser.add_argument('--epochs', type=int, default=100,
                        help='Number of training epochs')
    parser.add_argument('--batch-size', type=int, default=32,
                        help='Batch size for training')
    parser.add_argument('--predict-months', type=int, default=6,
                        help='Number of months to predict')
    parser.add_argument('--save', type=str, default='order_volume_model',
                        help='Path to save the trained model')
    parser.add_argument('--evaluate-only', action='store_true',
                        help='Only evaluate and predict using a pre-trained model')
    
    return parser.parse_args()

def main():
    """Main function to test the order volume model."""
    # Parse command line arguments
    args = parse_args()
    
    print("=" * 50)
    print("Order Volume Neural Network Model Test")
    print("=" * 50)
    
    # Initialize model
    model = OrderVolumeModel(data_path=args.data, model_path=args.load)
    
    if args.load and args.evaluate_only:
        print(f"Loaded pre-trained model from {args.load}")
        print("Generating predictions...")
        predictions = model.predict_future(months=args.predict_months)
        print(f"Predictions saved to 'future_predictions.csv'")
    else:
        # Preprocess data
        model.preprocess_data()
        
        # Prepare train/test split
        model.prepare_train_test_split(test_size=0.2)
        
        if not args.load:
            # Build model
            model.build_model()
            
            # Train model
            print(f"\nTraining model with {args.epochs} epochs and batch size {args.batch_size}...")
            history = model.train(epochs=args.epochs, batch_size=args.batch_size)
        
        # Evaluate model
        print("\nEvaluating model...")
        metrics = model.evaluate()
        
        # Generate predictions
        print(f"\nGenerating predictions for the next {args.predict_months} months...")
        predictions = model.predict_future(months=args.predict_months)
        
        # Save model
        if args.save:
            model.save_model(args.save)
            print(f"Model saved to {args.save}")
    
    print("\nTest completed successfully!")

if __name__ == "__main__":
    main() 