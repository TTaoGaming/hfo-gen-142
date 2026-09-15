#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, pathlib, re, subprocess, tempfile

TRACK_ID = "maple-preview-gguf-gb10cuda-v1"
SOURCE_PIN = "8ce8ca6c6d370b6235dfa8e2a0611a9adb6d77d1"
FRONTIER_PATH = f"Sources/patches/{TRACK_ID}/"
TARGETS = {
    "common/arg.cpp": "common/CMakeFiles/llama-common.dir/arg.cpp.o",
    "ggml/src/ggml-cpu/ggml-cpu.c": "ggml/src/CMakeFiles/ggml-cpu.dir/ggml-cpu/ggml-cpu.c.o",
}

def run(argv, cwd=None, timeout=120):
    return subprocess.run(argv, cwd=cwd, text=True, capture_output=True, timeout=timeout, check=False)

def sha256(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()

def touched(text):
    return sorted(set(re.findall(r"^\+\+\+ b/(.+)$", text, re.M)))

def evaluate_patch(patch_path: str, source_root: str, build: bool = False) -> dict:
    patch = pathlib.Path(patch_path).resolve(); src = pathlib.Path(source_root).resolve()
    text = patch.read_text(encoding="utf-8"); paths = touched(text)
    gates = {"nonempty_patch": bool(paths), "pin_bound": False, "apply_check": False,
             "diff_check": False, "touched_tu_build": None}
    out = {"schema":"hfo.frontier-static-eval.v1", "track_id":TRACK_ID,
           "source_pin":SOURCE_PIN, "frontier_candidate_path":FRONTIER_PATH,
           "patch_sha256":sha256(patch), "touched_files":paths, "gates":gates,
           "fitness_stage":"STATIC_PREFLIGHT_ONLY", "trusted_fitness":None,
           "promotion":"HOLD_TRUSTED_GB10_FITNESS"}
    head = run(["git","-C",str(src),"rev-parse","HEAD"]).stdout.strip()
    gates["pin_bound"] = head == SOURCE_PIN
    if not gates["pin_bound"]: out["error"]="SOURCE_PIN_MISMATCH"; return out
    with tempfile.TemporaryDirectory(prefix="ff-eval-") as td:
        work = pathlib.Path(td)/"src"
        cp = run(["git","clone","-q","--shared",str(src),str(work)], timeout=180)
        if cp.returncode: out["error"]="CLONE_FAILED"; return out
        run(["git","-C",str(work),"checkout","-q","--detach",SOURCE_PIN])
        chk = run(["git","-C",str(work),"apply","--check",str(patch)])
        gates["apply_check"] = chk.returncode == 0
        if not gates["apply_check"]: out["error"]=(chk.stderr or chk.stdout)[-1200:]; return out
        run(["git","-C",str(work),"apply",str(patch)])
        dc = run(["git","-C",str(work),"diff","--check"]); gates["diff_check"] = dc.returncode == 0
        if build and gates["diff_check"]:
            build_targets = [TARGETS[p] for p in paths if p in TARGETS]
            if len(build_targets) != len(paths):
                gates["touched_tu_build"] = False; out["error"]="UNMAPPED_BUILD_TARGET"
            else:
                bdir = work/"build"
                cfg = run(["cmake","-S",str(work),"-B",str(bdir),"-G","Ninja",
                           "-DGGML_CUDA=OFF","-DGGML_NATIVE=OFF","-DLLAMA_CURL=OFF",
                           "-DCMAKE_BUILD_TYPE=Release"], timeout=180)
                if cfg.returncode:
                    gates["touched_tu_build"] = False; out["error"]="CMAKE_FAILED:"+(cfg.stderr or cfg.stdout)[-1200:]
                else:
                    b = run(["ninja","-C",str(bdir),*build_targets], timeout=420)
                    gates["touched_tu_build"] = b.returncode == 0
                    if b.returncode: out["error"]="BUILD_FAILED:"+(b.stdout+b.stderr)[-1600:]
    required=[gates["nonempty_patch"],gates["pin_bound"],gates["apply_check"],gates["diff_check"]]
    if build: required.append(gates["touched_tu_build"] is True)
    out["preflight_score"] = sum(bool(x) for x in required)/len(required)
    out["preflight_pass"] = all(bool(x) for x in required)
    return out

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("patch"); ap.add_argument("--source-root",required=True)
    ap.add_argument("--build",action="store_true"); ap.add_argument("--out")
    args=ap.parse_args(); result=evaluate_patch(args.patch,args.source_root,args.build)
    payload=json.dumps(result,sort_keys=True,indent=2)+"\n"
    if args.out: pathlib.Path(args.out).write_text(payload,encoding="utf-8")
    print(payload,end=""); return 0 if result.get("preflight_pass") else 2

if __name__ == "__main__": raise SystemExit(main())
