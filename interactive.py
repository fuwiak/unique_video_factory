#!/usr/bin/env python3
"""
Interaktywny skrypt do unikalizacji wideo
"""

import os
import sys
from video_uniquizer import VideoUniquizer

def get_video_files():
    """Znajdź wszystkie pliki wideo w bieżącym katalogu"""
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv']
    video_files = []
    
    for file in os.listdir('.'):
        if any(file.lower().endswith(ext) for ext in video_extensions):
            video_files.append(file)
    
    return sorted(video_files)

def choose_video():
    """Pozwól użytkownikowi wybrać plik wideo"""
    video_files = get_video_files()
    
    if not video_files:
        print("❌ Nie znaleziono plików wideo w bieżącym katalogu!")
        print("Dostępne rozszerzenia: .mp4, .avi, .mov, .mkv, .wmv, .flv")
        return None
    
    print("📁 Znalezione pliki wideo:")
    for i, file in enumerate(video_files, 1):
        size_mb = os.path.getsize(file) / (1024*1024)
        print(f"   {i}. {file} ({size_mb:.1f} MB)")
    
    print(f"   {len(video_files) + 1}. Wprowadź własną ścieżkę")
    print()
    
    while True:
        try:
            choice = input("Wybierz plik (numer): ").strip()
            
            if choice.isdigit():
                choice_num = int(choice)
                if 1 <= choice_num <= len(video_files):
                    return video_files[choice_num - 1]
                elif choice_num == len(video_files) + 1:
                    custom_path = input("Wprowadź ścieżkę do pliku: ").strip()
                    if os.path.exists(custom_path):
                        return custom_path
                    else:
                        print("❌ Plik nie istnieje!")
                        continue
                else:
                    print("❌ Nieprawidłowy numer!")
                    continue
            else:
                print("❌ Wprowadź numer!")
                continue
                
        except KeyboardInterrupt:
            print("\n👋 Do widzenia!")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Błąd: {e}")
            continue

def choose_effects():
    """Pozwól użytkownikowi wybrać efekty"""
    print("\n🎨 Wybierz efekty do zastosowania:")
    print("1. Tylko efekty czasowe (szybkość, przycinanie)")
    print("2. Tylko efekty społecznościowe (Instagram, TikTok, YouTube)")
    print("3. Wszystkie efekty (czasowe + społecznościowe)")
    print("4. Własny wybór")
    
    while True:
        try:
            choice = input("Wybierz opcję (1-4): ").strip()
            
            if choice == '1':
                return ['temporal']
            elif choice == '2':
                return ['social']
            elif choice == '3':
                return ['temporal', 'social']
            elif choice == '4':
                print("\nDostępne efekty:")
                print("- temporal: Efekty czasowe")
                print("- social: Efekty społecznościowe")
                print("- visual: Efekty wizualne")
                print("- neural: Efekty neuronowe")
                
                effects_input = input("Wprowadź efekty (oddzielone przecinkami): ").strip()
                effects = [e.strip() for e in effects_input.split(',') if e.strip()]
                return effects if effects else ['temporal', 'social']
            else:
                print("❌ Nieprawidłowy wybór!")
                continue
                
        except KeyboardInterrupt:
            print("\n👋 Do widzenia!")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Błąd: {e}")
            continue

def main():
    print("🎬 INTERAKTYWNA UNIKALIZACJA WIDEO")
    print("=" * 50)
    
    try:
        # Wybierz plik wideo
        input_video = choose_video()
        if not input_video:
            return
        
        print(f"\n📁 Wybrany plik: {input_video}")
        size_mb = os.path.getsize(input_video) / (1024*1024)
        print(f"📊 Rozmiar: {size_mb:.1f} MB")
        
        # Wybierz efekty
        effects = choose_effects()
        
        # Nazwa pliku wyjściowego
        base_name = os.path.splitext(os.path.basename(input_video))[0]
        output_video = f"uniquized_{base_name}.mp4"
        
        print(f"\n📁 Plik wyjściowy: {output_video}")
        print(f"🎨 Efekty: {', '.join(effects)}")
        
        # Potwierdź
        confirm = input("\nCzy kontynuować? (y/N): ").strip().lower()
        if confirm not in ['y', 'yes', 'tak', 't']:
            print("❌ Anulowano!")
            return
        
        print("\n🚀 Rozpoczynam unikalizację...")
        
        # Utwórz unikalizator
        uniquizer = VideoUniquizer()
        
        # Zastosuj efekty
        result = uniquizer.uniquize_video(
            input_path=input_video,
            output_path=output_video,
            effects=effects
        )
        
        print(f"\n✅ GOTOWE!")
        print(f"📁 Wynik: {result}")
        if os.path.exists(result):
            result_size = os.path.getsize(result) / (1024*1024)
            print(f"📊 Rozmiar: {result_size:.1f} MB")
        
    except KeyboardInterrupt:
        print("\n👋 Do widzenia!")
    except Exception as e:
        print(f"❌ Błąd: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
