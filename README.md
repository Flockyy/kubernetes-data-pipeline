./setup-local-dev.sh# Kubernetes Data Engineering Pipeline

A showcase project demonstrating Kubernetes capabilities through a real-time data pipeline.

## Project Overview

This project implements a distributed data pipeline with three microservices:

1. **Data Generator**: Produces streaming event data (user activity logs)
2. **Data Processor**: Processes and transforms the raw events
3. **Data Aggregator**: Aggregates processed data and exposes metrics

## Kubernetes Features Demonstrated

- **Deployments**: Managing stateless applications
- **Services**: Internal communication between pods
- **ConfigMaps**: Configuration management
- **Secrets**: Sensitive data handling
- **Horizontal Pod Autoscaling**: Auto-scaling based on CPU/memory
- **Resource Limits**: CPU and memory constraints
- **Liveness & Readiness Probes**: Health checking
- **Namespaces**: Logical isolation
- **Labels & Selectors**: Resource organization
- **Argo Workflows**: Complex workflow orchestration
- **CronWorkflows**: Scheduled workflow execution
- **WorkflowTemplates**: Reusable workflow components

## Architecture

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│  Data Generator │─────▶│  Data Processor │─────▶│ Data Aggregator │
│   (Producer)    │      │   (Transform)   │      │   (Analytics)   │
└─────────────────┘      └─────────────────┘      └─────────────────┘
```

## Prerequisites

- Docker Desktop with Kubernetes enabled, OR
- Minikube, OR
- Kind (Kubernetes in Docker)
- kubectl CLI tool
- Python 3.9+
- [uv](https://github.com/astral-sh/uv) for fast Python environment management (optional for local dev)

## Quick Start

### 1. Local Development Setup (Optional)

Set up Python environments for local development using uv:

```bash
./setup-local-dev.sh
```

This creates virtual environments for each service and installs dependencies 10-100x faster than pip.

To run services locally:
```bash
# Terminal 1 - Processor (runs on port 8000)
cd data-processor && source .venv/bin/activate && python app.py

# Terminal 2 - Aggregator (runs on port 8000)
cd data-aggregator && source .venv/bin/activate && python app.py

# Terminal 3 - Generator (connects to processor)
cd data-generator && source .venv/bin/activate && python app.py
```

### 2. Build Docker Images

```bash
./build.sh
```

This builds all three microservices using uv for fast dependency installation.

### 3. Deploy to Kubernetes

```bash
./deploy.sh
```

### 4. Check Status

```bash
kubectl get pods -n data-pipeline
kubectl get services -n data-pipeline
```

### 5. View Logs

```bash
# Generator logs
kubectl logs -f -l app=data-generator -n data-pipeline

# Processor logs
kubectl logs -f -l app=data-processor -n data-pipeline

# Aggregator logs
kubectl logs -f -l app=data-aggregator -n data-pipeline
```

### 6. Access Metrics Dashboard

```bash
kubectl port-forward -n data-pipeline svc/data-aggregator 8080:8080
```

Then visit: http://localhost:8080/metrics

### 7. Scale the Pipeline

```bash
# Scale processor to 3 replicas
kubectl scale deployment data-processor -n data-pipeline --replicas=3

# Watch the scaling
kubectl get pods -n data-pipeline -w
```

### 8. Setup Argo Workflows (Optional)

```bash
# Install Argo Workflows
./install-argo.sh

# Deploy workflow definitions
./deploy-argo-workflows.sh

# Access Argo UI
kubectl port-forward -n argo svc/argo-server 2746:2746
# Then open: https://localhost:2746
```

### 8. Cleanup

```bash
./cleanup.sh
```

## Project Structure

```
.
├── README.md
├── build.sh                       # Build all Docker images
├── deploy.sh                      # Deploy to Kubernetes
├── cleanup.sh                     # Remove all resources
├── install-argo.sh                # Install Argo Workflows
├── deploy-argo-workflows.sh       # Deploy workflow definitions
├── data-generator/
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
├── data-processor/
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
├── data-aggregator/
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
├── k8s/
│   ├── namespace.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   ├── data-generator.yaml
│   ├── data-processor.yaml
│   └── data-aggregator.yaml
└── argo-workflows/
    ├── daily-aggregation.yaml      # CronWorkflow: Daily reports
    ├── data-quality-check.yaml     # CronWorkflow: Quality checks
    └── batch-reprocessing.yaml     # WorkflowTemplate: Batch jobs
```

## Testing the Pipeline

### Generate load
```bash
# Watch real-time processing
kubectl logs -f -l app=data-processor -n data-pipeline
```

### Check metrics
```bash
curl http://localhost:8080/metrics
```

## Learning Points

1. Argo Workflows Examples

### View Deployed Workflows
```bash
# List CronWorkflows
kubectl get cronworkflows -n data-pipeline

# List WorkflowTemplates
kubectl get workflowtemplates -n data-pipeline

# Watch active workflows
kubectl get workflows -n data-pipeline -w
```

### Submit Manual Workflow
```bash
# Submit batch reprocessing workflow
kubectl create -n data-pipeline -f - <<EOF
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: batch-reprocess-manual-
  namespace: data-pipeline
spec:
  workflowTemplateRef:
    name: batch-reprocessing
  arguments:
    parameters:
    - name: batch-size
      value: "100"
    - name: parallelism
      value: "3"
EOF
```

### View Workflow Logs
```bash
# Get workflow status
kubectl get workflow -n data-pipeline <workflow-name> -o yaml

# View logs for specific workflow
kubectl logs -n data-pipeline -l workflows.argoproj.io/workflow=<workflow-name>
```

### Workflow Descriptions

1. **daily-aggregation** (CronWorkflow)
   - Runs: Daily at 2 AM
   - Purpose: Generate daily reports and analytics
   - Steps: Fetch metrics → Process data → Generate report → Notify

2. **data-quality-check** (CronWorkflow)
   - Runs: Every 15 minutes
   - Purpose: Validate data quality and pipeline health
   - Checks: Service health, metrics validation, event rates

3. **batch-reprocessing** (WorkflowTemplate)
   - Runs: On-demand
   - Purpose: Reprocess historical data in parallel batches
   - Features: Backup, parallel processing, verification

## Next Steps

- Add persistent storage with PersistentVolumes
- Implement StatefulSets for stateful services
- Add monitoring with Prometheus and Grafana
- Implement ingress for external access
- Add CI/CD pipeline with Argo CD
- Integrate workflow notifications (Slack, email)

- Add persistent storage with PersistentVolumes
- Implement StatefulSets for stateful services
- Add monitoring with Prometheus
- Implement ingress for external access
- Add CI/CD pipeline
