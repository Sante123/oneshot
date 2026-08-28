#!/usr/bin/env bash
# Install oneshot into your user-level Claude directory.
#
#   ./install.sh                # install to ~/.claude
#   ./install.sh --project      # install to ./.claude
#   ./install.sh --check        # report status only
#   ./install.sh --uninstall    # remove what the installer added
#
# A thin wrapper around install.py. Requires Python 3.8+.
set -euo pipefail

repo="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ ! -f "$repo/install.py" ]]; then
  cat >&2 <<'EOF'
error: install.py not found next to this script.

The repository contents may be nested one level deep. The project root must
directly contain skills/, agents/, commands/ and .claude-plugin/.
EOF
  exit 1
fi

python=""
for candidate in python3 python; do
  if command -v "$candidate" >/dev/null 2>&1; then
    if "$candidate" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)' 2>/dev/null; then
      python="$candidate"
      break
    fi
  fi
done

if [[ -z "$python" ]]; then
  echo "error: Python 3.8 or newer is required and was not found on PATH." >&2
  exit 1
fi

exec "$python" "$repo/install.py" "$@"
