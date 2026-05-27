"""
geometry_battery.py — unified runner for the Model Geometry Battery (Pillar A).

Loads a model once (eager attention — strict superset), dispatches the importable
probes across the four levels (static->dynamic), emits one combined report with a
`coherence_placement` summary. Each probe wrapped in try/except: one failing
degrades the report, doesn't kill it.

See MODEL_GEOMETRY_BATTERY.md for the methodology. First unified runner; L1-topology
and L2-orthogonality (CLI-only, need pristine-vs-trained comparison) are flagged as
not-yet-wired rather than re-implemented here. Note: eval() mode is used throughout —
it disables dropout/BN but NOT autograd, so the L4 gradient probe still works.

Usage: python3 geometry_battery.py --model_id google/gemma-3-270m [--ckpt path] --output report.json
"""
import argparse, json
from pathlib import Path
import numpy as np
import torch

import ov_decorrelation_probe as ov
import effective_rank_probe as er
import functional_specialization_probe as fs
from kf_regularizer_gemma import kf_regularizer
from kf_glider_stability_probe import per_layer_meancos, TEXTS as GLIDER_TEXTS


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model_id", default="google/gemma-3-270m")
    ap.add_argument("--ckpt", default=None)
    ap.add_argument("--kf_lambda", type=float, default=5.0)
    ap.add_argument("--output", required=True)
    a = ap.parse_args()

    from transformers import AutoModelForCausalLM, AutoTokenizer
    dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    tok = AutoTokenizer.from_pretrained(a.model_id)
    model = AutoModelForCausalLM.from_pretrained(
        a.model_id, dtype=torch.float32, attn_implementation="eager").to(dev)
    if a.ckpt:
        c = torch.load(a.ckpt, map_location="cpu", weights_only=False)
        model.load_state_dict(c["model_state_dict"])
    model.eval()  # disables dropout/BN; autograd still active for L4
    n_heads = model.config.num_attention_heads
    rpt = {"model_id": a.model_id, "ckpt": a.ckpt, "levels": {}, "errors": {}}

    def safe(level, key, fn):
        try:
            rpt["levels"].setdefault(level, {})[key] = fn()
            print(f"  [{level}] {key}: ok")
        except Exception as e:
            rpt["errors"][f"{level}.{key}"] = repr(e)
            print(f"  [{level}] {key}: ERROR {e!r}")

    # L1 — weight geometry
    safe("L1_weight", "ov_write_meancos", lambda: ov.probe(model)["mean_abs_cos"])

    # L2 — activation geometry
    def _er():
        r = er.probe(model, tok, dev)
        return {"last_layer_PR": r["last_layer_PR"], "mean_PR": r["mean_PR"]}
    safe("L2_activation", "readout_effective_rank", _er)
    safe("L2_activation", "functional_class_sep", lambda: fs.probe(model, tok, dev)["class_sep_index"])

    # L3 — attention algebra (eager)
    def _l3():
        ids = tok("The Killing form measures algebraic coherence of attention heads.",
                  return_tensors="pt").to(dev)
        with torch.no_grad():
            out = model(**ids, output_attentions=True)
        cvs = kf_regularizer(out.attentions)
        return {"mean_commutator_cv": float(cvs.mean()), "n_layers": int(len(cvs))}
    safe("L3_attention_algebra", "killing_commutator_cv", _l3)

    # L4 — gradient dynamics (glider stability across inputs)
    def _l4():
        pats = [per_layer_meancos(model, tok, dev, t, n_heads, a.kf_lambda) for t in GLIDER_TEXTS]
        P = np.stack(pats)
        rs = [np.corrcoef(P[i], P[j])[0, 1] for i in range(len(P)) for j in range(i + 1, len(P))]
        r = float(np.mean(rs))
        return {"glider_cross_input_r": r,
                "interpretation": "input-stable (maintained coherence)" if r > 0.5 else "input-dependent (momentary)"}
    safe("L4_gradient_dynamics", "glider_stability", _l4)

    rpt["not_wired"] = {
        "L1_head_class_topology": "needs pristine-vs-trained comparison (eval_v07_1_generic.py CLI)",
        "L2_concept_orthogonality": "CLI-only (cosine_orthogonality_probing.py); wrap next",
        "L4_gating_signal_split": "build/dissolve split (kf_gating_signal_probe.py); wrap next",
    }

    # coherence placement (the static->dynamic read)
    L = rpt["levels"]
    ov_c = L.get("L1_weight", {}).get("ov_write_meancos", float("nan"))
    pr = L.get("L2_activation", {}).get("readout_effective_rank", {}).get("last_layer_PR", float("nan"))
    g = L.get("L4_gradient_dynamics", {}).get("glider_stability", {}).get("glider_cross_input_r", None)
    rpt["coherence_placement"] = (
        f"L1 ov-meancos={ov_c:.3f} | L2 readout-PR={pr:.1f} | L4 glider-r={(g if g is not None else float('nan')):.3f} -> "
        + ("DYNAMIC coherence present" if (g is not None and g > 0.5)
           else "STATIC structure only (no dynamic-coherence signal at L4)")
    )

    Path(a.output).parent.mkdir(parents=True, exist_ok=True)
    json.dump(rpt, open(a.output, "w"), indent=2)
    print("\n=== coherence_placement ===")
    print(rpt["coherence_placement"])
    print(f"errors: {len(rpt['errors'])}  saved: {a.output}")


if __name__ == "__main__":
    main()
