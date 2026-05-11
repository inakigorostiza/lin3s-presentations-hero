#!/usr/bin/env bash
# Build the .skill file from source.
#
# Requires:
#   - Python 3.8+
#   - Anthropic's skill-creator scripts available at the path in SKILL_CREATOR
#
# Usage:
#   bash scripts/build.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILL_DIR="${REPO_ROOT}/skill"
OUTPUT_DIR="${REPO_ROOT}"
SKILL_CREATOR="${SKILL_CREATOR:-/mnt/skills/examples/skill-creator}"

if [ ! -d "${SKILL_DIR}" ]; then
    echo "Error: skill directory not found at ${SKILL_DIR}" >&2
    exit 1
fi

if [ ! -d "${SKILL_CREATOR}" ]; then
    echo "Error: skill-creator not found at ${SKILL_CREATOR}" >&2
    echo "Set the SKILL_CREATOR environment variable to its location." >&2
    exit 1
fi

# The skill-creator package_skill script expects the skill folder name to
# match the YAML `name` field. Our skill folder is named `skill/` for repo
# clarity, so we copy to a staging location with the correct name.
STAGING_DIR=$(mktemp -d)
SKILL_NAME=$(grep -m1 '^name:' "${SKILL_DIR}/SKILL.md" | sed 's/^name: *//')
STAGING_SKILL="${STAGING_DIR}/${SKILL_NAME}"
cp -r "${SKILL_DIR}" "${STAGING_SKILL}"

echo "Packaging skill from ${STAGING_SKILL}"
echo "Output directory: ${OUTPUT_DIR}"

cd "${SKILL_CREATOR}"
python -c "
import sys
sys.path.insert(0, '${SKILL_CREATOR}')
from scripts.package_skill import package_skill
package_skill('${STAGING_SKILL}', output_dir='${OUTPUT_DIR}')
"

# Cleanup
rm -rf "${STAGING_DIR}"

echo ""
echo "Done. The .skill file is in ${OUTPUT_DIR}/${SKILL_NAME}.skill"
