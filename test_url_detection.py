#!/usr/bin/env python3
"""
Test czy bot poprawnie wykrywa VK clips URL
"""

def test_url_detection():
    """Test wykrywania VK clips URL"""
    print("🔍 Test wykrywania VK clips URL")
    
    # Test URL
    url = "https://vk.com/clips/id1069245351?feedType=ownerFeed&owner=1069245351&z=clip1069245351_456239129"
    
    print(f"URL: {url}")
    print(f"Zawiera '/clips/': {'/clips/' in url}")
    
    # Test logiki bota
    if '/clips/' in url:
        print("✅ Bot powinien wywołać get_vk_clip_data")
    else:
        print("❌ Bot nie wywoła get_vk_clip_data")
    
    # Test czy to VK URL
    if 'vk.com' in url.lower():
        print("✅ To jest VK URL")
    else:
        print("❌ To nie jest VK URL")

if __name__ == '__main__':
    test_url_detection()
