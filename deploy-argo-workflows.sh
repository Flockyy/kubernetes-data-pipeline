#!/bin/bash

echo "🚀 Deploying Argo Workflows..."

# Deploy all workflow definitions
echo "Deploying workflow templates and cron workflows..."

kubectl apply -f argo-workflows/daily-aggregation.yaml
kubectl apply -f argo-workflows/data-quality-check.yaml
kubectl apply -f argo-workflows/batch-reprocessing.yaml

echo ""
echo "✅ Argo workflows deployed successfully!"
echo ""
echo "📋 View all workflows:"
echo "  kubectl get cronworkflows -n data-pipeline"
echo "  kubectl get workflowtemplates -n data-pipeline"
echo ""
echo "🚀 Submit a workflow manually:"
echo "  kubectl create -n data-pipeline -f argo-workflows/batch-reprocessing.yaml"
echo ""
echo "🔍 Watch workflow execution:"
echo "  kubectl get workflows -n data-pipeline -w"
echo ""
echo "📊 View workflow logs:"
echo "  kubectl logs -n data-pipeline -l workflows.argoproj.io/workflow=<workflow-name>"
echo ""
echo "🌐 Access Argo UI:"
echo "  kubectl port-forward -n argo svc/argo-server 2746:2746"
echo "  Then open: https://localhost:2746"
