#!/usr/bin/env python3
"""
Test regex dla VK video ID extraction
"""

import re

def test_extract_vk_video_id(url: str):
    """Test wyciągania video ID z URL VK clip"""
    print(f"URL: {url}")
    
    # Format: https://vk.com/clips/id1069245351?feedType=ownerFeed&owner=1069245351&z=clip1069245351_456239129
    # Szukamy clip{owner_id}_{video_id}
    clip_match = re.search(r'clip(\d+)_(\d+)', url)
    if clip_match:
        print(f"✅ clip_match: {clip_match.groups()}")
        return clip_match.group(2)  # video_id
    
    # Alternatywnie szukamy w parametrze z
    z_match = re.search(r'z=clip\d+_(\d+)', url)
    if z_match:
        print(f"✅ z_match: {z_match.groups()}")
        return z_match.group(1)
    
    print("❌ Brak dopasowania")
    return None

def test_extract_vk_owner_id(url: str):
    """Test wyciągania owner ID z URL VK clip"""
    print(f"URL: {url}")
    
    # Format: https://vk.com/clips/id1069245351?feedType=ownerFeed&owner=1069245351&z=clip1069245351_456239129
    # Szukamy owner=123456
    owner_match = re.search(r'owner=(\d+)', url)
    if owner_match:
        print(f"✅ owner_match: {owner_match.groups()}")
        return owner_match.group(1)
    
    # Alternatywnie z clip{owner_id}_{video_id}
    clip_match = re.search(r'clip(\d+)_\d+', url)
    if clip_match:
        print(f"✅ clip_match: {clip_match.groups()}")
        return clip_match.group(1)
    
    print("❌ Brak dopasowania")
    return None

if __name__ == '__main__':
    print("🔍 Test regex dla VK video ID extraction")
    
    # Test URL
    url = "https://vk.com/clips/id1069245351?feedType=ownerFeed&owner=1069245351&z=clip1069245351_456239129"
    
    print("\n📊 Test video ID:")
    video_id = test_extract_vk_video_id(url)
    print(f"Video ID: {video_id}")
    
    print("\n📊 Test owner ID:")
    owner_id = test_extract_vk_owner_id(url)
    print(f"Owner ID: {owner_id}")
    
    print("\n🔍 Debug regex:")
    print(f"URL: {url}")
    print(f"Szukam: clip(\\d+)_(\\d+)")
    clip_match = re.search(r'clip(\d+)_(\d+)', url)
    print(f"clip_match: {clip_match}")
    if clip_match:
        print(f"Groups: {clip_match.groups()}")
    
    print(f"\nSzukam: z=clip\\d+_(\\d+)")
    z_match = re.search(r'z=clip\d+_(\d+)', url)
    print(f"z_match: {z_match}")
    if z_match:
        print(f"Groups: {z_match.groups()}")
    
    print(f"\nSzukam: owner=(\\d+)")
    owner_match = re.search(r'owner=(\d+)', url)
    print(f"owner_match: {owner_match}")
    if owner_match:
        print(f"Groups: {owner_match.groups()}")
