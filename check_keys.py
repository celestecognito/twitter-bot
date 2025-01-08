import os
print("=== Checking API Keys ===")
print(f"CONSUMER_KEY: {'✅ Exists' if os.environ.get('CONSUMER_KEY') else '❌ Missing'}")
print(f"CONSUMER_SECRET: {'✅ Exists' if os.environ.get('CONSUMER_SECRET') else '❌ Missing'}")
print(f"ACCESS_TOKEN: {'✅ Exists' if os.environ.get('ACCESS_TOKEN') else '❌ Missing'}")
print(f"ACCESS_TOKEN_SECRET: {'✅ Exists' if os.environ.get('ACCESS_TOKEN_SECRET') else '❌ Missing'}")
print(f"OPENAI_API_KEY: {'✅ Exists' if os.environ.get('OPENAI_API_KEY') else '❌ Missing'}")
