#!/usr/bin/env python3
"""Trusted payment-boundary check for a pinned OpenEMR portal candidate.

The candidate PHP file is treated as data. The render wrapper and expected
secret values come from this checker, not from files in the candidate branch.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path


PHP_IMAGE = "php@sha256:bd6f2dc7a4e4537e927355c94a74c3022911aa504278f5f0fd94016c90dfaecc"
PRIVATE = "sk_test_FAKE_DEMO_ONLY"
PUBLIC = "pk_test_FAKE_DEMO_ONLY"


def render_wrapper(source: str) -> str:
    start_marker = '    <script type="text/javascript">\n        var chargeMsg = '
    start = source.index(start_marker)
    end = source.index("        function calctotal()", start)
    fragment = source[start:end]
    if fragment.count("var publicKey =") != 1 or "gateway_public_key" not in fragment:
        raise ValueError("Payment script markers changed; review the candidate manually")
    auth_start = source.index("<?php if ($GLOBALS['payment_gateway'] == 'AuthorizeNet') {")
    auth_end = source.index("<?php }  // end authorize.net ?>", auth_start) + len("<?php }  // end authorize.net ?>")
    prefix = """<?php
$GLOBALS['gateway_public_key'] = getenv('DEMO_PUBLIC');
$GLOBALS['gateway_api_key'] = getenv('DEMO_PRIVATE');
$GLOBALS['payment_gateway'] = 'Stripe';
function xl($value) { return $value; }
?>
"""
    return prefix + fragment + "    </script>\n" + source[auth_start:auth_end] + "\n"


def check(candidate: Path) -> dict:
    source = candidate.read_bytes()
    source_hash = hashlib.sha256(source).hexdigest()
    try:
        wrapper = render_wrapper(source.decode())
    except (UnicodeDecodeError, ValueError) as exc:
        return {"status": "error", "reason": str(exc), "candidate_sha256": source_hash,
                "execution_scope": "isolated_payment_component", "php_image": PHP_IMAGE}
    with tempfile.TemporaryDirectory(prefix="openemr-gate-") as directory:
        root = Path(directory)
        root.chmod(0o755)
        (root / "render.php").write_text(wrapper)
        (root / "render.php").chmod(0o644)
        command = ["docker", "run", "--rm", "--network", "none", "--read-only",
                   "--cap-drop", "ALL", "--security-opt", "no-new-privileges",
                   "--pids-limit", "64", "--memory", "256m", "--cpus", "1",
                   "--user", "65534:65534", "--tmpfs", "/tmp",
                   "--mount", f"type=bind,source={root},target=/case,readonly",
                   "-e", f"DEMO_PUBLIC={PUBLIC}", "-e", f"DEMO_PRIVATE={PRIVATE}",
                   PHP_IMAGE, "php", "-d", "display_errors=0", "/case/render.php"]
        try:
            result = subprocess.run(command, text=True, capture_output=True, timeout=45, env=os.environ.copy())
        except (subprocess.TimeoutExpired, OSError) as exc:
            return {"status": "error", "reason": type(exc).__name__, "candidate_sha256": source_hash,
                    "execution_scope": "isolated_payment_component", "php_image": PHP_IMAGE}
    reached = result.returncode == 0 and "var chargeMsg =" in result.stdout and "var publicKey =" in result.stdout
    public_present = PUBLIC in result.stdout
    secret_absent = PRIVATE not in result.stdout
    status = "passed" if reached and public_present and secret_absent else "failed" if reached else "error"
    return {"status": status, "candidate_sha256": source_hash, "php_image": PHP_IMAGE,
            "execution_scope": "isolated_payment_component", "render_exit_code": result.returncode,
            "render_reached": reached, "public_client_value_present": public_present,
            "private_credential_absent": secret_absent,
            "browser_response_sha256": hashlib.sha256(result.stdout.encode()).hexdigest(),
            "failure_reason": "private_gateway_credential_in_browser_response" if reached and not secret_absent else None,
            "claim_limit": "Pinned OpenEMR payment script fragment with synthetic credentials; no full application transaction."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate", type=Path)
    args = parser.parse_args()
    record = check(args.candidate)
    print(json.dumps(record, indent=2))
    raise SystemExit(0 if record["status"] == "passed" else 1)
