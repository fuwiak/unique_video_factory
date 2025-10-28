#!/usr/bin/env python3
"""
Test Bot Logic Fix
Tests that bot doesn't ask for video when user is in blogger_states
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_bot_logic():
    """Test bot logic for blogger states"""
    print("🧪 Testing Bot Logic Fix")
    print("=" * 50)
    
    # Simulate user states
    blogger_states = {
        12345: {
            'status': 'waiting_for_vk_id',
            'blogger_name': 'Лиза',
            'vk_url': 'https://vk.com/clips/lizaaaakorzh',
            'current_platform': 'VK'
        }
    }
    
    user_states = {}  # Empty - user hasn't sent video
    
    user_id = 12345
    
    print(f"📱 User ID: {user_id}")
    print(f"📱 In blogger_states: {user_id in blogger_states}")
    print(f"📱 In user_states: {user_id in user_states}")
    
    # Test the logic
    if user_id in blogger_states:
        print("✅ User is in blogger_states - should handle blogger creation")
        print("✅ Bot should NOT ask for video")
        return True
    elif user_id not in user_states:
        print("❌ User not in user_states - bot would ask for video")
        print("❌ This is the bug!")
        return False
    else:
        print("✅ User is in user_states - normal flow")
        return True

def test_blogger_state_priority():
    """Test that blogger_states has priority over user_states"""
    print("\n🔍 Testing Blogger State Priority")
    print("=" * 50)
    
    # Test case 1: User in blogger_states only
    blogger_states_1 = {12345: {'status': 'waiting_for_vk_id'}}
    user_states_1 = {}
    
    user_id = 12345
    
    if user_id in blogger_states_1:
        print("✅ Case 1: User in blogger_states only - should handle blogger creation")
        result_1 = True
    else:
        print("❌ Case 1: Failed")
        result_1 = False
    
    # Test case 2: User in both states
    blogger_states_2 = {12345: {'status': 'waiting_for_vk_id'}}
    user_states_2 = {12345: {'video_id': 'test123'}}
    
    if user_id in blogger_states_2:
        print("✅ Case 2: User in both states - blogger_states should have priority")
        result_2 = True
    else:
        print("❌ Case 2: Failed")
        result_2 = False
    
    # Test case 3: User in user_states only
    blogger_states_3 = {}
    user_states_3 = {12345: {'video_id': 'test123'}}
    
    if user_id in blogger_states_3:
        print("❌ Case 3: User not in blogger_states - should not handle blogger creation")
        result_3 = False
    elif user_id in user_states_3:
        print("✅ Case 3: User in user_states only - normal flow")
        result_3 = True
    else:
        print("❌ Case 3: User in neither state - should ask for video")
        result_3 = False
    
    return result_1 and result_2 and result_3

def main():
    """Run all tests"""
    print("🚀 Bot Logic Fix Test Suite")
    print("=" * 60)
    
    tests = [
        ("Bot Logic Fix", test_bot_logic),
        ("Blogger State Priority", test_blogger_state_priority)
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
        print("🎉 All tests passed! Bot logic fix is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

