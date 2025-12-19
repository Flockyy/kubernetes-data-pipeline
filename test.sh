#!/bin/bash

# Kubernetes Data Pipeline - Quick Testing Guide
# Run this script to test all components

echo "🧪 KUBERNETES DATA PIPELINE TESTING"
echo "===================================="
echo ""

# Test 1: Check if everything is running
echo "TEST 1: Pod Status"
echo "-------------------"
kubectl get pods -n data-pipeline | grep -E "NAME|data-generator|data-processor|data-aggregator"
echo ""
read -p "Press Enter to continue..."

# Test 2: View live event generation
echo ""
echo "TEST 2: Live Event Generation (Ctrl+C to stop)"
echo "------------------------------------------------"
kubectl logs -f -l app=data-generator -n data-pipeline --tail=10
echo ""

# Test 3: Check metrics
echo ""
echo "TEST 3: Current Metrics"
echo "-----------------------"
kubectl run metrics-test --image=curlimages/curl:latest --rm -i --restart=Never -n data-pipeline -- \
  curl -s http://data-aggregator:8000/metrics 2>/dev/null | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f\"Total Events:    {data['total_events']:,}\")
print(f\"Active Users:    {data['active_users']:,}\")
print(f\"Total Revenue:   \${data['purchases']['total_revenue']:,.2f}\")
print(f\"Purchase Count:  {data['purchases']['count']:,}\")
print(f\"Last Update:     {data['last_update']}\")
"
echo ""
read -p "Press Enter to continue..."

# Test 4: Health checks
echo ""
echo "TEST 4: Service Health Checks"
echo "-------------------------------"
kubectl run health-test --image=curlimages/curl:latest --rm -i --restart=Never -n data-pipeline -- \
  sh -c "echo 'Aggregator:' && curl -s http://data-aggregator:8000/health && echo '' && echo 'Processor:' && curl -s http://data-processor:8000/health" 2>/dev/null
echo ""
read -p "Press Enter to continue..."

# Test 5: Check Argo workflows
echo ""
echo "TEST 5: Argo Workflows Status"
echo "-------------------------------"
echo "Installed Workflows:"
kubectl get cronworkflows,workflowtemplates -n data-pipeline
echo ""
echo "Recent Workflow Runs:"
kubectl get workflows -n data-pipeline --sort-by=.status.finishedAt | tail -5
echo ""
read -p "Press Enter to continue..."

# Test 6: Submit test workflow
echo ""
echo "TEST 6: Submit Test Batch Workflow"
echo "------------------------------------"
read -p "Do you want to submit a test batch reprocessing workflow? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    kubectl create -n data-pipeline -f - <<'EOF'
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: manual-test-
  namespace: data-pipeline
spec:
  workflowTemplateRef:
    name: batch-reprocessing
  arguments:
    parameters:
    - name: batch-size
      value: "50"
EOF
    echo ""
    echo "Workflow submitted! Monitor with:"
    echo "  kubectl get workflows -n data-pipeline -w"
fi

echo ""
echo "============================================"
echo "         TESTING COMPLETE ✅"
echo "============================================"
echo ""
echo "📊 To view dashboards:"
echo ""
echo "1. Metrics Dashboard:"
echo "   kubectl port-forward -n data-pipeline svc/data-aggregator 8080:8000"
echo "   Open: http://localhost:8080/metrics/html"
echo ""
echo "2. Argo Workflows UI:"
echo "   kubectl port-forward -n argo svc/argo-server 2746:2746"
echo "   Open: https://localhost:2746"
echo ""
