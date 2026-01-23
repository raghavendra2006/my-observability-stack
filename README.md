# Kubernetes Observability Stack (Grafana + Loki + Promtail)

This project sets up a **basic Kubernetes observability stack** using **Grafana**, **Loki**, and **Promtail** to collect, store, and query logs from Kubernetes workloads.

If you follow this README step by step, you will end with:

* Grafana UI running locally
* Loki storing logs
* Promtail shipping Kubernetes pod logs to Loki
* Ability to query logs using **LogQL** in Grafana Explore

No magic. No skipped steps.

---

## Architecture Overview

**Flow (simple and correct):**

1. Kubernetes Pods generate logs
2. Promtail runs as a DaemonSet and reads pod logs
3. Promtail sends logs to Loki
4. Loki indexes and stores logs
5. Grafana queries Loki using LogQL

```
Pods → Promtail → Loki → Grafana
```

---

## Prerequisites

You must already have:

* Kubernetes cluster (Minikube / Kind / Docker Desktop / EKS etc.)
* kubectl configured and working
* Helm v3 installed
* Internet access to pull Helm charts

Verify before proceeding:

```bash
kubectl get nodes
helm version
```

If these fail, stop. Fix them first.

---

## Project Structure

```
my-observability-stack/
├── app/
│   ├── Dockerfile
│   ├── app.py
│   ├── requirements.txt
│   └── docker-compose.yml
├── kubernetes/
│   ├── prometheus/
│   │   └── values.yaml  # Or manifests
│   ├── grafana/
│   │   └── dashboards/
│   │       ├── Screenshot.png
│   │       └── Screenshot.png
│   ├── loki/
│   │   └── values.yaml  # Or manifests
│   └── sample-app/
│       ├── deployment.yaml
│       └── service.yaml
|       |__ servicemonitor.yaml
├── alerts/
│   └── app-alerts.yaml
├── README.md

---

## Step 1: Create Namespace

All observability components run in one namespace.

```bash
kubectl create namespace observability
```

Verify:

```bash
kubectl get ns | findstr observability
```

---

## Step 2: Add Grafana Helm Repository

```bash
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update
```

---

## Step 3: Install Loki (with test schema)

Loki **requires a schema configuration**. For learning and local testing, use the test schema.

```bash
helm install loki grafana/loki \
  -n observability \
  --set loki.useTestSchema=true \
  --wait \
  --timeout 10m
```

Verify:

```bash
kubectl get pods -n observability
```

You should see Loki pods in `Running` state.

---

## Step 4: Install Promtail

Promtail collects logs from Kubernetes pods.

```bash
helm install promtail grafana/promtail \
  -n observability \
  --set loki.serviceName=loki \
  --wait
```

Verify:

```bash
kubectl get pods -n observability | findstr promtail
```

Status **must be** `Running`.

---

## Step 5: Install Grafana

```bash
helm install grafana grafana/grafana \
  -n observability \
  --wait
```

---

## Step 6: Access Grafana UI

Port-forward Grafana:

```bash
kubectl port-forward svc/grafana 3000:80 -n observability
```

Open browser:

```
http://localhost:3000
```

### Login Credentials

Get admin password:

```bash
kubectl get secret grafana -n observability -o jsonpath="{.data.admin-password}" | base64 --decode
```

* Username: `admin`
* Password: (decoded value)

---

## Step 7: Verify Loki Data Source

In Grafana:

1. Go to **Connections → Data sources**
2. Open **Loki**
3. Click **Save & Test**

You must see:

```
Data source connected
```

If not, Loki is not reachable.

---

## Step 8: Query Logs Using LogQL

Go to:

```
Explore → Select datasource → Loki
```

### IMPORTANT

Do **NOT** type `LogQL` in the query box.
That is the **language name**, not a query.

---

### Basic Queries (Start Here)

#### 1. All logs

```logql
{job="kubernetes-pods"}
```

#### 2. Logs from a namespace

```logql
{namespace="default"}
```

#### 3. Logs containing a keyword

```logql
{job="kubernetes-pods"} |= "error"
```

---

## Time Range (Very Important)

Grafana defaults to **Last 15 minutes**.

You can change it to:

* `now-1h`
* `now-6h`
* `now-24h`
* Custom absolute times

If you see **no logs**, it is usually because:

* Time range is wrong
* Labels don’t match
* Logs do not exist

Not because Grafana is broken.

---

## Common Problems & Fixes

### 1. No logs returned

Check:

* Promtail pods are running
* Time range is expanded
* Correct labels are used

---

### 2. Promtail stuck in ContainerCreating

Cause:

* Node permissions
* Volume mount issues

Fix:

```bash
kubectl describe pod <promtail-pod> -n observability
```

---

### 3. Loki install fails with schema error

Correct fix (for learning):

```bash
--set loki.useTestSchema=true
```

Production requires **proper schema_config**.

---

## What This Project Is (and Is Not)

✔ Good for:

* Learning observability
* Understanding log pipelines
* Kubernetes debugging

✖ Not for:

* Production use
* Long-term log retention
* High-scale workloads

---

## Next Improvements (If You’re Serious)

1. Configure S3/GCS storage for Loki
2. Set retention policies
3. Add Prometheus + Alertmanager
4. Create Grafana dashboards
5. Enable RBAC and auth

---

## Final Reality Check

If you can:

* Install this stack
* See logs in Grafana
* Write LogQL queries

You are already ahead of most "DevOps beginners".

But this is **step one**, not the finish line.
