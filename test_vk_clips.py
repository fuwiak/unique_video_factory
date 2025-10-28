#!/usr/bin/env python3
"""
Test VK Clips Functionality
Tests the new VK clips feature that fetches last 5 clips instead of profile data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from advanced_social_stats import AdvancedSocialStatsChecker
from google_sheets_integration import GoogleSheetsIntegration

def test_vk_clips():
    """Test VK clips functionality"""
    print("🧪 Testing VK Clips Functionality")
    print("=" * 50)
    
    checker = AdvancedSocialStatsChecker()
    
    # Test VK clips URL
    vk_url = 'https://vk.com/clips/lizaaaakorzh?feedType=ownerFeed&owner=1072165347&z=clip1072165347_456239069'
    print(f"📱 Testing VK URL: {vk_url}")
    
    try:
        result = checker.check_vk_stats(vk_url)
        print(f"✅ VK Result: {result}")
        
        if 'clips' in result:
            print(f"📊 Clips count: {len(result['clips'])}")
            for i, clip in enumerate(result['clips']):
                print(f"  📹 Clip {i+1}: {clip.get('title', 'No title')} - {clip.get('views', 0)} views")
        else:
            print("❌ No clips found in result")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

def test_google_sheets_integration():
    """Test Google Sheets integration with VK clips"""
    print("\n📊 Testing Google Sheets Integration")
    print("=" * 50)
    
    sheets = GoogleSheetsIntegration()
    checker = AdvancedSocialStatsChecker()
    
    # Test VK clips
    vk_url = 'https://vk.com/clips/lizaaaakorzh?feedType=ownerFeed&owner=1072165347&z=clip1072165347_456239069'
    print(f"📱 Testing VK URL: {vk_url}")
    
    try:
        result = checker.check_vk_stats(vk_url)
        print(f"✅ VK Result: {result}")
        
        if 'clips' in result:
            print(f"📊 Clips count: {len(result['clips'])}")
            
            # Test Google Sheets save
            blogger_name = 'Лиза'
            print(f"💾 Testing Google Sheets save for blogger: {blogger_name}")
            
            # Add blogger data
            result['blogger_name'] = blogger_name
            result['user_name'] = blogger_name
            result['url'] = vk_url
            
            success = sheets.save_to_blogger_sheet(blogger_name, {'VK': result})
            print(f"✅ Google Sheets save success: {success}")
            
            if success:
                print("🎉 VK clips successfully saved to Google Sheets!")
                return True
            else:
                print("❌ Failed to save to Google Sheets")
                return False
        else:
            print("❌ No clips found in result")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_structure():
    """Test VK clips data structure"""
    print("\n🔍 Testing VK Clips Data Structure")
    print("=" * 50)
    
    checker = AdvancedSocialStatsChecker()
    
    # Test VK clips
    vk_url = 'https://vk.com/clips/lizaaaakorzh?feedType=ownerFeed&owner=1072165347&z=clip1072165347_456239069'
    
    try:
        result = checker.check_vk_stats(vk_url)
        
        if 'clips' in result:
            print(f"📊 Found {len(result['clips'])} clips")
            
            # Check first clip structure
            first_clip = result['clips'][0]
            print(f"📹 First clip structure:")
            print(f"  - Title: {first_clip.get('title', 'N/A')}")
            print(f"  - Video ID: {first_clip.get('video_id', 'N/A')}")
            print(f"  - Views: {first_clip.get('views', 'N/A')}")
            print(f"  - Likes: {first_clip.get('likes', 'N/A')}")
            print(f"  - Comments: {first_clip.get('comments', 'N/A')}")
            print(f"  - Date: {first_clip.get('date', 'N/A')}")
            print(f"  - Duration: {first_clip.get('duration', 'N/A')}")
            print(f"  - URL: {first_clip.get('url', 'N/A')}")
            
            # Check required fields
            required_fields = ['title', 'video_id', 'views', 'likes', 'comments', 'date', 'duration', 'url']
            missing_fields = [field for field in required_fields if field not in first_clip]
            
            if missing_fields:
                print(f"❌ Missing fields: {missing_fields}")
                return False
            else:
                print("✅ All required fields present")
                return True
        else:
            print("❌ No clips found in result")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 VK Clips Functionality Test Suite")
    print("=" * 60)
    
    tests = [
        ("VK Clips Functionality", test_vk_clips),
        ("Google Sheets Integration", test_google_sheets_integration),
        ("Data Structure", test_data_structure)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! VK clips functionality is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
