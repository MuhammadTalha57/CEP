# Stage 7: deploy on AWS and compare with Kaggle (exact steps)

**What this does.**
- The three apps run as a **cloud-hosted service** on one EC2 instance. It is the same Docker image and code as on Kaggle, with Ollama pinned to the same version (0.40.16) and the same model files.
- The laptop attacks it over the Internet, through the HTTP API with an API key (black-box), using **the same trials as Kaggle** (same trial ids, seeds and payloads).
- `report.py --compare-env kaggle aws` then pairs every cloud trial with its Kaggle trial.

**Why this instance (costs stay inside the free credits).**
- An AWS account on the **Free plan** may only launch small CPU instances (t3/t4g micro/small, c7i-flex.large, m7i-flex.large). GPU instances (g4dn) are not allowed.
- Free plan accounts are not charged: when the credits run out, the account is closed instead of billed.
- We use **m7i-flex.large** (2 vCPU, 8 GB RAM, no GPU). It is the only allowed type with enough memory for a 3B model plus the D1 detector.
- [INFERENCE] Expected cost: about $0.10 per hour or less (check the price shown on the launch page), plus a few cents for the 30 GB disk and public IP. Under $2 for the whole stage.
- **Do not upgrade the account to the Paid plan.** Only the Paid plan can bill beyond the credits.

**What differs from Kaggle (report it, do not hide it).**
- AWS here is CPU-only (2 vCPU), while Kaggle had a T4 GPU. Latency differences therefore mix *hardware* and *deployment* (network + Docker + HTTP).
- Security outcomes (ASR, utility) should not depend on hardware at temperature 0. Small numeric differences between CPU and GPU can still change some outputs, and the identical-output rate measures exactly that.

**Cloud matrix** (`configs/cloud.yaml`, run in this order, each block resumes):

| block | model | apps | defense | variants | trials | rough time [INFERENCE, not measured] |
|---|---|---|---|---|---|---|
| 1 | gemma3-1b | chatbot, rag | none | 10 | 300 | ~0.5 h |
| 2 | gemma3-1b | chatbot, rag | layered | 10 | 300 | ~0.75 h |
| 3 | llama3.2-3b | agent | none | 5 | 75 | ~0.8 h |
| 4 | llama3.2-3b | agent | layered | 5 | 75 | ~0.9 h |
| 5 | llama3.2-3b | chatbot, rag | none | 10 | 300 | ~2 h |
| 6 | llama3.2-3b | chatbot, rag | layered | 10 | 300 | ~2 h |

Blocks 1–4 are the minimum for the paper: all three apps, with and without the layered defense. Blocks 5–6 are added if time allows. Stopping at any point keeps every finished trial.

---

## Step 1: Safety first (AWS console, 3 min)
1. Sign in at https://console.aws.amazon.com.
2. Top-right search bar: type `Billing` → open **Billing and Cost Management**.
3. Left menu **Credits**: note the remaining credit (about $190).
4. Left menu **Budgets** → **Create budget** → **Use a template** → **Zero spend budget** → enter your email → **Create budget**. You get an email if real money (not credits) is ever charged.

## Step 2: Launch the instance (EC2 console, 5 min)
1. Top-right **region** menu: choose **Asia Pacific (Mumbai) ap-south-1**. It is close to you, so less network delay. If m7i-flex.large is not offered there, use **US East (N. Virginia)**.
2. Search bar: `EC2` → **Instances** → **Launch instances**.
3. **Name**: type `cep-llm-lab`.
4. **Application and OS Images**: **Ubuntu** → **Ubuntu Server 24.04 LTS (HVM), SSD Volume Type** (64-bit x86).
5. **Instance type**: type `m7i-flex.large` and select it.
6. **Key pair** → **Create new key pair**:
   - Name `cep-key`, type **RSA**, format **.pem** → **Create key pair**.
   - The file `cep-key.pem` downloads to `Downloads`.
7. **Network settings** → **Edit**:
   - Auto-assign public IP: **Enable**.
   - Firewall: **Create security group**, name `cep-lab-sg`.
   - The rule `ssh` (TCP 22): set **Source type = My IP**.
   - **Add security group rule**: Type **Custom TCP**, Port range `8000`, Source type **My IP**, Description `lab api`.
   - (Only your own IP can reach the server. If your home IP changes later, edit these two rules back to "My IP".)
8. **Configure storage**: change `8` to **30** GiB, type **gp3**.
9. **Launch instance** → **View all instances**.
10. Wait until **Instance state = Running** and **Status check = 2/2 checks passed** (about 2 min).
11. Click the instance and copy its **Public IPv4 address**. Below it is called `<IP>`.

## Step 3: Make an API key and connect (laptop PowerShell, 2 min)
```powershell
# 1. a random 32-character API key; copy the printed value, it is <KEY> below
-join ((48..57)+(97..122) | Get-Random -Count 32 | ForEach-Object {[char]$_})
# 2. SSH needs the key file to be private
icacls "$HOME\Downloads\cep-key.pem" /inheritance:r /grant:r "$($env:USERNAME):R"
# 3. connect (type "yes" the first time)
ssh -i "$HOME\Downloads\cep-key.pem" ubuntu@<IP>
```

## Step 4: Set up the server (inside the SSH session, about 10 min)
```bash
curl -fsSL https://raw.githubusercontent.com/MuhammadTalha57/CEP/master/deploy/aws_setup.sh -o aws_setup.sh
bash aws_setup.sh <KEY>
```
At the end, check that:
- `/health` lists the models;
- the warm-up printed a JSON with an `"output"`;
- `environment_aws.json` shows `ollama version is 0.40.16`, `m7i-flex.large`, and `gemma3:1b` / `llama3.2:3b` with the **same IDs as Kaggle** (`97558784bdc9`, `a80c4f17acd5`).

Then type `exit`.

## Step 5: Run the cloud matrix from the laptop (PowerShell, hours)
Keep the laptop plugged in and stop it from sleeping: **Settings → System → Power → "When plugged in, put my device to sleep after" → Never**.
```powershell
cd <path-to-your-clone>
git pull origin master
mkdir results\aws -Force
scp -i "$HOME\Downloads\cep-key.pem" ubuntu@<IP>:environment_aws.json results\aws\environment_aws.json
curl.exe http://<IP>:8000/health
$env:APP_API_KEY = "<KEY>"
$env:PYTHONPATH = "src"
.\.venv\Scripts\python -m llmsec.harness.cloud --target http://<IP>:8000
```
- Each block prints `warm-up ...`, then `N to run, M already done`, then progress every 10 trials with the time per trial.
- To pause: **Ctrl+C**. To continue: run the last command again (same PowerShell window, or set the two `$env:` lines again first). Finished trials are skipped.
- If the progress lines show `error=...HTTP 401`, the key differs from the server's. If they show `ConnectError`, check that the instance is running and the 8000 rule is "My IP".

## Step 6: Finish and shut down (AWS console, 2 min)
1. Build the comparison with `python scripts/cloud_compare.py` and `python scripts/make_figures.py`, then commit `results/aws` and the regenerated files.
2. **EC2 → Instances** → select `cep-llm-lab` → **Instance state → Terminate (delete) instance** → confirm. The 30 GB disk is deleted with it.
3. **EC2 → Volumes**: should be empty. **EC2 → Elastic IPs**: should be empty.
4. **Billing → Credits**: the used amount should be a few dollars at most.

Stopping instead of terminating also stops compute charges but keeps the disk (about $2.40 per month). Terminate once the results are committed.
