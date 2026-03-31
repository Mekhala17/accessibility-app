from pyngrok import ngrok
import time

# Add your authtoken
ngrok.set_auth_token("33EOoU2I7Uakjl4cbpn69nC4inY_2LaEP5d9n8zmxkEy1btnE")

try:
    print("Starting ngrok tunnel...\n")
    public_url = ngrok.connect(5001)
    print(f"✅ Your public URL: {public_url}")
    print(f"\n🚀 Share this URL with friends:\n   {public_url}\n")
    print("Keep this window open!\n")

    # Keep it running
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("\n\nStopping ngrok...")
    ngrok.kill()
    print("✅ ngrok stopped!")