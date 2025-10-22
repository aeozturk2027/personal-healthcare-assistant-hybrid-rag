"""
MCP Tools - Tarih/zaman ve utility fonksiyonları
"""
from datetime import datetime, timedelta, date
from typing import Optional
from dateutil import parser
import re

class DateTools:
    """Tarih/zaman ve utility tools"""
    
    @staticmethod
    def get_current_date() -> str:
        """Bugünün tarihini döndür (YYYY-MM-DD)"""
        return date.today().isoformat()
    
    @staticmethod
    def get_current_time() -> str:
        """Şu anki zamanı döndür (HH:MM)"""
        return datetime.now().strftime("%H:%M")
    
    
    @staticmethod
    def parse_relative_date(text: str) -> Optional[str]:
        """
        Relative tarih ifadelerini parse et
        Örnek: "tomorrow", "next week", "in 3 days"
        """
        text_lower = text.lower()
        today = date.today()
        
        # Today
        if "today" in text_lower:
            return today.isoformat()
        
        # Tomorrow
        if "tomorrow" in text_lower:
            return (today + timedelta(days=1)).isoformat()
        
        # Yesterday
        if "yesterday" in text_lower:
            return (today - timedelta(days=1)).isoformat()
        
        # This week
        if "this week" in text_lower:
            return today.isoformat()
        
        # Next week
        if "next week" in text_lower:
            return (today + timedelta(weeks=1)).isoformat()
        
        # In N days
        match = re.search(r'in (\d+) days?', text_lower)
        if match:
            days = int(match.group(1))
            return (today + timedelta(days=days)).isoformat()
        
        # In N weeks
        match = re.search(r'in (\d+) weeks?', text_lower)
        if match:
            weeks = int(match.group(1))
            return (today + timedelta(weeks=weeks)).isoformat()
        
        return None
    
    
    @staticmethod
    def format_date_friendly(date_str: str) -> str:
        """Tarihi user-friendly formatta göster"""
        try:
            date_obj = parser.parse(date_str).date()
            today = date.today()
            
            if date_obj == today:
                return "Today"
            elif date_obj == today + timedelta(days=1):
                return "Tomorrow"
            elif date_obj == today - timedelta(days=1):
                return "Yesterday"
            else:
                # Format: "Monday, Jan 15"
                return date_obj.strftime("%A, %b %d")
        except:
            return date_str
    
    @staticmethod
    def is_date_in_range(date_str: str, days_ahead: int = 7) -> bool:
        """Tarih önümüzdeki N gün içinde mi?"""
        try:
            date_obj = parser.parse(date_str).date()
            today = date.today()
            future = today + timedelta(days=days_ahead)
            return today <= date_obj <= future
        except:
            return False

