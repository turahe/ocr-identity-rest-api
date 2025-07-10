#!/usr/bin/env python3
"""
Test script for the new upload functionality
"""
import requests
import time
import json
from pathlib import Path


def test_upload_async():
    """Test async upload functionality"""
    print("🧪 Testing async upload...")
    
    # Create a test image (or use existing one)
    test_image_path = Path("test_image.jpg")
    if not test_image_path.exists():
        print("❌ Test image not found. Please create a test_image.jpg file.")
        return False
    
    # Upload file
    url = "http://localhost:8000/upload-image/"
    files = {"file": open(test_image_path, "rb")}
    
    try:
        response = requests.post(url, files=files)
        response.raise_for_status()
        
        result = response.json()
        print(f"✅ Upload initiated: {result}")
        
        # Get task ID
        task_id = result.get("task_id")
        if task_id:
            print(f"📋 Task ID: {task_id}")
            
            # Monitor task status
            for i in range(10):  # Check for 10 seconds
                time.sleep(1)
                task_response = requests.get(f"http://localhost:8000/task/{task_id}")
                if task_response.status_code == 200:
                    task_result = task_response.json()
                    print(f"📊 Task status: {task_result['state']}")
                    
                    if task_result['state'] == 'SUCCESS':
                        print(f"🎉 Task completed: {task_result['result']}")
                        return True
                    elif task_result['state'] == 'FAILURE':
                        print(f"❌ Task failed: {task_result}")
                        return False
                else:
                    print(f"⚠️  Could not check task status: {task_response.status_code}")
            
            print("⏰ Task monitoring timeout")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Upload failed: {e}")
        return False


def test_upload_sync():
    """Test sync upload functionality"""
    print("\n🧪 Testing sync upload...")
    
    test_image_path = Path("test_image.jpg")
    if not test_image_path.exists():
        print("❌ Test image not found. Please create a test_image.jpg file.")
        return False
    
    url = "http://localhost:8000/upload-image-sync/"
    files = {"file": open(test_image_path, "rb")}
    
    try:
        response = requests.post(url, files=files)
        response.raise_for_status()
        
        result = response.json()
        print(f"✅ Sync upload completed: {result}")
        
        # Get media ID
        media_id = result.get("media_id")
        if media_id:
            print(f"📋 Media ID: {media_id}")
            
            # Get media info
            media_response = requests.get(f"http://localhost:8000/media/{media_id}")
            if media_response.status_code == 200:
                media_info = media_response.json()
                print(f"📄 Media info: {media_info}")
            
            # Get OCR results
            ocr_response = requests.get(f"http://localhost:8000/media/{media_id}/ocr")
            if ocr_response.status_code == 200:
                ocr_info = ocr_response.json()
                print(f"🔍 OCR results: {ocr_info}")
            
            return True
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Sync upload failed: {e}")
        return False


def test_health_check():
    """Test health check endpoint"""
    print("\n🧪 Testing health check...")
    
    try:
        response = requests.get("http://localhost:8000/health")
        response.raise_for_status()
        
        result = response.json()
        print(f"✅ Health check: {result}")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check failed: {e}")
        return False


def main():
    """Main test function"""
    print("🚀 Testing OCR Identity REST API v2.0.0")
    print("=" * 50)
    
    # Test health check
    if not test_health_check():
        print("❌ Health check failed. Is the server running?")
        return
    
    # Test async upload
    async_success = test_upload_async()
    
    # Test sync upload
    sync_success = test_upload_sync()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"✅ Health Check: {'PASS' if True else 'FAIL'}")
    print(f"✅ Async Upload: {'PASS' if async_success else 'FAIL'}")
    print(f"✅ Sync Upload: {'PASS' if sync_success else 'FAIL'}")
    
    if async_success and sync_success:
        print("\n🎉 All tests passed! The new architecture is working correctly.")
    else:
        print("\n❌ Some tests failed. Check the logs above for details.")


if __name__ == "__main__":
    main() 