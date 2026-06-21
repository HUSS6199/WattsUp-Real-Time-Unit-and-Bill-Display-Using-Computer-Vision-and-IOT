"""Firebase Realtime Database operations."""

import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime
from typing import Optional, Dict
import os


class FirebaseDB:
    """Handles all Firebase database operations for WattsUp."""
    
    def __init__(self, firebase_url: str, creds_path: str = "serviceAccountKey.json"):
        """
        Initialize Firebase connection.
        
        Args:
            firebase_url: Firebase Realtime Database URL
            creds_path: Path to service account credentials JSON
        """
        self.firebase_url = firebase_url
        self.creds_path = creds_path
        self.initialized = False
        self.usage_ref = None
        self.history_ref = None
        
    def connect(self) -> bool:
        """
        Establish connection to Firebase.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not firebase_admin._apps:
                if not os.path.exists(self.creds_path):
                    print(f"❌ Credentials file not found: {self.creds_path}")
                    return False
                
                cred = credentials.Certificate(self.creds_path)
                firebase_admin.initialize_app(cred, {'databaseURL': self.firebase_url})
                print("✅ Firebase initialized successfully.")
            
            self.usage_ref = db.reference('current_usage')
            self.history_ref = db.reference('meter_readings')
            self.initialized = True
            return True
            
        except Exception as e:
            print(f"❌ Firebase initialization failed: {e}")
            return False
    
    def get_current_usage(self) -> Optional[Dict]:
        """
        Get current usage data from Firebase.
        
        Returns:
            Dictionary with current usage data, or None on error
        """
        try:
            return self.usage_ref.get() or {}
        except Exception as e:
            print(f"❌ Failed to read current usage: {e}")
            return None
    
    def update_current_usage(self, units: float, bill: float, is_alert: bool) -> bool:
        """
        Update current usage in Firebase.
        
        Args:
            units: Current meter reading in kWh
            bill: Calculated bill amount in PKR
            is_alert: Whether to trigger notification
        
        Returns:
            True if successful, False otherwise
        """
        try:
            now = datetime.now()
            self.usage_ref.update({
                'units': round(units, 2),
                'bill_pkr': round(bill + 400, 0),  # Add fixed charge
                'trigger_notification': is_alert,
                'last_sync': now.strftime('%H:%M:%S')
            })
            return True
        except Exception as e:
            print(f"❌ Failed to update current usage: {e}")
            return False
    
    def log_meter_reading(self, units: float, bill: float) -> bool:
        """
        Log meter reading to history.
        
        Args:
            units: Current meter reading in kWh
            bill: Calculated bill amount in PKR
        
        Returns:
            True if successful, False otherwise
        """
        try:
            now = datetime.now()
            timestamp_str = now.strftime('%Y-%m-%d %H:%M:%S')
            
            # Get previous reading to calculate consumption
            previous_data = self.usage_ref.get() or {}
            prev_units = previous_data.get('units', 0)
            
            if units > prev_units:
                consumption = units - prev_units
                self.history_ref.push({
                    'timestamp': timestamp_str,
                    'units': round(units, 2),
                    'consumption_delta': round(consumption, 2),
                    'bill_pkr': round(bill + 400, 0)
                })
                print(f"📈 Logged meter reading: +{round(consumption, 2)} kWh")
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Failed to log meter reading: {e}")
            return False
    
    def sync_reading(self, units: float, bill: float, is_alert: bool = False) -> bool:
        """
        Perform full sync: update current usage and log to history.
        
        Args:
            units: Current meter reading in kWh
            bill: Calculated bill amount in PKR
            is_alert: Whether to trigger notification
        
        Returns:
            True if both operations successful
        """
        if not self.initialized:
            print("❌ Firebase not initialized")
            return False
        
        success = True
        success &= self.update_current_usage(units, bill, is_alert)
        success &= self.log_meter_reading(units, bill)
        
        if success:
            print(f"✅ Firebase sync complete: {units} kWh, Bill: Rs. {bill+400:.0f}")
        
        return success
