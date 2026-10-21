#!/usr/bin/env python3
"""Execute the extracted OpenEMR portal PHP rendering path with fake credentials."""
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMAGE = "php@sha256:bd6f2dc7a4e4537e927355c94a74c3022911aa504278f5f0fd94016c90dfaecc"
private = "sk_test_FAKE_DEMO_ONLY"
public = "pk_test_FAKE_DEMO_ONLY"
command = ["docker", "run", "--rm", "--network", "none", "--read-only", "--tmpfs", "/tmp",
           "--mount", f"type=bind,source={ROOT},target=/case,readonly",
           "-e", f"DEMO_PUBLIC={public}", "-e", f"DEMO_PRIVATE={private}",
           "-e", "DEMO_GATEWAY=Stripe", IMAGE, "php", "-d", "display_errors=0", "/case/portal/render.php"]
result = subprocess.run(command, text=True, capture_output=True, timeout=45)
if result.returncode != 0 or "var chargeMsg =" not in result.stdout or public not in result.stdout:
    raise SystemExit("ERROR: portal render or public client value was unavailable")
if private in result.stdout:
    raise SystemExit("FAIL: private gateway credential appeared in browser response")
print("PASS: private credential absent; public client value present")
