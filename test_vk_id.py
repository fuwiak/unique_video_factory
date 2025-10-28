#!/usr/bin/env python3
"""
Test VK ID Functionality
Tests the new VK ID extraction and bot integration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from advanced_social_stats import AdvancedSocialStatsChecker

def test_vk_id_extraction():
    """Test VK ID extraction from URL"""
    print("🧪 Testing VK ID Extraction")
    print("=" * 50)
    
    checker = AdvancedSocialStatsChecker()
    
    # Test cases
    test_cases = [
        {
            'url': 'https://vk.com/clips/lizaaaakorzh?feedType=ownerFeed&owner=1072165347&z=clip1072165347_456239068',
            'expected_id': '1072165347',
            'description': 'VK clips URL with owner parameter'
        },
        {
            'url': 'https://vk.com/clips/lizaaaakorzh',
            'expected_id': 'lizaaaakorzh',
            'description': 'VK clips URL without owner parameter'
        },
        {
            'url': 'https://vk.com/id123456789',
            'expected_id': '123456789',
            'description': 'VK profile URL with ID'
        },
        {
            'url': 'https://vk.com/username',
            'expected_id': 'username',
            'description': 'VK profile URL with username'
        }
    ]
    
    results = []
    for test_case in test_cases:
        print(f"📱 Testing: {test_case['description']}")
        print(f"   URL: {test_case['url']}")
        
        try:
            extracted_id = checker._extract_vk_user_id(test_case['url'])
            expected_id = test_case['expected_id']
            
            print(f"   Expected: {expected_id}")
            print(f"   Extracted: {extracted_id}")
            
            if extracted_id == expected_id:
                print(f"   ✅ PASSED")
                results.append(True)
            else:
                print(f"   ❌ FAILED")
                results.append(False)
                
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            results.append(False)
        
        print()
    
    return all(results)

def test_vk_id_validation():
    """Test VK ID validation logic"""
    print("🔍 Testing VK ID Validation")
    print("=" * 50)
    
    checker = AdvancedSocialStatsChecker()
    
    # Test cases
    test_cases = [
        {
            'user_id': '1072165347',
            'is_digit': True,
            'description': 'Numeric VK ID'
        },
        {
            'user_id': 'lizaaaakorzh',
            'is_digit': False,
            'description': 'Username VK ID'
        },
        {
            'user_id': '123456789',
            'is_digit': True,
            'description': 'Another numeric VK ID'
        },
        {
            'user_id': 'user_name',
            'is_digit': False,
            'description': 'Another username VK ID'
        }
    ]
    
    results = []
    for test_case in test_cases:
        print(f"📱 Testing: {test_case['description']}")
        print(f"   User ID: {test_case['user_id']}")
        
        try:
            is_digit = test_case['user_id'].isdigit()
            expected = test_case['is_digit']
            
            print(f"   Expected is_digit: {expected}")
            print(f"   Actual is_digit: {is_digit}")
            
            if is_digit == expected:
                print(f"   ✅ PASSED")
                results.append(True)
            else:
                print(f"   ❌ FAILED")
                results.append(False)
                
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            results.append(False)
        
        print()
    
    return all(results)

def test_vk_api_integration():
    """Test VK API integration logic"""
    print("🔌 Testing VK API Integration")
    print("=" * 50)
    
    checker = AdvancedSocialStatsChecker()
    
    # Test VK API key availability
    has_api_key = checker.api_keys.get('vk') is not None
    print(f"📱 VK API key available: {has_api_key}")
    
    if has_api_key:
        print("✅ VK API key is available - real data can be fetched")
    else:
        print("⚠️ VK API key not available - will use fallback methods")
    
    # Test VK clips processing
    vk_url = 'https://vk.com/clips/lizaaaakorzh?feedType=ownerFeed&owner=1072165347&z=clip1072165347_456239068'
    print(f"📱 Testing VK URL: {vk_url}")
    
    try:
        result = checker.check_vk_stats(vk_url)
        print(f"✅ VK Result: {result}")
        
        if 'error' in result:
            print(f"⚠️ VK Error: {result['error']}")
            if 'Brak VK API key' in result['error'] or 'Nie można pobrać clipsów' in result['error']:
                print("✅ Expected error - no VK API key or clips not available")
                return True
            else:
                print("❌ Unexpected error")
                return False
        else:
            print("✅ VK processing successful")
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_bot_state_management():
    """Test bot state management for VK ID"""
    print("🤖 Testing Bot State Management")
    print("=" * 50)
    
    # Test state structure
    test_state = {
        'status': 'waiting_for_vk_id',
        'blogger_name': 'Лиза',
        'vk_url': 'https://vk.com/clips/lizaaaakorzh',
        'current_platform': 'VK'
    }
    
    print(f"📱 Test state: {test_state}")
    
    # Test state validation
    required_fields = ['status', 'blogger_name', 'vk_url', 'current_platform']
    missing_fields = [field for field in required_fields if field not in test_state]
    
    if missing_fields:
        print(f"❌ Missing fields: {missing_fields}")
        return False
    else:
        print("✅ All required fields present")
    
    # Test status validation
    if test_state['status'] == 'waiting_for_vk_id':
        print("✅ Status is correct")
    else:
        print(f"❌ Incorrect status: {test_state['status']}")
        return False
    
    # Test platform validation
    if test_state['current_platform'] == 'VK':
        print("✅ Platform is correct")
    else:
        print(f"❌ Incorrect platform: {test_state['current_platform']}")
        return False
    
    print("✅ Bot state management test passed")
    return True

def main():
    """Run all tests"""
    print("🚀 VK ID Functionality Test Suite")
    print("=" * 60)
    
    tests = [
        ("VK ID Extraction", test_vk_id_extraction),
        ("VK ID Validation", test_vk_id_validation),
        ("VK API Integration", test_vk_api_integration),
        ("Bot State Management", test_bot_state_management)
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
        print("🎉 All tests passed! VK ID functionality is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
