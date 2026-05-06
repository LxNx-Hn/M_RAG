#!/usr/bin/env bash
# Pull experiment results from Alice to local and archive by timestamp.
#
# Usage:
#   bash backend/scripts/pull_alice_results.sh <PEM_PATH> <HOST> <PORT> [LABEL]
#
# Example:
#   bash backend/scripts/pull_alice_results.sh \
#     ~/Downloads/OLD_ALICE_KEY_REDACTED.pem \
#     OLD_ALICE_HOST_REDACTED OLD_ALICE_PORT_REDACTED
#
# Pulled files:
#   - evaluation/results/*.json       (table1/2/3 ablation results)
#   - evaluation/data/pseudo_gt_track1.json
#   - evaluation/data/pseudo_gt_track2.json
#   - evaluation/data/track1_queries.json
#   - scripts/master_run.log
#
# All files are copied to:
#   1. Their canonical paths under backend/ (overwrites, for git commit)
#   2. backend/evaluation/archive/<TIMESTAMP>_<LABEL>/ (immutable snapshot)

set -euo pipefail

PEM="${1:?Usage: $0 <pem_path> <host> <port> [label]}"
HOST="${2:?}"
PORT="${3:?}"
LABEL="${4:-run}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="${SCRIPT_DIR}/.."
REMOTE="elicer@${HOST}"
REMOTE_BASE="~/M_RAG/backend"

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
ARCHIVE_DIR="${BACKEND_DIR}/evaluation/archive/${TIMESTAMP}_${LABEL}"
mkdir -p "${ARCHIVE_DIR}"

SSH_OPTS="-i ${PEM} -o StrictHostKeyChecking=no -p ${PORT}"

pull_file() {
    local remote_path="$1"
    local local_path="${BACKEND_DIR}/$2"
    local archive_path="${ARCHIVE_DIR}/$2"

    mkdir -p "$(dirname "${archive_path}")"
    mkdir -p "$(dirname "${local_path}")"

    echo -n "  pulling $2 ... "
    if scp ${SSH_OPTS} "${REMOTE}:${REMOTE_BASE}/${remote_path}" "${local_path}" 2>/dev/null; then
        cp "${local_path}" "${archive_path}"
        echo "OK"
    else
        echo "SKIP (not found on remote)"
    fi
}

echo "========================================"
echo "Alice → Local pull  [${TIMESTAMP}_${LABEL}]"
echo "  remote: ${REMOTE}:${PORT}"
echo "  archive: evaluation/archive/${TIMESTAMP}_${LABEL}/"
echo "========================================"

# Experiment results
pull_file "evaluation/results/table1_track1.json"  "evaluation/results/table1_track1.json"
pull_file "evaluation/results/table2_decoder.json" "evaluation/results/table2_decoder.json"
pull_file "evaluation/results/table2_alpha.json"   "evaluation/results/table2_alpha.json"
pull_file "evaluation/results/table2_beta.json"    "evaluation/results/table2_beta.json"
pull_file "evaluation/results/table3_domain.json"  "evaluation/results/table3_domain.json"

# GT and query files
pull_file "evaluation/data/pseudo_gt_track1.json"  "evaluation/data/pseudo_gt_track1.json"
pull_file "evaluation/data/pseudo_gt_track2.json"  "evaluation/data/pseudo_gt_track2.json"
pull_file "evaluation/data/track1_queries.json"    "evaluation/data/track1_queries.json"

# Log (gitignored but useful for debugging)
pull_file "scripts/master_run.log" "evaluation/archive/${TIMESTAMP}_${LABEL}/master_run.log"
# Also keep a local copy outside archive for convenience
scp ${SSH_OPTS} "${REMOTE}:${REMOTE_BASE}/scripts/master_run.log" \
    "${BACKEND_DIR}/scripts/master_run.log" 2>/dev/null && echo "  master_run.log → scripts/master_run.log (local copy)" || true

echo ""
echo "Archive saved to: backend/evaluation/archive/${TIMESTAMP}_${LABEL}/"
echo ""
echo "Next steps:"
echo "  cd $(dirname ${BACKEND_DIR})"
echo "  git add backend/evaluation/data/pseudo_gt_track*.json backend/evaluation/results/"
echo "  git commit -m 'results: ${TIMESTAMP} ${LABEL}'"
echo "  git push"
