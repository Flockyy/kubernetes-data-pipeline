# Argo Workflows Quick Reference

## Access Argo UI

```bash
kubectl port-forward -n argo svc/argo-server 2746:2746
```
Then open: https://localhost:2746

## View Workflows

```bash
# List all CronWorkflows
kubectl get cronworkflows -n data-pipeline

# List all WorkflowTemplates
kubectl get workflowtemplates -n data-pipeline

# List active/recent workflows
kubectl get workflows -n data-pipeline

# Watch workflows in real-time
kubectl get workflows -n data-pipeline -w
```

## Submit Workflows

### Daily Aggregation (runs automatically at 2 AM)
```bash
# Trigger manually
kubectl create -n data-pipeline -f - <<EOF
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: daily-agg-manual-
spec:
  workflowTemplateRef:
    name: daily-aggregation
EOF
```

### Data Quality Check (runs every 15 minutes)
```bash
# Trigger manually
kubectl create -n data-pipeline -f - <<EOF
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: quality-check-manual-
spec:
  workflowTemplateRef:
    name: data-quality-check
EOF
```

### Batch Reprocessing (on-demand)
```bash
# Default batch size (100 records per batch)
kubectl create -n data-pipeline -f - <<EOF
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: batch-reprocess-
spec:
  workflowTemplateRef:
    name: batch-reprocessing
  arguments:
    parameters:
    - name: batch-size
      value: "100"
EOF
```

```bash
# Custom batch size
kubectl create -n data-pipeline -f - <<EOF
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: batch-reprocess-
spec:
  workflowTemplateRef:
    name: batch-reprocessing
  arguments:
    parameters:
    - name: batch-size
      value: "50"
EOF
```

## Monitor Workflows

### Get workflow status
```bash
WORKFLOW_NAME=<workflow-name>
kubectl get workflow -n data-pipeline $WORKFLOW_NAME
```

### View workflow details
```bash
kubectl get workflow -n data-pipeline $WORKFLOW_NAME -o yaml
```

### View workflow logs
```bash
# All logs
kubectl logs -n data-pipeline -l workflows.argoproj.io/workflow=$WORKFLOW_NAME --all-containers

# Specific step
kubectl logs -n data-pipeline $WORKFLOW_NAME-<step-name>-<hash> main
```

### View workflow in UI
```bash
# Port forward (if not already running)
kubectl port-forward -n argo svc/argo-server 2746:2746

# Open browser to https://localhost:2746
# Navigate to the workflow
```

## Manage CronWorkflows

### Suspend a CronWorkflow (stop automatic execution)
```bash
kubectl patch cronworkflow data-quality-check -n data-pipeline -p '{"spec":{"suspend":true}}'
```

### Resume a CronWorkflow
```bash
kubectl patch cronworkflow data-quality-check -n data-pipeline -p '{"spec":{"suspend":false}}'
```

### Change schedule
```bash
kubectl patch cronworkflow daily-aggregation -n data-pipeline --type merge -p '{"spec":{"schedule":"0 3 * * *"}}'
```

## Delete Workflows

### Delete a specific workflow
```bash
kubectl delete workflow -n data-pipeline $WORKFLOW_NAME
```

### Delete all completed workflows
```bash
kubectl delete workflows -n data-pipeline --field-selector status.phase=Succeeded
kubectl delete workflows -n data-pipeline --field-selector status.phase=Failed
```

### Delete all workflows
```bash
kubectl delete workflows -n data-pipeline --all
```

## Troubleshooting

### Workflow stuck or not starting
```bash
# Check workflow controller logs
kubectl logs -n argo -l app=workflow-controller

# Check Argo server logs
kubectl logs -n argo -l app=argo-server
```

### Permission errors
```bash
# Check service account
kubectl get sa workflow-executor -n data-pipeline

# Check role bindings
kubectl get rolebinding -n data-pipeline

# View role permissions
kubectl get role workflow-role -n data-pipeline -o yaml
```

### View failed step logs
```bash
# List all pods for the workflow
kubectl get pods -n data-pipeline -l workflows.argoproj.io/workflow=$WORKFLOW_NAME

# Get logs from failed pod
kubectl logs -n data-pipeline <pod-name> main
```

## Workflow Metrics

### Count workflows by status
```bash
kubectl get workflows -n data-pipeline -o json | jq '.items | group_by(.status.phase) | map({phase: .[0].status.phase, count: length})'
```

### List recent workflow executions
```bash
kubectl get workflows -n data-pipeline --sort-by=.status.startedAt
```

### Get workflow execution times
```bash
kubectl get workflows -n data-pipeline -o custom-columns=NAME:.metadata.name,STATUS:.status.phase,DURATION:.status.estimatedDuration
```

## Best Practices

1. **Use meaningful names**: Use `generateName` with descriptive prefixes
2. **Set resource limits**: Define CPU/memory limits in workflow templates
3. **Add timeouts**: Set `activeDeadlineSeconds` to prevent stuck workflows
4. **Clean up old workflows**: Regularly delete completed workflows
5. **Monitor failures**: Set up alerts for failed workflows
6. **Use parameters**: Make workflows flexible with input parameters
7. **Test locally**: Test workflow logic before deploying to production
