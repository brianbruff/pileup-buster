"""In-memory database for testing purposes"""
import os
from datetime import datetime
from typing import List, Dict, Any, Optional


class InMemoryQueueDatabase:
    """In-memory database operations for queue management (testing only)"""
    
    def __init__(self):
        self.queue_data: List[Dict[str, Any]] = []
    
    def register_callsign(self, callsign: str) -> Dict[str, Any]:
        """Register a callsign in the queue"""
        # Check if callsign already exists
        existing = next((entry for entry in self.queue_data if entry["callsign"] == callsign), None)
        if existing:
            raise ValueError("Callsign already in queue")
        
        # Get current queue count and check against limit
        current_count = len(self.queue_data)
        max_queue_size = int(os.getenv('MAX_QUEUE_SIZE', '50'))
        
        if current_count >= max_queue_size:
            raise ValueError(f"Queue is full. Maximum queue size is {max_queue_size}")
        
        # Get current position (count + 1)
        position = current_count + 1
        
        # Create entry
        entry = {
            'callsign': callsign,
            'timestamp': datetime.utcnow().isoformat(),
            'position': position
        }
        
        # Add to in-memory storage
        self.queue_data.append(entry)
        
        return entry.copy()
    
    def find_callsign(self, callsign: str) -> Optional[Dict[str, Any]]:
        """Find a callsign in the queue and return with updated position"""
        # Find the entry
        entry = next((entry for entry in self.queue_data if entry["callsign"] == callsign), None)
        if not entry:
            return None
        
        # Calculate current position based on timestamp order
        sorted_queue = sorted(self.queue_data, key=lambda x: x["timestamp"])
        position = next((i+1 for i, e in enumerate(sorted_queue) if e["callsign"] == callsign), 0)
        
        # Return copy with updated position
        result = entry.copy()
        result['position'] = position
        return result
    
    def get_queue_list(self) -> List[Dict[str, Any]]:
        """Get the complete queue list with updated positions"""
        # Sort by timestamp (FIFO order) and update positions
        sorted_queue = sorted(self.queue_data, key=lambda x: x["timestamp"])
        
        queue_list = []
        for i, entry in enumerate(sorted_queue):
            entry_copy = entry.copy()
            entry_copy['position'] = i + 1
            queue_list.append(entry_copy)
        
        return queue_list
    
    def remove_callsign(self, callsign: str) -> Optional[Dict[str, Any]]:
        """Remove a callsign from the queue"""
        # Find and remove the entry
        entry = next((entry for entry in self.queue_data if entry["callsign"] == callsign), None)
        if entry:
            self.queue_data.remove(entry)
            return entry.copy()
        
        return None
    
    def clear_queue(self) -> int:
        """Clear the entire queue and return count of removed entries"""
        count = len(self.queue_data)
        self.queue_data.clear()
        return count
    
    def get_next_callsign(self) -> Optional[Dict[str, Any]]:
        """Get and remove the next callsign in queue (FIFO)"""
        if not self.queue_data:
            return None
        
        # Find the oldest entry (by timestamp)
        oldest_entry = min(self.queue_data, key=lambda x: x["timestamp"])
        self.queue_data.remove(oldest_entry)
        
        return oldest_entry.copy()
    
    def get_queue_count(self) -> int:
        """Get the total count of entries in queue"""
        return len(self.queue_data)


# Global in-memory database instance for testing
test_queue_db = InMemoryQueueDatabase()