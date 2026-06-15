"""
Quick Gemini API health check.

Run this anytime with:
    python test_gemini.py

It will tell you in plain language whether your Gemini API key
and model are working, or exactly what's wrong (expired key,
quota exceeded, wrong model name, no internet, etc.) -
without you needing to read through app.py.
"""

import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get('GEMINI_API_KEY', '')
MODEL_NAME = 'gemini-2.5-flash'  # should match the model used in app.py


def main():
    print("=" * 50)
    print("Gemini API Health Check")
    print("=" * 50)

    if not API_KEY:
        print("❌ GEMINI_API_KEY .env file mein set nahi hai.")
        print("   -> .env file mein ye line check karein: GEMINI_API_KEY=your_key_here")
        return

    print(f"API Key (first 10 chars): {API_KEY[:10]}...")
    print(f"Model being tested: {MODEL_NAME}")
    print("-" * 50)

    try:
        import google.generativeai as genai
    except ImportError:
        print("❌ 'google-generativeai' package installed nahi hai.")
        print("   -> Run: pip install google-generativeai")
        return

    try:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content("Say 'OK' if you can read this.")
        print("✅ SUCCESS! Gemini API kaam kar raha hai.")
        print(f"   Response: {response.text.strip()}")

    except Exception as e:
        err = str(e)
        print("❌ FAILED. Gemini API call mein error aaya:\n")
        print(f"   Raw error: {err}\n")

        lower = err.lower()
        if "api_key" in lower or "api key" in lower or "permission" in lower or "401" in lower or "403" in lower:
            print("   -> WAJAH: Aapki API KEY invalid/expired/revoked hai.")
            print("   -> FIX: https://aistudio.google.com/apikey par jaa kar nayi free API key banayein")
            print("           aur .env file mein GEMINI_API_KEY= ki value update karein.")
        elif "404" in lower or "not found" in lower:
            print("   -> WAJAH: Model name galat hai ya retire ho gaya hai.")
            print(f"   -> FIX: '{MODEL_NAME}' ko kisi current model se replace karein,")
            print("           e.g. 'gemini-2.5-flash' ya 'gemini-3.5-flash'.")
        elif "429" in lower or "quota" in lower or "resource_exhausted" in lower:
            print("   -> WAJAH: API quota/rate limit khatam ho gaya hai (free tier limit).")
            print("   -> FIX: Thodi der wait karein, ya Google AI Studio mein billing/quota check karein,")
            print("           ya nayi API key bana lein.")
        elif "connection" in lower or "network" in lower or "timeout" in lower:
            print("   -> WAJAH: Internet connection ka masla lag raha hai.")
            print("   -> FIX: Internet connection check karein.")
        else:
            print("   -> Upar wala error message Claude ko bhej dein, exact fix de denge.")


if __name__ == "__main__":
    main()
