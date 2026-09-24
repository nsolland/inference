import hashlib, json, subprocess, sys, tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
RUNNER=ROOT/"exup_eval"/"verify_receipt.py"

def test_minimal_receipt_verifies():
    with tempfile.TemporaryDirectory() as d:
        d=Path(d)
        for n in ("base.bin","cand.bin","raw.json"): (d/n).write_bytes(n.encode())
        r={
          "protocol":"EXUP-EVAL-01","protocol_version":"0.1.0","timestamp_utc":"2026-09-24T00:00:00Z",
          "benchmark_upstream_commit":"3fbc329939999c13d0a7b5e67fb2092287e06047","runner_sha256":"pending-self-hash",
          "workload":{"name":"fixture"},"dataset_sha256":"0"*64,
          "baseline_artifact_sha256":hashlib.sha256(b"base.bin").hexdigest(),
          "candidate_artifact_sha256":hashlib.sha256(b"cand.bin").hexdigest(),
          "hardware_fingerprint":{"fixture":True},"software_fingerprint":{"fixture":True},
          "scenario":"Offline","acceptance_rule":{"fixture":True},"resource_envelope":{"fixture":True},
          "baseline_accuracy":1.0,"candidate_accuracy":1.0,
          "baseline_performance":1.0,"candidate_performance":1.1,
          "raw_results_sha256":hashlib.sha256(b"raw.json").hexdigest(),"verdict":"PASS"
        }
        p=d/"receipt.json"; p.write_text(json.dumps(r))
        x=subprocess.run([sys.executable,str(RUNNER),str(p),"--baseline-artifact",str(d/"base.bin"),"--candidate-artifact",str(d/"cand.bin"),"--raw-results",str(d/"raw.json")],capture_output=True,text=True)
        assert x.returncode==0, x.stdout+x.stderr
        assert json.loads(x.stdout)["valid"] is True
