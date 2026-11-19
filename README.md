# Replication Data and Code for: "Reading the Room with AI: FOMC Deliberation and Growth-at-Risk"

This repository contains the replication archive, data artifacts, scripts, and supplementary materials for the manuscript **"Reading the Room with AI: FOMC Deliberation and Growth-at-Risk"**, submitted to the *Journal of Monetary Economics*.

- **Public Repository URL:** https://github.com/Ortiz-BBVAResearch/Reading-the-Room-with-AI-FOMC-Deliberation-and-Growth-at-Risk

---

## Repository Structure

- **`replication/abg_target_correction/`**: Unpacked replication directory for direct browser inspection. Contains the forecast banks, real-time inference outputs, event anatomy, paired horse-race evaluations, structural certifications, and table/figure replication manifests.
- **`replication/ABG_target_correction_replication_archive.zip`**: Standalone compressed archive of the complete replication package.
- **`supplementary/figures/`**: Source data, diagnostic outputs, reproducibility scripts, and figure files corresponding to the manuscript and supplementary appendix.
- **`supplementary/formal_dissents/`**: Descriptive post-design FOMC vote/dissent analysis and accompanying documentation.
- **`manuscript/`**: Submitted manuscript PDF and Supplementary Material PDF provided for reference and reviewer convenience.
- **`SHA256SUMS.txt`**: Cryptographic SHA-256 checksums for all primary archive files to verify file integrity.

---

## Software & Reproducibility Notes

- **Environment:** Python 3.x (`pandas`, `numpy`, `scipy`, `statsmodels`, `matplotlib`).
- **Execution & Auditing:** Individual workstreams inside `replication/abg_target_correction/` and `supplementary/figures/` include self-contained CSV outputs, JSON execution manifests, and scripts used to generate the tables and figures reported in the paper.
- **Integrity Verification:** To verify file checksums locally on macOS/Linux, run:
  ```bash
  shasum -a 256 -c SHA256SUMS.txt
