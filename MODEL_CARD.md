# Uyghur pretokenized UPOS student

Experiment version 0.1.0. Registered decision: **PASS**.

## Task and architecture

Input: a UTF-8 JSONL object with a pretokenized `tokens` list. Output preserves the list and adds equally long UPOS labels. Character bidirectional GRU + word bidirectional LSTM; CPU inference requires PyTorch only. This model does not perform tokenization.

Frozen configuration: `distilled`. Release weights were chosen by development non-punctuation accuracy before test scoring: `C13`.
SHA-256: `6614613c3d398da75e53a686e9dbf5a64616dd876880102903dca3c29f15cc4b`. Checkpoint size: 14,602,130 bytes.

## Training data and provenance

UD Uyghur-UDT r2.15, commit 77a1c20dae6650284c4c50959833ea2485c5119a: 1,656 train sentences / 19,262 words; 900 development and 900 test sentences. Source authors: Marhaba Eli, Daniel Zeman, Francis Tyers. UPOS annotations are manual/native according to the source metadata; the texts are literature and school reading material.

Fixed public conll17 vectors and Stanza v1.10.0 Uyghur teacher resources are separately attributed. Teacher probability targets, when used, come only from train. Test does not build vocabulary, supply targets, select epochs or choose release weights.

## Frozen test results

| Metric | Stanza baseline | Candidate three-seed mean | Release checkpoint |
| --- | ---: | ---: | ---: |
| overall | 89.690% | 90.103% | 89.903% |
| nonpunct | 87.159% | 87.662% | 87.413% |
| oov | 79.768% | 79.559% | 78.641% |

Raw predictions, sentence-paired bootstrap intervals, every seed and each failed/missing gate are preserved in the final experiment report. A point-estimate PASS does not establish general statistical non-inferiority; crossing intervals must be disclosed.

## Measured CPU behavior

Release p50: 2.782 ms; p95: 4.479 ms; speed ratio vs baseline: 6.031x; median peak RSS: 407,519,232 bytes.
Same machine, CPU-only, one thread, batch=1, alternating model order. Five fresh processes per model measure memory/cold start; the first three full rounds measure latency. Input parsing and output serialization are included. See final report for hardware, variability and raw measurements.

The final resource record is the complete environmental recovery of an interrupted registered repeat. The first complete run was inconclusive; the interrupted run retained 27/35 records. All are preserved. No model, quality prediction, threshold or frozen evaluation code changed, and no best-of-attempt selection was used. CPU affinity was 0; stability CV uses all five process rounds. See reports/P6-interruption-recovery-registration.md.

## Limitations

Small, fiction-oriented evaluation; no validated dialect, speech, OCR or business-domain capability. OOV is defined relative to annotated train even when public vectors cover the word. Possible overlap between external vector pretraining text and evaluation text cannot be independently excluded. No third-party adoption or independent external replication is claimed.

## Licensing and attribution

Original software: MIT. Trained checkpoint distribution: CC BY-SA 4.0 with UD attribution and share-alike notice; Apache-2.0 third-party resource notices are retained. The checkpoint is not covered solely by the code MIT license. See NOTICE.md and licenses/.

## Use

Install the wheel and a supported PyTorch build. Run `uyghur-pos predict --model model.pt` and pipe JSONL input. No network access is required after the weights are available. Empty lists return empty labels; invalid inputs are rejected. Maximum 512 tokens per sentence and 128 Unicode code points per token.
