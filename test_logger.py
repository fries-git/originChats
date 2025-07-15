#!/usr/bin/env python3
"""
Test script to verify logger implementation
"""

import sys
import os

# Add the originChats directory to the path so we can import the logger
sys.path.append('/Users/admin/Documents/rotur/originChats')

from logger import Logger

def test_logger():
    """Test all logger functions"""
    print("Testing Logger Implementation...")
    print("=" * 50)
    
    Logger.info("Logger test started")
    Logger.add("Testing add/creation action")
    Logger.edit("Testing edit/modification action") 
    Logger.delete("Testing deletion action")
    Logger.get("Testing retrieval/query action")
    Logger.warning("Testing warning message")
    Logger.error("Testing error message")
    Logger.success("Testing success message")
    Logger.discord_message("TestUser", "This is a test Discord message")
    
    print("=" * 50)
    Logger.success("All logger functions tested successfully!")

if __name__ == "__main__":
    test_logger()
