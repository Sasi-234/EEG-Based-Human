"""
EEG Signal Preprocessing Module
Handles loading, filtering, artifact removal, and feature extraction from EEG signals
"""
import numpy as np
import pandas as pd
from scipy import signal
from scipy.signal import butter, filtfilt, iirnotch
import logging

logger = logging.getLogger(__name__)


class EEGPreprocessor:
    """
    Comprehensive EEG signal preprocessing class
    Supports DEAP dataset format with 32 channels
    """
    
    def __init__(self, sampling_rate=128):
        """
        Initialize the preprocessor
        
        Args:
            sampling_rate (int): Sampling rate in Hz (default: 128 for DEAP)
        """
        self.sampling_rate = sampling_rate
        self.channels = 32  # DEAP dataset has 32 EEG channels
        
    def load_eeg_data(self, file_path):
        """
        Load EEG data from various file formats
        
        Args:
            file_path (str): Path to the EEG data file
            
        Returns:
            np.ndarray: EEG data array (channels x samples)
        """
        try:
            file_extension = file_path.split('.')[-1].lower()
            
            if file_extension == 'csv':
                data = pd.read_csv(file_path, header=None).values
            elif file_extension == 'dat':
                data = np.loadtxt(file_path)
            elif file_extension in ['edf', 'bdf']:
                # For EDF/BDF files, we would use MNE library
                # This is a placeholder for the actual implementation
                try:
                    import mne
                    raw = mne.io.read_raw_edf(file_path, preload=True, verbose=False)
                    data = raw.get_data()
                except ImportError:
                    logger.error("MNE library not available for EDF/BDF files")
                    raise ValueError("MNE library required for EDF/BDF files")
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
            
            # Ensure data is in correct shape (channels x samples)
            if data.shape[0] > data.shape[1]:
                data = data.T
                
            logger.info(f"Loaded EEG data with shape: {data.shape}")
            return data
            
        except Exception as e:
            logger.error(f"Error loading EEG data: {str(e)}")
            raise
    
    def bandpass_filter(self, data, lowcut=4.0, highcut=45.0, order=5):
        """
        Apply bandpass filter to remove unwanted frequencies
        
        Args:
            data (np.ndarray): EEG data (channels x samples)
            lowcut (float): Low cutoff frequency in Hz
            highcut (float): High cutoff frequency in Hz
            order (int): Filter order
            
        Returns:
            np.ndarray: Filtered EEG data
        """
        try:
            nyquist = 0.5 * self.sampling_rate
            low = lowcut / nyquist
            high = highcut / nyquist
            
            b, a = butter(order, [low, high], btype='band')
            
            filtered_data = np.zeros_like(data)
            for i in range(data.shape[0]):
                filtered_data[i] = filtfilt(b, a, data[i])
            
            logger.info(f"Applied bandpass filter: {lowcut}-{highcut} Hz")
            return filtered_data
            
        except Exception as e:
            logger.error(f"Error in bandpass filtering: {str(e)}")
            raise
    
    def notch_filter(self, data, freq=50.0, quality_factor=30.0):
        """
        Apply notch filter to remove power line interference
        
        Args:
            data (np.ndarray): EEG data (channels x samples)
            freq (float): Frequency to remove (50 Hz or 60 Hz)
            quality_factor (float): Quality factor
            
        Returns:
            np.ndarray: Filtered EEG data
        """
        try:
            b, a = iirnotch(freq, quality_factor, self.sampling_rate)
            
            filtered_data = np.zeros_like(data)
            for i in range(data.shape[0]):
                filtered_data[i] = filtfilt(b, a, data[i])
            
            logger.info(f"Applied notch filter at {freq} Hz")
            return filtered_data
            
        except Exception as e:
            logger.error(f"Error in notch filtering: {str(e)}")
            raise
    
    def normalize_data(self, data, method='zscore'):
        """
        Normalize EEG data
        
        Args:
            data (np.ndarray): EEG data (channels x samples)
            method (str): Normalization method ('zscore', 'minmax', 'robust')
            
        Returns:
            np.ndarray: Normalized EEG data
        """
        try:
            normalized_data = np.zeros_like(data)
            
            for i in range(data.shape[0]):
                if method == 'zscore':
                    mean = np.mean(data[i])
                    std = np.std(data[i])
                    normalized_data[i] = (data[i] - mean) / (std + 1e-8)
                    
                elif method == 'minmax':
                    min_val = np.min(data[i])
                    max_val = np.max(data[i])
                    normalized_data[i] = (data[i] - min_val) / (max_val - min_val + 1e-8)
                    
                elif method == 'robust':
                    median = np.median(data[i])
                    q75, q25 = np.percentile(data[i], [75, 25])
                    iqr = q75 - q25
                    normalized_data[i] = (data[i] - median) / (iqr + 1e-8)
                    
                else:
                    raise ValueError(f"Unknown normalization method: {method}")
            
            logger.info(f"Applied {method} normalization")
            return normalized_data
            
        except Exception as e:
            logger.error(f"Error in normalization: {str(e)}")
            raise
    
    def remove_artifacts_simple(self, data, threshold=3.0):
        """
        Simple artifact removal using threshold-based detection
        
        Args:
            data (np.ndarray): EEG data (channels x samples)
            threshold (float): Z-score threshold for artifact detection
            
        Returns:
            np.ndarray: Cleaned EEG data
        """
        try:
            cleaned_data = data.copy()
            
            for i in range(data.shape[0]):
                mean = np.mean(data[i])
                std = np.std(data[i])
                z_scores = np.abs((data[i] - mean) / (std + 1e-8))
                
                # Replace artifacts with interpolated values
                artifact_indices = z_scores > threshold
                if np.any(artifact_indices):
                    cleaned_data[i][artifact_indices] = np.interp(
                        np.where(artifact_indices)[0],
                        np.where(~artifact_indices)[0],
                        data[i][~artifact_indices]
                    )
            
            logger.info("Applied simple artifact removal")
            return cleaned_data
            
        except Exception as e:
            logger.error(f"Error in artifact removal: {str(e)}")
            raise
    
    def segment_data(self, data, segment_length=None, overlap=0.5):
        """
        Segment EEG data into fixed-length windows
        
        Args:
            data (np.ndarray): EEG data (channels x samples)
            segment_length (int): Length of each segment in samples
            overlap (float): Overlap ratio between segments (0-1)
            
        Returns:
            np.ndarray: Segmented data (segments x channels x samples)
        """
        try:
            if segment_length is None:
                segment_length = self.sampling_rate * 2  # 2 seconds default
            
            step = int(segment_length * (1 - overlap))
            num_segments = (data.shape[1] - segment_length) // step + 1
            
            segments = []
            for i in range(num_segments):
                start = i * step
                end = start + segment_length
                if end <= data.shape[1]:
                    segments.append(data[:, start:end])
            
            segments = np.array(segments)
            logger.info(f"Created {len(segments)} segments")
            return segments
            
        except Exception as e:
            logger.error(f"Error in segmentation: {str(e)}")
            raise
    
    def extract_frequency_bands(self, data):
        """
        Extract power in different frequency bands
        
        Args:
            data (np.ndarray): EEG data (channels x samples)
            
        Returns:
            dict: Power in different frequency bands
        """
        try:
            # Define frequency bands
            bands = {
                'delta': (0.5, 4),
                'theta': (4, 8),
                'alpha': (8, 13),
                'beta': (13, 30),
                'gamma': (30, 45)
            }
            
            band_powers = {}
            
            for band_name, (low, high) in bands.items():
                band_data = self.bandpass_filter(data, low, high)
                # Calculate power as variance
                power = np.var(band_data, axis=1)
                band_powers[band_name] = power
            
            logger.info("Extracted frequency band powers")
            return band_powers
            
        except Exception as e:
            logger.error(f"Error in frequency band extraction: {str(e)}")
            raise
    
    def extract_statistical_features(self, data):
        """
        Extract statistical features from EEG data
        
        Args:
            data (np.ndarray): EEG data (channels x samples)
            
        Returns:
            dict: Statistical features
        """
        try:
            features = {
                'mean': np.mean(data, axis=1),
                'std': np.std(data, axis=1),
                'var': np.var(data, axis=1),
                'min': np.min(data, axis=1),
                'max': np.max(data, axis=1),
                'median': np.median(data, axis=1),
                'skewness': self._calculate_skewness(data),
                'kurtosis': self._calculate_kurtosis(data)
            }
            
            logger.info("Extracted statistical features")
            return features
            
        except Exception as e:
            logger.error(f"Error in statistical feature extraction: {str(e)}")
            raise
    
    def _calculate_skewness(self, data):
        """Calculate skewness for each channel"""
        from scipy.stats import skew
        return skew(data, axis=1)
    
    def _calculate_kurtosis(self, data):
        """Calculate kurtosis for each channel"""
        from scipy.stats import kurtosis
        return kurtosis(data, axis=1)
    
    def preprocess_pipeline(self, file_path, apply_notch=True, apply_artifact_removal=True):
        """
        Complete preprocessing pipeline
        
        Args:
            file_path (str): Path to EEG data file
            apply_notch (bool): Whether to apply notch filter
            apply_artifact_removal (bool): Whether to remove artifacts
            
        Returns:
            dict: Preprocessed data and features
        """
        try:
            # Load data
            data = self.load_eeg_data(file_path)
            
            # Apply bandpass filter
            data = self.bandpass_filter(data)
            
            # Apply notch filter if requested
            if apply_notch:
                data = self.notch_filter(data)
            
            # Remove artifacts if requested
            if apply_artifact_removal:
                data = self.remove_artifacts_simple(data)
            
            # Normalize data
            data = self.normalize_data(data, method='zscore')
            
            # Extract features
            band_powers = self.extract_frequency_bands(data)
            statistical_features = self.extract_statistical_features(data)
            
            # Segment data
            segments = self.segment_data(data)
            
            result = {
                'preprocessed_data': data,
                'segments': segments,
                'band_powers': band_powers,
                'statistical_features': statistical_features,
                'shape': data.shape,
                'num_segments': len(segments)
            }
            
            logger.info("Preprocessing pipeline completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error in preprocessing pipeline: {str(e)}")
            raise


def preprocess_eeg_file(file_path, sampling_rate=128):
    """
    Convenience function to preprocess an EEG file
    
    Args:
        file_path (str): Path to EEG data file
        sampling_rate (int): Sampling rate in Hz
        
    Returns:
        dict: Preprocessed data and features
    """
    preprocessor = EEGPreprocessor(sampling_rate=sampling_rate)
    return preprocessor.preprocess_pipeline(file_path)

# Made with Bob
