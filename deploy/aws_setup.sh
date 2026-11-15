#!/usr/bin/env bash
# One-time setup of the AWS EC2 host (Ubuntu 24.04, m7i-flex.large). Stage 7, deploy/AWS_GUIDE.md step 4.
#   bash aws_setup.sh <APP_API_KEY>
# Installs Docker, clones the repo, starts the same Docker Compose stack as design.md §7 (pinned Ollama 0.40.16),
# pulls the cloud models, warms up the D1 detector and writes ~/environment_aws.json for the results folder.
set -euo pipefail
KEY="${1:?usage: bash aws_setup.sh <APP_API_KEY>}"
REPO_URL="https://github.com/MuhammadTalha57/CEP.git"
MODELS="gemma3:1b llama3.2:3b"          # configs/cloud.yaml

echo "== 1/6 swap (4 GB): the image build and a 3B model must fit next to each other in 8 GB RAM"
if ! sudo swapon --show | grep -q /swapfile; then
  sudo fallocate -l 4G /swapfile && sudo chmod 600 /swapfile && sudo mkswap /swapfile >/dev/null && sudo swapon /swapfile
  echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab >/dev/null
fi

echo "== 2/6 Docker + git"
sudo apt-get update -qq
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq docker.io docker-compose-v2 git curl >/dev/null
sudo systemctl enable --now docker

echo "== 3/6 code"
cd ~
if [ -d CEP/.git ]; then git -C CEP pull -q --ff-only; else git clone -q --depth 1 "$REPO_URL" CEP; fi
cd ~/CEP
COMMIT=$(git rev-parse --short HEAD)
TOKEN=$(curl -s -X PUT http://169.254.169.254/latest/api/token -H "X-aws-ec2-metadata-token-ttl-seconds: 300")
md() { curl -s -H "X-aws-ec2-metadata-token: $TOKEN" "http://169.254.169.254/latest/meta-data/$1"; }
ITYPE=$(md instance-type); AZ=$(md placement/availability-zone)
printf 'APP_API_KEY=%s\nSERVER_ENV=aws-ec2-%s\n' "$KEY" "$ITYPE" > .env && chmod 600 .env

echo "== 4/6 build and start the stack (first build takes several minutes)"
sudo docker compose up -d --build

echo "== 5/6 pull models"
for m in $MODELS; do sudo docker compose exec -T ollama ollama pull "$m" | tail -1; done

echo "== 6/6 health + warm-up (loads gemma3 and downloads the D1 detector once)"
for i in $(seq 1 30); do curl -sf localhost:8000/health >/dev/null && break; sleep 2; done
curl -s localhost:8000/health; echo
curl -s -X POST localhost:8000/v1/run -H "X-API-Key: $KEY" -H "Content-Type: application/json" \
  -d '{"model":"gemma3-1b","defense":"layered","seed":0,"request":{"app":"chatbot","user_message":"Hello","lab":{"secret":"ACME-WARM-UP00"}}}' \
  | head -c 400; echo

python3 - "$COMMIT" "$ITYPE" "$AZ" <<'PY' > ~/environment_aws.json
import json, subprocess, sys, time
sh = lambda c: subprocess.run(c, shell=True, capture_output=True, text=True).stdout.strip()
print(json.dumps({
    "env": "aws", "commit": sys.argv[1], "instance_type": sys.argv[2], "availability_zone": sys.argv[3],
    "cpu": sh("lscpu | grep 'Model name' | sed 's/.*: *//'"), "vcpus": sh("nproc"),
    "mem": sh("free -h | awk '/Mem/{print $2}'"), "gpu": "none",
    "ollama": sh("sudo docker compose exec -T ollama ollama --version"),
    "ollama_models": sh("sudo docker compose exec -T ollama ollama list").splitlines(),
    "docker": sh("docker --version"), "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}, indent=2))
PY
cat ~/environment_aws.json
echo "SETUP DONE. Check above: health shows the models, the warm-up returned an 'output', ollama 0.40.16."
