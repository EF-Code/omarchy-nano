# Evaluation

`results.json` records the metrics from the completed Colab run. The reported
evaluation loss is measured on 37 held-out examples selected at the document
level. It is useful for tracking optimization, but it is not evidence that the
model gives safe or correct shell commands.

Future evaluations should add a fixed, separately authored prompt set with
expected answers and command-safety checks. Keep those results separate from
training loss so the two measurements are not confused.
