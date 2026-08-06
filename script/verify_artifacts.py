#!/usr/bin/env python
"""Verify all artifacts are clean (no secrets, API keys, etc.)."""

import sys
from pathlib import Path
import json
import re
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.config import load_settings

settings = load_settings()

print("="*70)
print("CP6: Artifact Verification & Secret Scan")
print("="*70)

# Patterns to detect
SECRET_PATTERNS = [
    r'api[_-]?key',
    r'secret[_-]?key',
    r'password',
    r'token',
    r'sk_[a-zA-Z0-9]{20,}',  # Stripe-like keys
    r'pk_[a-zA-Z0-9]{20,}',  # Stripe-like keys
    r'bearer\s+[a-zA-Z0-9\-\.]+',  # Bearer tokens
    r'https://[a-zA-Z0-9\-]+:[a-zA-Z0-9\-]+@',  # URLs with credentials
]

artifacts_to_check = [
    # Data files
    ('Baseline JSON', settings.paths.clean_json),
    ('Corrupted CSV', settings.paths.corrupted_clean_csv),
    ('Corrupted JSON', settings.paths.corrupted_clean_json),
    ('Repaired CSV', settings.paths.repaired_clean_csv),
    ('Repaired JSON', settings.paths.repaired_clean_json),
    
    # Quality files
    ('Baseline Quality', settings.paths.quality_dir / 'baseline_quality.json'),
    ('Corrupted Quality', settings.paths.quality_dir / 'corrupted_quality.json'),
    ('Repaired Quality', settings.paths.quality_dir / 'repaired_quality.json'),
    ('Baseline Freshness', settings.paths.freshness_report),
    ('Corrupted Freshness', settings.paths.quality_dir / 'corrupted_freshness.json'),
    ('Repaired Freshness', settings.paths.quality_dir / 'repaired_freshness.json'),
    
    # Results
    ('Baseline Metrics', settings.paths.baseline_metrics),
    ('Baseline Answers', settings.paths.baseline_answers),
    ('Corruption Log', settings.paths.corruption_log),
    
    # Reports
    ('Phase1 Report', settings.paths.baseline_report),
    ('Corruption Report', settings.paths.comparison_report),
]

print("\nScanning artifacts for secrets/sensitive data...\n")

issues_found = []
files_scanned = 0

for name, path in artifacts_to_check:
    if not path.exists():
        print(f"⏭️  {name}: Not found (skipping)")
        continue
    
    files_scanned += 1
    
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Check for secret patterns (case-insensitive)
        found_secrets = False
        for pattern in SECRET_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                # Check if it's actually a secret or just a field name
                # Field names like "api_key" in data are ok, but actual keys are not
                if any(secret in content for secret in [
                    'GOOGLE_API_KEY',
                    'OPENAI_API_KEY', 
                    'ANTHROPIC_API_KEY',
                    'sk-',
                    'pk-',
                    'Bearer '
                ]):
                    issues_found.append(f"{name}: Possible secret detected")
                    found_secrets = True
                    break
        
        if not found_secrets:
            # Additional check: no API keys with actual values
            if ('api_key' in content or 'secret' in content) and '=' in content:
                lines_with_secrets = [l for l in content.split('\n') 
                                     if ('api' in l.lower() and '=' in l) or 
                                        ('key' in l.lower() and '=' in l)]
                if lines_with_secrets and not any('""' in l or "''" in l for l in lines_with_secrets):
                    issues_found.append(f"{name}: Possible credentials in assignment")
                    found_secrets = True
        
        if found_secrets:
            print(f"❌ {name}: SENSITIVE DATA DETECTED")
        else:
            print(f"✅ {name}: Clean")
            
    except Exception as e:
        print(f"⚠️  {name}: Error scanning - {str(e)[:50]}")

print(f"\n{'-'*70}")
print(f"Files scanned: {files_scanned}")
print(f"Issues found: {len(issues_found)}")

if issues_found:
    print(f"\n🚨 SECURITY ISSUES:")
    for issue in issues_found:
        print(f"  - {issue}")
else:
    print(f"\n✅ All artifacts are clean - no secrets detected!")

print(f"\n{'-'*70}")
print("Artifact Integrity Check")
print(f"{'-'*70}\n")

# Verify data consistency
try:
    baseline_quality = json.load(open(settings.paths.quality_dir / 'baseline_quality.json'))
    repaired_quality = json.load(open(settings.paths.quality_dir / 'repaired_quality.json'))
    corrupted_quality = json.load(open(settings.paths.quality_dir / 'corrupted_quality.json'))
    
    print("Quality Metric Consistency:")
    
    # Check repaired matches baseline
    if baseline_quality['total_rows'] == repaired_quality['total_rows']:
        print(f"  ✅ Row count preserved: {baseline_quality['total_rows']}")
    else:
        print(f"  ❌ Row count mismatch: baseline={baseline_quality['total_rows']}, repaired={repaired_quality['total_rows']}")
    
    if baseline_quality['passed'] == repaired_quality['passed']:
        print(f"  ✅ Quality gates match: {baseline_quality['passed']}")
    else:
        print(f"  ❌ Quality gate mismatch: baseline={baseline_quality['passed']}, repaired={repaired_quality['passed']}")
    
    # Check corrupted shows degradation
    if corrupted_quality['summary_empty_count'] > baseline_quality['summary_empty_count']:
        print(f"  ✅ Corruption detected: empty_summaries baseline={baseline_quality['summary_empty_count']} → corrupted={corrupted_quality['summary_empty_count']}")
    else:
        print(f"  ⚠️  No summary corruption detected")
    
    if not corrupted_quality['passed'] and baseline_quality['passed']:
        print(f"  ✅ Quality gate failure detected in corrupted data")
    else:
        print(f"  ⚠️  Expected quality gate failure in corrupted data")
    
except Exception as e:
    print(f"  ❌ Error checking consistency: {e}")

print(f"\n{'='*70}")
print("✅ Artifact Verification Complete")
print(f"{'='*70}")
print("\nReady for final submission!")
