#!/usr/bin/env bash
# Install the persistent abc proof-attempt fleet on Ubuntu 24.04 (Oracle
# Always Free Ampere A1, 4 OCPU / 24 GB).  No API keys are included here.
set -euo pipefail

REPO="${REPO:-https://github.com/kortana78/axiom.git}"
AXIOM_DIR="${AXIOM_DIR:-/opt/axiom}"
USER_NAME="${USER_NAME:-ubuntu}"
BRANCH="${BRANCH:-main}"
MATHLIB_REV="${MATHLIB_REV:-cf28751adfc7f48c0f7c6c0954a61c38cd957439}"
ENV_FILE="/etc/axiom/abc-prover.env"
HOME_DIR="$(getent passwd "$USER_NAME" | cut -d: -f6)"
MATHLIB_DIR="${MATHLIB_DIR:-$HOME_DIR/mathlib4}"
WORKERS="${ABC_PROVER_WORKERS:-3}"

if [ "$(id -u)" -ne 0 ]; then
  echo "run with sudo: sudo bash install.sh" >&2
  exit 1
fi

echo "==> system packages"
apt-get update -qq
apt-get install -y -qq python3-venv python3-pip git curl ca-certificates build-essential

echo "==> repository"
if [ ! -d "$AXIOM_DIR/.git" ]; then
  git clone "$REPO" "$AXIOM_DIR"
fi
git -C "$AXIOM_DIR" fetch origin "$BRANCH"
git -C "$AXIOM_DIR" checkout "$BRANCH"
git -C "$AXIOM_DIR" pull --ff-only

echo "==> python environment"
python3 -m venv "$AXIOM_DIR/.venv"
"$AXIOM_DIR/.venv/bin/pip" install -q --upgrade pip
"$AXIOM_DIR/.venv/bin/pip" install -q -r "$AXIOM_DIR/requirements.txt"

echo "==> elan / lake (as $USER_NAME)"
if [ ! -x "$HOME_DIR/.elan/bin/lake" ]; then
  sudo -u "$USER_NAME" bash -c \
    'curl -sSfL https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y --default-toolchain none'
fi

echo "==> pinned Mathlib"
if [ ! -d "$MATHLIB_DIR/.git" ]; then
  sudo -u "$USER_NAME" git clone https://github.com/leanprover-community/mathlib4 "$MATHLIB_DIR"
fi
sudo -u "$USER_NAME" git -C "$MATHLIB_DIR" fetch --depth 1 origin "$MATHLIB_REV"
sudo -u "$USER_NAME" git -C "$MATHLIB_DIR" checkout --detach FETCH_HEAD
sudo -u "$USER_NAME" env PATH="$HOME_DIR/.elan/bin:$PATH" \
  bash -c "cd '$MATHLIB_DIR' && lake exe cache get"

echo "==> secrets template"
mkdir -p /etc/axiom
if [ ! -f "$ENV_FILE" ]; then
  cp "$AXIOM_DIR/deploy/oracle/abc-prover.env.example" "$ENV_FILE"
  sed -i "s#AXIOM_MATHLIB=.*#AXIOM_MATHLIB=$MATHLIB_DIR#" "$ENV_FILE"
  sed -i "s#^ABC_PROVER_WORKERS=.*#ABC_PROVER_WORKERS=$WORKERS#" "$ENV_FILE"
  chmod 600 "$ENV_FILE"
  echo "EDIT $ENV_FILE: replace REPLACE_ME with free-tier keys."
fi

echo "==> systemd units"
cp "$AXIOM_DIR/deploy/oracle/axiom-abc-prover.service" /etc/systemd/system/
cp "$AXIOM_DIR/deploy/oracle/axiom-abc-sync.service" /etc/systemd/system/
cp "$AXIOM_DIR/deploy/oracle/axiom-abc-sync.timer" /etc/systemd/system/
chown -R "$USER_NAME":"$USER_NAME" "$AXIOM_DIR" "$MATHLIB_DIR"
systemctl daemon-reload
systemctl enable --now axiom-abc-prover.service
systemctl enable --now axiom-abc-sync.timer

echo "==> status"
sleep 5
"$AXIOM_DIR/.venv/bin/python" -m axiom.abc_prover.supervisor \
  --root "$AXIOM_DIR" --status results/abc_prover/supervisor.json --health || true
systemctl --no-pager status axiom-abc-prover.service | head -20 || true
echo "Installed. Edit $ENV_FILE then: systemctl restart axiom-abc-prover"
