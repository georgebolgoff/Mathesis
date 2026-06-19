from dotenv import load_dotenv
from pathlib import Path
import os

root = Path(__file__).resolve().parent.parent
print("ROOT:", root)

load_dotenv(root / ".env")

key = os.getenv("TOGETHER_API_KEY")

print("KEY EXISTS:", key is not None)
print("KEY LENGTH:", len(key) if key else 0)

if key:
    print("FIRST 8:", key[:8])