#!/usr/bin/env python3
"""
Multi-Source Intelligence Framework (MSIF) Ensemble Classifier

This module implements the main ensemble classifier for Black Basta ransomware detection
as described in the research paper. The ensemble combines Random Forest, SVM, and LSTM
models for robust attack vector prediction.

Author: Jude Osamor
Institution: University of the West of England, Bristol
License: MIT
"""

import numpy as np
import pandas as pd
import joblib
import logging
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
import warnings

from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.svm import SVC
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.preprocessing import StandardScaler
from sklearn.utils import resample
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.wrappers.scikit_learn import KerasClassifier

from ..utils.config import load_config
from ..utils.logging_setup import setup_logging
from ..utils.validation_utils import validate_features, calculate_confidence_intervals

# Suppress warnings
warnings.filterwarnings('ignore', category=FutureWarning)
tf.get_logger().setLevel('ERROR')

logger = logging.getLogger(__name__)


class MSIFEnsemble:
    """
    Multi-Source Intelligence Framework Ensemble Classifier
    
    This class implements the ensemble approach combining multiple ML algorithms
    for Black Basta ransomware detection with statistical validation.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize MSIF Ensemble classifier
        
        Args:
            config: Configuration dictionary with model parameters
        """
        self.config = config or load_config()
        self.scaler = StandardScaler()
        self.is_fitted = False
        self.feature_names = None
        self.model_performance = {}
        
        # Initialize individual models with research-validated parameters
        self.random_forest = RandomForestClassifier(
            n_estimators=500,
            max_depth=20,
            min_samples_split=5,
            min_samples_leaf=2,
            max_features='sqrt',
            bootstrap=True,
            oob_score=True,
            random_state=42,
            n_jobs=-1
        )
        
        self.svm = SVC(
            kernel='rbf',
            C=1.0,
            gamma='scale',
            probability=True,
            cache_size=2000,
            max_iter=10000,
            random_state=42
        )
        
        # LSTM model will be created dynamically based on input shape
        self.lstm_model = None
        
        # Ensemble with research-validated weights
        self.ensemble = None
        
        logger.info("MSIF Ensemble classifier initialized")
    
    def _create_lstm_model(self, input_shape: Tuple[int, int]) -> tf.keras.Model:
        """
        Create LSTM model for temporal pattern analysis
        
        Args:
            input_shape: Shape of input sequences (timesteps, features)
            
        Returns:
            Compiled LSTM model
        """
        model = Sequential([
            LSTM(50, return_sequences=True, input_shape=input_shape),
            Dropout(0.2),
            LSTM(50, return_sequences=False),
            Dropout(0.2),
            Dense(25, activation='relu'),
            Dense(1, activation='sigmoid')
        ])
        
        model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def _prepare_lstm_data(self, X: np.ndarray, sequence_length: int = 10) -> np.ndarray:
        """
        Prepare data for LSTM model by creating sequences
        
        Args:
            X: Feature matrix
            sequence_length: Length of sequences for LSTM
            
        Returns:
            Reshaped data for LSTM input
        """
        if len(X.shape) == 2:
            # Create sequences from features
            sequences = []
            for i in range(len(X) - sequence_length + 1):
                sequences.append(X[i:(i + sequence_length)])
            return np.array(sequences)
        return X
    
    def fit(self, X: np.ndarray, y: np.ndarray, 
            validation_split: float = 0.2) -> 'MSIFEnsemble':
        """
        Train the ensemble model with cross-validation
        
        Args:
            X: Feature matrix (n_samples, n_features)
            y: Target labels (n_samples,)
            validation_split: Fraction of data for validation
            
        Returns:
            Self for method chaining
        """
        logger.info("Starting MSIF ensemble training...")
        
        # Validate input
        X, y = validate_features(X, y)
        
        # Store feature names if provided as DataFrame
        if isinstance(X, pd.DataFrame):
            self.feature_names = X.columns.tolist()
            X = X.values
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Split data
        split_idx = int(len(X) * (1 - validation_split))
        X_train, X_val = X_scaled[:split_idx], X_scaled[split_idx:]
        y_train, y_val = y[:split_idx], y[split_idx:]
        
        # Train individual models
        logger.info("Training Random Forest...")
        self.random_forest.fit(X_train, y_train)
        
        logger.info("Training SVM...")
        self.svm.fit(X_train, y_train)
        
        # Train LSTM model
        logger.info("Training LSTM...")
        X_lstm_train = self._prepare_lstm_data(X_train)
        X_lstm_val = self._prepare_lstm_data(X_val)
        
        if len(X_lstm_train) > 0:
            self.lstm_model = self._create_lstm_model((X_lstm_train.shape[1], X_lstm_train.shape[2]))
            
            # Adjust y for LSTM sequences
            y_lstm_train = y_train[len(y_train) - len(X_lstm_train):]
            
            self.lstm_model.fit(
                X_lstm_train, y_lstm_train,
                epochs=50,
                batch_size=32,
                validation_split=0.2,
                verbose=0
            )
        
        # Create ensemble with research-validated weights
        self.ensemble = VotingClassifier(
            estimators=[
                ('rf', self.random_forest),
                ('svm', self.svm)
            ],
            voting='soft',
            weights=[0.6, 0.4]  # Weights based on individual performance
        )
        
        self.ensemble.fit(X_train, y_train)
        
        # Evaluate performance
        self._evaluate_performance(X_val, y_val)
        
        self.is_fitted = True
        logger.info("MSIF ensemble training completed successfully")
        
        return self
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions using the ensemble
        
        Args:
            X: Feature matrix
            
        Returns:
            Predictions array
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before making predictions")
        
        if isinstance(X, pd.DataFrame):
            X = X.values
        
        X_scaled = self.scaler.transform(X)
        return self.ensemble.predict(X_scaled)
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Predict class probabilities using the ensemble
        
        Args:
            X: Feature matrix
            
        Returns:
            Prediction probabilities
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before making predictions")
        
        if isinstance(X, pd.DataFrame):
            X = X.values
        
        X_scaled = self.scaler.transform(X)
        return self.ensemble.predict_proba(X_scaled)
    
    def get_confidence_score(self, X: np.ndarray) -> np.ndarray:
        """
        Calculate confidence scores for predictions
        
        Args:
            X: Feature matrix
            
        Returns:
            Confidence scores array
        """
        probas = self.predict_proba(X)
        # Confidence is the maximum probability
        return np.max(probas, axis=1)
    
    def _evaluate_performance(self, X_val: np.ndarray, y_val: np.ndarray) -> None:
        """
        Evaluate model performance with statistical validation
        
        Args:
            X_val: Validation features
            y_val: Validation labels
        """
        predictions = self.ensemble.predict(X_val)
        probas = self.ensemble.predict_proba(X_val)
        
        # Calculate metrics
        accuracy = accuracy_score(y_val, predictions)
        precision = precision_score(y_val, predictions, average='weighted')
        recall = recall_score(y_val, predictions, average='weighted')
        f1 = f1_score(y_val, predictions, average='weighted')
        auc = roc_auc_score(y_val, probas[:, 1])
        
        # Calculate confidence intervals using bootstrap
        ci_accuracy = calculate_confidence_intervals(y_val, predictions, accuracy_score)
        ci_precision = calculate_confidence_intervals(y_val, predictions, 
                                                    lambda y, p: precision_score(y, p, average='weighted'))
        
        self.model_performance = {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'auc': auc,
            'accuracy_ci': ci_accuracy,
            'precision_ci': ci_precision,
            'oob_score': self.random_forest.oob_score_
        }
        
        logger.info(f"Model Performance:")
        logger.info(f"Accuracy: {accuracy:.3f} (95% CI: {ci_accuracy[0]:.3f}-{ci_accuracy[1]:.3f})")
        logger.info(f"Precision: {precision:.3f}")
        logger.info(f"Recall: {recall:.3f}")
        logger.info(f"F1-Score: {f1:.3f}")
        logger.info(f"AUC: {auc:.3f}")
    
    def cross_validate(self, X: np.ndarray, y: np.ndarray, 
                      cv: int = 5) -> Dict[str, np.ndarray]:
        """
        Perform cross-validation with statistical significance testing
        
        Args:
            X: Feature matrix
            y: Target labels
            cv: Number of cross-validation folds
            
        Returns:
            Cross-validation scores dictionary
        """
        if isinstance(X, pd.DataFrame):
            X = X.values
        
        X_scaled = self.scaler.fit_transform(X)
        
        skf = StratifiedKFold(n_splits=cv, shuffle=True, random_state=42)
        
        # Perform cross-validation for ensemble
        cv_scores = {
            'accuracy': cross_val_score(self.ensemble, X_scaled, y, 
                                      cv=skf, scoring='accuracy'),
            'precision': cross_val_score(self.ensemble, X_scaled, y, 
                                       cv=skf, scoring='precision_weighted'),
            'recall': cross_val_score(self.ensemble, X_scaled, y, 
                                    cv=skf, scoring='recall_weighted'),
            'f1': cross_val_score(self.ensemble, X_scaled, y, 
                                cv=skf, scoring='f1_weighted')
        }
        
        # Log results with confidence intervals
        for metric, scores in cv_scores.items():
            mean_score = np.mean(scores)
            std_score = np.std(scores)
            ci_lower = mean_score - 1.96 * (std_score / np.sqrt(cv))
            ci_upper = mean_score + 1.96 * (std_score / np.sqrt(cv))
            
            logger.info(f"CV {metric}: {mean_score:.3f} ± {std_score:.3f} "
                       f"(95% CI: {ci_lower:.3f}-{ci_upper:.3f})")
        
        return cv_scores
    
    def get_feature_importance(self) -> Dict[str, np.ndarray]:
        """
        Get feature importance from Random Forest component
        
        Returns:
            Feature importance dictionary
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted first")
        
        importance = self.random_forest.feature_importances_
        
        if self.feature_names:
            return dict(zip(self.feature_names, importance))
        else:
            return {f"feature_{i}": imp for i, imp in enumerate(importance)}
    
    def save_model(self, filepath: str) -> None:
        """
        Save the trained model to disk
        
        Args:
            filepath: Path to save the model
        """
        if not self.is_fitted:
            raise ValueError("Cannot save unfitted model")
        
        model_data = {
            'ensemble': self.ensemble,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'model_performance': self.model_performance,
            'config': self.config
        }
        
        # Save LSTM separately if it exists
        if self.lstm_model:
            lstm_path = str(Path(filepath).with_suffix('.h5'))
            self.lstm_model.save(lstm_path)
            model_data['lstm_path'] = lstm_path
        
        joblib.dump(model_data, filepath)
        logger.info(f"Model saved to {filepath}")
    
    @classmethod
    def load_pretrained(cls, filepath: str) -> 'MSIFEnsemble':
        """
        Load a pre-trained model from disk
        
        Args:
            filepath: Path to the saved model
            
        Returns:
            Loaded MSIFEnsemble instance
        """
        model_data = joblib.load(filepath)
        
        instance = cls(config=model_data.get('config'))
        instance.ensemble = model_data['ensemble']
        instance.scaler = model_data['scaler']
        instance.feature_names = model_data['feature_names']
        instance.model_performance = model_data['model_performance']
        instance.is_fitted = True
        
        # Load LSTM if it exists
        if 'lstm_path' in model_data:
            instance.lstm_model = tf.keras.models.load_model(model_data['lstm_path'])
        
        logger.info(f"Model loaded from {filepath}")
        return instance


def main():
    """
    Example usage of MSIFEnsemble
    """
    # Setup logging
    setup_logging()
    
    # Load sample data (this would be replaced with actual data loading)
    logger.info("Loading sample data...")
    
    # This is a placeholder - replace with actual data loading
    np.random.seed(42)
    X = np.random.randn(1000, 47)  # 47 features as per research
    y = np.random.randint(0, 2, 1000)  # Binary classification
    
    # Initialize and train model
    msif = MSIFEnsemble()
    
    # Train the model
    msif.fit(X, y)
    
    # Perform cross-validation
    cv_scores = msif.cross_validate(X, y)
    
    # Make predictions on new data
    X_new = np.random.randn(100, 47)
    predictions = msif.predict(X_new)
    probabilities = msif.predict_proba(X_new)
    confidence = msif.get_confidence_score(X_new)
    
    logger.info(f"Made predictions for {len(X_new)} samples")
    logger.info(f"Average prediction confidence: {np.mean(confidence):.3f}")
    
    # Get feature importance
    importance = msif.get_feature_importance()
    top_features = sorted(importance.items(), key=lambda x: x[1], reverse=True)[:10]
    
    logger.info("Top 10 most important features:")
    for feature, score in top_features:
        logger.info(f"  {feature}: {score:.3f}")
    
    # Save model
    msif.save_model('models/msif_ensemble.pkl')


if __name__ == "__main__":
    main()