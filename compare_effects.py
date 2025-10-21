#!/usr/bin/env python3
"""
Skrypt do porównania różnych efektów na tym samym wideo
"""

import os
from video_uniquizer import VideoUniquizer

def compare_effects():
    print("🎬 PORÓWNANIE EFEKTÓW UNIKALIZACJI")
    print("=" * 50)
    
    input_video = "test.mp4"
    
    if not os.path.exists(input_video):
        print(f"❌ Plik {input_video} nie istnieje!")
        return
    
    print(f"📁 Plik wejściowy: {input_video}")
    print(f"📊 Rozmiar: {os.path.getsize(input_video) / (1024*1024):.1f} MB")
    print()
    
    try:
        uniquizer = VideoUniquizer()
        
        # Lista różnych kombinacji efektów
        effect_combinations = [
            (['temporal'], 'temporal_only'),
            (['social'], 'social_only'), 
            (['visual'], 'visual_only'),
            (['temporal', 'social'], 'temporal_social'),
            (['temporal', 'visual'], 'temporal_visual'),
            (['social', 'visual'], 'social_visual'),
            (['temporal', 'social', 'visual'], 'all_effects')
        ]
        
        print("🚀 Tworzymy wersje z różnymi efektami...")
        print()
        
        for effects, name in effect_combinations:
            output_file = f"compare_{name}.mp4"
            print(f"🎨 {name}: {', '.join(effects)}")
            
            try:
                result = uniquizer.uniquize_video(
                    input_path=input_video,
                    output_path=output_file,
                    effects=effects
                )
                
                if os.path.exists(result):
                    size_mb = os.path.getsize(result) / (1024*1024)
                    print(f"   ✅ {result} ({size_mb:.1f} MB)")
                else:
                    print(f"   ❌ Błąd tworzenia pliku")
                    
            except Exception as e:
                print(f"   ❌ Błąd: {e}")
            
            print()
        
        print("🎉 WSZYSTKIE WERSJE GOTOWE!")
        print()
        print("📁 Utworzone pliki porównawcze:")
        for _, name in effect_combinations:
            filename = f"compare_{name}.mp4"
            if os.path.exists(filename):
                size_mb = os.path.getsize(filename) / (1024*1024)
                print(f"   • {filename} - {size_mb:.1f} MB")
        
        print()
        print("🎯 Opis efektów:")
        print("   • temporal_only: Tylko zmiany prędkości i przycinanie")
        print("   • social_only: Tylko efekty społecznościowe")
        print("   • visual_only: Tylko efekty wizualne (jasność, kontrast)")
        print("   • temporal_social: Czasowe + społecznościowe")
        print("   • temporal_visual: Czasowe + wizualne")
        print("   • social_visual: Społecznościowe + wizualne")
        print("   • all_effects: Wszystkie efekty")
        
    except Exception as e:
        print(f"❌ Błąd: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    compare_effects()
