#!/usr/bin/env python3
"""
Data Cleaning Module for MSIF Framework

This module handles data preprocessing, cleaning, and validation for the
Multi-Source Intelligence Framework, ensuring data quality and consistency
across all intelligence sources.

Author: Jude Osamor
Institution: University of the West of England, Bristol
License: MIT
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple, Optional, Union
from pathlib import Path
import json
import re
from datetime import datetime, timedelta

from ..utils.config import load_config
from ..utils.logging_setup import setup_logging

logger = logging.getLogger(__name__)


class DataCleaner:
    """
    Data cleaning and preprocessing for MSIF framework
    
    This class handles the cleaning and preprocessing of data from multiple
    sources including honeypots, network traffic, malware samples, and 
    victim interviews.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize DataCleaner with configuration"""
        self.config = config or load_config()
        self.cleaning_stats = {}
        
    def clean_honeypot_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Clean honeypot log data
        
        Args:
            data: Raw honeypot data
            
        Returns:
            Cleaned honeypot data
        """
        logger.info("Cleaning honeypot data...")
        initial_rows = len(data)
        
        # Remove duplicates based on timestamp, source IP, and event type
        data = data.drop_duplicates(subset=['timestamp', 'source_ip', 'event_type'])
        
        # Clean IP addresses
        data['source_ip'] = data['source_ip'].apply(self._clean_ip_address)
        
        # Standardize timestamps
        data['timestamp'] = pd.to_datetime(data['timestamp'], errors='coerce')
        
        # Remove rows with invalid timestamps
        data = data.dropna(subset=['timestamp'])
        
        # Clean and validate port numbers
        data['dest_port'] = data['dest_port'].apply(self._clean_port)
        
        # Categorize attack types
        data['attack_category'] = data['event_type'].apply(self._categorize_attack)
        
        # Remove test traffic and internal IPs
        data = data[~data['source_ip'].str.startswith(('192.168.', '10.', '172.'))]
        
        final_rows = len(data)
        removed_rows = initial_rows - final_rows
        
        self.cleaning_stats['honeypot'] = {
            'initial_rows': initial_rows,
            'final_rows': final_rows,
            'removed_rows': removed_rows,
            'removal_rate': removed_rows / initial_rows if initial_rows > 0 else 0
        }
        
        logger.info(f"Honeypot data cleaned: {removed_rows} rows removed ({removed_rows/initial_rows*100:.1f}%)")
        return data
    
    def clean_network_traffic_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Clean network traffic analysis data
        
        Args:
            data: Raw network traffic data
            
        Returns:
            Cleaned network traffic data
        """
        logger.info("Cleaning network traffic data...")
        initial_rows = len(data)
        
        # Remove incomplete flows
        required_columns = ['src_ip', 'dst_ip', 'src_port', 'dst_port', 'protocol']
        data = data.dropna(subset=required_columns)
        
        # Clean IP addresses
        data['src_ip'] = data['src_ip'].apply(self._clean_ip_address)
        data['dst_ip'] = data['dst_ip'].apply(self._clean_ip_address)
        
        # Validate port ranges
        data['src_port'] = data['src_port'].apply(self._clean_port)
        data['dst_port'] = data['dst_port'].apply(self._clean_port)
        
        # Remove invalid protocols
        valid_protocols = ['TCP', 'UDP', 'ICMP', 'HTTP', 'HTTPS', 'SSH', 'FTP']
        data = data[data['protocol'].isin(valid_protocols)]
        
        # Clean packet and byte counts
        data['packets'] = pd.to_numeric(data['packets'], errors='coerce')
        data['bytes'] = pd.to_numeric(data['bytes'], errors='coerce')
        data = data.dropna(subset=['packets', 'bytes'])
        
        # Remove zero-packet flows
        data = data[data['packets'] > 0]
        
        final_rows = len(data)
        removed_rows = initial_rows - final_rows
        
        self.cleaning_stats['network_traffic'] = {
            'initial_rows': initial_rows,
            'final_rows': final_rows,
            'removed_rows': removed_rows,
            'removal_rate': removed_rows / initial_rows if initial_rows > 0 else 0
        }
        
        logger.info(f"Network traffic data cleaned: {removed_rows} rows removed ({removed_rows/initial_rows*100:.1f}%)")
        return data
    
    def clean_malware_analysis_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Clean malware analysis results
        
        Args:
            data: Raw malware analysis data
            
        Returns:
            Cleaned malware analysis data
        """
        logger.info("Cleaning malware analysis data...")
        initial_rows = len(data)
        
        # Validate MD5/SHA256 hashes
        data = data[data['md5_hash'].str.match(r'^[a-fA-F0-9]{32}, na=False)]
        data = data[data['sha256_hash'].str.match(r'^[a-fA-F0-9]{64}, na=False)]
        
        # Clean file sizes (convert to bytes)
        data['file_size'] = data['file_size'].apply(self._clean_file_size)
        
        # Standardize malware family names
        data['malware_family'] = data['malware_family'].apply(self._standardize_malware_family)
        
        # Clean detection timestamps
        data['first_seen'] = pd.to_datetime(data['first_seen'], errors='coerce')
        data = data.dropna(subset=['first_seen'])
        
        # Remove duplicate samples (same hash)
        data = data.drop_duplicates(subset=['sha256_hash'])
        
        final_rows = len(data)
        removed_rows = initial_rows - final_rows
        
        self.cleaning_stats['malware_analysis'] = {
            'initial_rows': initial_rows,
            'final_rows': final_rows,
            'removed_rows': removed_rows,
            'removal_rate': removed_rows / initial_rows if initial_rows > 0 else 0
        }
        
        logger.info(f"Malware analysis data cleaned: {removed_rows} rows removed ({removed_rows/initial_rows*100:.1f}%)")
        return data
    
    def clean_victim_interview_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and anonymize victim interview data
        
        Args:
            data: Raw victim interview data
            
        Returns:
            Cleaned and anonymized interview data
        """
        logger.info("Cleaning victim interview data...")
        initial_rows = len(data)
        
        # Remove any remaining PII
        data = self._remove_pii(data)
        
        # Standardize industry sectors
        data['industry_sector'] = data['industry_sector'].apply(self._standardize_industry)
        
        # Clean organization sizes
        data['organization_size'] = data['organization_size'].apply(self._standardize_org_size)
        
        # Validate incident dates
        data['incident_date'] = pd.to_datetime(data['incident_date'], errors='coerce')
        data = data.dropna(subset=['incident_date'])
        
        # Remove incidents outside study period (2022-2023)
        study_start = pd.to_datetime('2022-01-01')
        study_end = pd.to_datetime('2023-12-31')
        data = data[(data['incident_date'] >= study_start) & (data['incident_date'] <= study_end)]
        
        # Clean financial impact data
        data['direct_cost'] = pd.to_numeric(data['direct_cost'], errors='coerce')
        data['indirect_cost'] = pd.to_numeric(data['indirect_cost'], errors='coerce')
        
        final_rows = len(data)
        removed_rows = initial_rows - final_rows
        
        self.cleaning_stats['victim_interviews'] = {
            'initial_rows': initial_rows,
            'final_rows': final_rows,
            'removed_rows': removed_rows,
            'removal_rate': removed_rows / initial_rows if initial_rows > 0 else 0
        }
        
        logger.info(f"Victim interview data cleaned: {removed_rows} rows removed ({removed_rows/initial_rows*100:.1f}%)")
        return data
    
    def _clean_ip_address(self, ip: str) -> Optional[str]:
        """Clean and validate IP address"""
        if pd.isna(ip):
            return None
        
        # Remove any whitespace
        ip = str(ip).strip()
        
        # Validate IPv4 format
        pattern = r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})
        match = re.match(pattern, ip)
        
        if match:
            octets = [int(x) for x in match.groups()]
            if all(0 <= octet <= 255 for octet in octets):
                return ip
        
        return None
    
    def _clean_port(self, port: Union[str, int, float]) -> Optional[int]:
        """Clean and validate port number"""
        if pd.isna(port):
            return None
        
        try:
            port_int = int(port)
            if 1 <= port_int <= 65535:
                return port_int
        except (ValueError, TypeError):
            pass
        
        return None
    
    def _categorize_attack(self, event_type: str) -> str:
        """Categorize attack types"""
        if pd.isna(event_type):
            return 'unknown'
        
        event_type = str(event_type).lower()
        
        if 'brute' in event_type or 'password' in event_type:
            return 'brute_force'
        elif 'malware' in event_type or 'ransomware' in event_type:
            return 'malware'
        elif 'scan' in event_type or 'probe' in event_type:
            return 'reconnaissance'
        elif 'exploit' in event_type:
            return 'exploitation'
        else:
            return 'other'
    
    def _clean_file_size(self, size: Union[str, int, float]) -> Optional[int]:
        """Clean and normalize file size to bytes"""
        if pd.isna(size):
            return None
        
        if isinstance(size, (int, float)):
            return int(size)
        
        size_str = str(size).strip().upper()
        
        # Extract number and unit
        match = re.match(r'(\d+\.?\d*)\s*([KMGT]?B?)', size_str)
        if match:
            number = float(match.group(1))
            unit = match.group(2)
            
            multipliers = {
                'B': 1, '': 1,
                'KB': 1024, 'K': 1024,
                'MB': 1024**2, 'M': 1024**2,
                'GB': 1024**3, 'G': 1024**3,
                'TB': 1024**4, 'T': 1024**4
            }
            
            return int(number * multipliers.get(unit, 1))
        
        return None
    
    def _standardize_malware_family(self, family: str) -> str:
        """Standardize malware family names"""
        if pd.isna(family):
            return 'unknown'
        
        family = str(family).lower().strip()
        
        # Map common variations to standard names
        family_mapping = {
            'black basta': 'black_basta',
            'blackbasta': 'black_basta',
            'basta': 'black_basta',
            'lock bit': 'lockbit',
            'lockbit2.0': 'lockbit',
            'lockbit3.0': 'lockbit',
            'conti': 'conti',
            'ryuk': 'ryuk',
            'maze': 'maze',
            'egregor': 'egregor'
        }
        
        return family_mapping.get(family, family)
    
    def _standardize_industry(self, industry: str) -> str:
        """Standardize industry sector names"""
        if pd.isna(industry):
            return 'unknown'
        
        industry = str(industry).lower().strip()
        
        industry_mapping = {
            'manufacturing': 'manufacturing',
            'healthcare': 'healthcare',
            'financial services': 'financial_services',
            'finance': 'financial_services',
            'education': 'education',
            'government': 'government',
            'retail': 'retail',
            'technology': 'technology',
            'energy': 'energy',
            'utilities': 'utilities'
        }
        
        for key, value in industry_mapping.items():
            if key in industry:
                return value
        
        return 'other'
    
    def _standardize_org_size(self, size: str) -> str:
        """Standardize organization size categories"""
        if pd.isna(size):
            return 'unknown'
        
        size_str = str(size).lower().strip()
        
        # Extract number if present
        numbers = re.findall(r'\d+', size_str)
        if numbers:
            num_employees = int(numbers[0])
            if num_employees < 50:
                return 'small'
            elif num_employees < 500:
                return 'medium'
            elif num_employees < 5000:
                return 'large'
            else:
                return 'enterprise'
        
        # Use keywords if no numbers
        if 'small' in size_str or 'startup' in size_str:
            return 'small'
        elif 'medium' in size_str or 'mid' in size_str:
            return 'medium'
        elif 'large' in size_str or 'big' in size_str:
            return 'large'
        elif 'enterprise' in size_str or 'corporation' in size_str:
            return 'enterprise'
        
        return 'unknown'
    
    def _remove_pii(self, data: pd.DataFrame) -> pd.DataFrame:
        """Remove any remaining personally identifiable information"""
        # List of columns that might contain PII
        pii_columns = ['company_name', 'contact_person', 'email', 'phone', 'address']
        
        for col in pii_columns:
            if col in data.columns:
                data = data.drop(columns=[col])
        
        # Remove any data that looks like PII in text fields
        text_columns = data.select_dtypes(include=['object']).columns
        
        for col in text_columns:
            if col in data.columns:
                # Remove email patterns
                data[col] = data[col].astype(str).str.replace(
                    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 
                    '[EMAIL]', regex=True
                )
                
                # Remove phone patterns
                data[col] = data[col].str.replace(
                    r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', 
                    '[PHONE]', regex=True
                )
        
        return data
    
    def get_cleaning_report(self) -> Dict:
        """Generate a comprehensive cleaning report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'data_sources': list(self.cleaning_stats.keys()),
            'total_initial_rows': sum(stats['initial_rows'] for stats in self.cleaning_stats.values()),
            'total_final_rows': sum(stats['final_rows'] for stats in self.cleaning_stats.values()),
            'total_removed_rows': sum(stats['removed_rows'] for stats in self.cleaning_stats.values()),
            'source_details': self.cleaning_stats
        }
        
        report['overall_removal_rate'] = (
            report['total_removed_rows'] / report['total_initial_rows'] 
            if report['total_initial_rows'] > 0 else 0
        )
        
        return report
    
    def save_cleaning_report(self, filepath: str) -> None:
        """Save cleaning report to file"""
        report = self.get_cleaning_report()
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Cleaning report saved to {filepath}")


def main():
    """Example usage of DataCleaner"""
    setup_logging()
    
    # Initialize cleaner
    cleaner = DataCleaner()
    
    # Example data cleaning (replace with actual file loading)
    logger.info("Starting data cleaning process...")
    
    # This would be replaced with actual data loading from files
    sample_honeypot_data = pd.DataFrame({
        'timestamp': ['2023-01-01 10:00:00', '2023-01-01 11:00:00'],
        'source_ip': ['192.168.1.100', '203.0.113.1'],
        'dest_port': [22, 3389],
        'event_type': ['ssh_brute_force', 'rdp_attempt']
    })
    
    cleaned_data = cleaner.clean_honeypot_data(sample_honeypot_data)
    logger.info(f"Cleaned honeypot data: {len(cleaned_data)} rows")
    
    # Generate and save report
    report = cleaner.get_cleaning_report()
    logger.info("Data cleaning completed")
    logger.info(f"Overall removal rate: {report['overall_removal_rate']:.2%}")


if __name__ == "__main__":
    main()