"""
Spotify Integration Test Script
Teste die Spotify API Verbindung
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.spotify_service import spotify_service
from app.core.config import settings


def test_spotify_auth():
    """Test Spotify Authentication Flow"""
    print("🎵 Hister 2.0 - Spotify Integration Test\n")
    print("=" * 50)
    
    # Check Config
    print("\n1️⃣  Config Check:")
    print(f"   Client ID: {settings.spotify_client_id[:10]}..." if settings.spotify_client_id else "   ❌ FEHLT")
    print(f"   Client Secret: {settings.spotify_client_secret[:10]}..." if settings.spotify_client_secret else "   ❌ FEHLT")
    print(f"   Redirect URI: {settings.spotify_redirect_uri}")
    
    if not settings.spotify_client_id or not settings.spotify_client_secret:
        print("\n❌ FEHLER: Spotify Credentials fehlen!")
        print("   1. Gehe zu: https://developer.spotify.com/dashboard")
        print("   2. Erstelle eine neue App")
        print("   3. Kopiere .env.example zu .env")
        print("   4. Trage Client ID & Secret ein")
        return False
    
    # Generate Auth URL
    print("\n2️⃣  Generiere Auth URL...")
    try:
        auth_url = spotify_service.get_auth_url()
        print(f"   ✅ Auth URL generiert")
        print(f"\n   🔗 Öffne diese URL im Browser:")
        print(f"   {auth_url}\n")
        print("   Nach dem Login wirst du weitergeleitet.")
        print("   Kopiere den 'code' Parameter aus der URL.")
        return True
    except Exception as e:
        print(f"   ❌ Fehler: {e}")
        return False


def test_playlist_access():
    """Test Playlist Access (requires manual auth)"""
    print("\n3️⃣  Playlist Test:")
    print("   Für diesen Test musst du dich authentifizieren.")
    
    # Beispiel Playlist ID (Spotify's "Today's Top Hits" ist öffentlich)
    test_playlist_id = "37i9dQZF1DXcBWIGoYBM5M"
    
    try:
        print(f"\n   Teste mit öffentlicher Playlist: {test_playlist_id}")
        playlist_info = spotify_service.get_playlist_tracks(test_playlist_id)
        
        print(f"   ✅ Playlist geladen!")
        print(f"   📝 Name: {playlist_info.name}")
        print(f"   👤 Owner: {playlist_info.owner}")
        print(f"   🎵 Tracks: {playlist_info.total_tracks}")
        
        if playlist_info.tracks:
            print(f"\n   Erste 3 Songs:")
            for i, track in enumerate(playlist_info.tracks[:3], 1):
                print(f"   {i}. {track.artist} - {track.title}")
                print(f"      Album: {track.album}")
                print(f"      Jahr: {track.release_date[:4]} ({track.decade})")
        
        return True
    except Exception as e:
        print(f"   ❌ Fehler: {e}")
        print(f"   Hinweis: Möglicherweise musst du dich zuerst authentifizieren.")
        return False


def test_decade_calculation():
    """Test Decade Calculation"""
    print("\n4️⃣  Jahrzehnt-Berechnung Test:")
    
    test_dates = [
        ("1994-08-23", "1990er"),
        ("2003-11-17", "2000er"),
        ("1985-07-13", "1980er"),
        ("2020-03-27", "2020er"),
        ("1979-12-31", "1970er"),
    ]
    
    all_correct = True
    for date, expected in test_dates:
        result = spotify_service._get_decade(date)
        status = "✅" if result == expected else "❌"
        print(f"   {status} {date} -> {result} (erwartet: {expected})")
        if result != expected:
            all_correct = False
    
    return all_correct


def main():
    """Run all tests"""
    print("\n" + "=" * 50)
    print("🧪 STARTE TESTS")
    print("=" * 50)
    
    # Test 1: Auth
    auth_ok = test_spotify_auth()
    
    # Test 2: Decade Calculation (immer möglich)
    decade_ok = test_decade_calculation()
    
    # Test 3: Playlist (optional, braucht Auth)
    print("\n" + "=" * 50)
    playlist_ok = test_playlist_access()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 ZUSAMMENFASSUNG")
    print("=" * 50)
    print(f"   Auth URL: {'✅' if auth_ok else '❌'}")
    print(f"   Jahrzehnt: {'✅' if decade_ok else '❌'}")
    print(f"   Playlist: {'✅' if playlist_ok else '⚠️  (optional)'}")
    
    if auth_ok and decade_ok:
        print("\n✅ Grundlegende Integration funktioniert!")
        print("\n📝 NÄCHSTE SCHRITTE:")
        print("   1. Öffne die Auth URL oben im Browser")
        print("   2. Logge dich bei Spotify ein")
        print("   3. Starte den Backend-Server:")
        print("      cd backend")
        print("      uvicorn app.main:app --reload")
        print("   4. Öffne http://localhost:8000/docs")
        print("   5. Teste die API Endpoints")
    else:
        print("\n❌ Es gibt noch Probleme. Siehe Fehler oben.")
    
    print("\n" + "=" * 50 + "\n")


if __name__ == "__main__":
    main()
