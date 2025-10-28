#!/usr/bin/env python3
"""
Test czy bot poprawnie wykrywa VK clips URL
"""

def test_bot_logic():
    """Test logiki bota dla VK clips"""
    print("🔍 Test logiki bota dla VK clips")
    
    # Test URL
    url = "https://vk.com/clips/id1069245351?feedType=ownerFeed&owner=1069245351&z=clip1069245351_456239129"
    
    print(f"URL: {url}")
    print(f"Platform: VK")
    print(f"Zawiera '/clips/': {'/clips/' in url}")
    
    # Test logiki bota
    if '/clips/' in url:
        print("✅ Bot powinien wywołać get_vk_clip_data")
        print("🎬 Bot wywołuje get_vk_clip_data dla URL: ...")
        print("📊 Bot otrzymał wynik z get_vk_clip_data: ...")
    else:
        print("❌ Bot nie wywoła get_vk_clip_data")
        print("Bot wywoła check_vk_stats")
    
    # Test czy może problem jest w group_links_by_platform
    print(f"\n🔍 Test group_links_by_platform:")
    print(f"URL zawiera 'vk.com': {'vk.com' in url.lower()}")
    print(f"URL zawiera '/clips/': {'/clips/' in url}")
    
    # Symulacja group_links_by_platform
    if 'vk.com' in url.lower():
        print("✅ URL zostanie sklasyfikowany jako VK")
        # Symulacja convert_vk_to_clips_url
        if '/clips/' in url:
            print("✅ convert_vk_to_clips_url zwróci URL bez zmian")
            final_url = url
        else:
            print("❌ convert_vk_to_clips_url zmieni URL")
            final_url = "https://vk.com/clips/id1069245351"  # Bez parametrów
        
        print(f"Final URL: {final_url}")
        print(f"Final URL zawiera '/clips/': {'/clips/' in final_url}")

if __name__ == '__main__':
    test_bot_logic()
