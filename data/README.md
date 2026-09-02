# Data and preprocessing

The training corpus is derived from the Markdown manual in the Omarchy source
repository. The original run used 51 non-empty Markdown documents and produced
296 text-only instruction examples: 259 for training and 37 for evaluation.

`../scripts/prepare_omarchy_data.py` is the checked-in preprocessing entry
point. It removes image syntax, keeps the source path in each example's
metadata, creates a document-level split, and writes JSONL files with this
schema:

```json
{"messages": [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}], "source": "..."}
```

The raw Omarchy checkout and generated JSONL files are intentionally not
committed here. Recreate them from the pinned source commit in
`PROVENANCE.json`. This keeps the GitHub repository small and makes the
provenance explicit without bundling a second copy of the source material.

The corpus is text-only. Markdown image references are replaced with the
literal marker `[image omitted]`; no image or multimodal training data is
included.
