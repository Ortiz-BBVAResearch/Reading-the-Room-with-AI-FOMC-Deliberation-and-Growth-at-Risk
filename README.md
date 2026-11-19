# JME data repository deposit — staging folder

This folder assembles the submitted manuscript and Supplementary Material with the available replication archive and selected supplementary result files. It is a **local deposit candidate**, not a published repository. No DOI or public URL has been created; do not enter a fabricated URL in the JME form.

## Contents

- `manuscript/`: the final manuscript PDF and Supplementary Material PDF supplied for this task.
- `replication/`: the existing ABG target-correction replication archive (ZIP). It contains forecast banks, manifests and analysis artifacts from that workstream.
- `supplementary/figures/`: figure source data, diagnostics, reproducibility script and figure files from the pre-submission bundle.
- `supplementary/pre_submission/`: pre-submission calculations, tables, code and manifests selected from the JME closeout bundle.
- `supplementary/formal_dissents/`: descriptive post-design vote results and their limitation note, included as supplementary supporting results.

## Before public deposit

1. Confirm the journal permits the manuscript PDF to be included in the data deposit; the two PDFs are here for convenient review and need not be part of the public dataset.
2. Audit that the archive covers the exact submitted manuscript and supplementary tables, and that any referenced external/private data are documented without redistributing restricted source files.
3. Add a top-level data/code guide with software versions and execution commands for the full analyses. The current folder stages the artifacts; it does not claim that every result can be regenerated from this folder alone.
4. Deposit the approved package in a public repository, make it public, then replace the URL placeholder in `JME_FORM_FIELDS.md` with the repository's persistent HTTPS landing-page URL.
5. Recreate the ZIP after any edits and retain its checksum.

The repository URL must be public and start with `https://` before it is entered into the journal system.
