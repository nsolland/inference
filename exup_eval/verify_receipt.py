#!/usr/bin/env python3
import argparse, hashlib, json, pathlib, sys
REQUIRED = ["protocol","protocol_version","timestamp_utc","benchmark_upstream_commit","runner_sha256","workload","dataset_sha256","baseline_artifact_sha256","candidate_artifact_sha256","hardware_fingerprint","software_fingerprint","scenario","acceptance_rule","resource_envelope","baseline_accuracy","candidate_accuracy","baseline_performance","candidate_performance","raw_results_sha256","verdict"]

def sha256_file(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest()

def canonical(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()

def main():
    p=argparse.ArgumentParser(description="EXUP-EVAL-01 receipt verifier")
    p.add_argument("receipt")
    p.add_argument("--baseline-artifact")
    p.add_argument("--candidate-artifact")
    p.add_argument("--raw-results")
    a=p.parse_args()
    r=json.loads(pathlib.Path(a.receipt).read_text())
    missing=[k for k in REQUIRED if k not in r]
    errors=[]
    if missing: errors.append("missing fields: "+", ".join(missing))
    for arg,field in [(a.baseline_artifact,"baseline_artifact_sha256"),(a.candidate_artifact,"candidate_artifact_sha256"),(a.raw_results,"raw_results_sha256")]:
        if arg and r.get(field)!=sha256_file(arg): errors.append(field+" mismatch")
    if r.get("protocol")!="EXUP-EVAL-01": errors.append("wrong protocol")
    if r.get("verdict") not in ("PASS","FAIL"): errors.append("verdict must be PASS or FAIL")
    if errors:
        print(json.dumps({"valid":False,"errors":errors},indent=2)); return 2
    body=dict(r); body.pop("receipt_sha256",None)
    digest=hashlib.sha256(canonical(body)).hexdigest()
    if r.get("receipt_sha256") and r["receipt_sha256"]!=digest:
        print(json.dumps({"valid":False,"errors":["receipt_sha256 mismatch"]},indent=2)); return 2
    print(json.dumps({"valid":True,"computed_receipt_sha256":digest},indent=2)); return 0
if __name__=="__main__": sys.exit(main())
