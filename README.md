---
language:
- en
license: apache-2.0
library_name: transformers
pipeline_tag: text-generation
base_model: Qwen/Qwen3.5-2B-Base
base_model_relation: finetune
tags:
- omarchy
- qwen3.5
- qlora
- lora
- gguf
- llama.cpp
---

# Omarchy Nano 2B

Omarchy Nano 2B is an experimental, Omarchy-focused fine-tune of
[Qwen3.5-2B-Base](https://huggingface.co/Qwen/Qwen3.5-2B-Base). It is intended
to answer questions about Omarchy configuration, commands, applications, and
workflows. It is not an official Omarchy project.

## Artifacts

- `gguf-q4_k_m/omarchy-nano.Q4_K_M.gguf` — approximately 1.25 GB; intended
  for llama.cpp-compatible local inference.
- `gguf-q4_k_m/omarchy-nano.F16-mmproj.gguf` — optional multimodal projector.
- `adapter/` — QLoRA adapter, tokenizer, processor configuration, and training
  metadata.

For low-memory or potato PCs, download only the Q4_K_M GGUF. The projector is
only needed by compatible multimodal runners that accept image input.

## Training data

The dataset contains 296 examples derived from 51 non-empty Markdown files
from the Omarchy manual.

- Training split: 259 examples
- Evaluation split: 37 examples
- Split method: document-level
- Omarchy source commit: `d3d23fdddef846ebb98b52122a6ece66211c0daf`
- Image references were replaced with `[image omitted]`; training was text-only.

## Training configuration

- Method: 4-bit QLoRA
- LoRA rank: 16
- Trainable parameters: 10,911,744 (0.49%)
- Epochs: 2
- Maximum sequence length: 512
- Effective batch size: 8
- Learning rate: 2e-4
- Optimizer: 8-bit AdamW
- Hardware: Google Colab Tesla T4

Final optimization metrics:

- Training loss: 1.6297
- Evaluation loss: 1.6660

These are optimization metrics, not a task-accuracy benchmark.

## Usage with llama.cpp

Download the Q4_K_M file and run it with a llama.cpp-compatible runner:

```bash
wget -O omarchy-nano.Q4_K_M.gguf \
  https://huggingface.co/NewSonnet/omarchy-nano-2b/resolve/main/gguf-q4_k_m/omarchy-nano.Q4_K_M.gguf

llama-cli -m omarchy-nano.Q4_K_M.gguf -cnv
```

The `adapter/` directory is a LoRA adapter and must be loaded on the base
model with a PEFT-compatible Transformers workflow; it is not a standalone
model.

## Limitations

This is a small experimental model. It may provide incorrect commands, omit
important context, or hallucinate configuration details. Verify commands
against the current Omarchy documentation before running them, especially for
system or security-sensitive changes.

The training data was text-only. The included projector does not mean that
this fine-tune was trained for image understanding.

## Reproducibility files

- `omarchy-nano.ipynb` — cleaned, credential-free Colab training notebook.
- `requirements-colab.txt` — pinned top-level training dependencies.
- `scripts/prepare_omarchy_data.py` — image-sanitizing, document-level JSONL
  preprocessing path.
- `data/PROVENANCE.json` — source commit, dataset counts, and run settings.
- `evaluation/results.json` — recorded held-out loss from the completed run.

The notebook reuses an existing Drive dataset when present. If it is absent,
it rebuilds a sanitized baseline from the pinned Omarchy source snapshot; the
reference counts in the provenance and evaluation files describe the completed
run, not a guarantee that every fresh preprocessing run will produce identical
counts.

Model weights, checkpoints, and credentials are intentionally excluded from
this GitHub repository. They are published separately on Hugging Face.

## Licensing and attribution

The base Qwen3.5-2B-Base model is released under Apache-2.0. The Omarchy
source material is released under the MIT License. Users must comply with both
licenses and retain the relevant attribution.

- Base model: https://huggingface.co/Qwen/Qwen3.5-2B-Base
- Omarchy source: https://github.com/omacom/omarchy
- Reproducibility project: https://github.com/EF-Code/omarchy-nano
