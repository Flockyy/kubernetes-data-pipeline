#!/bin/bash

echo "🧹 Cleaning up Kubernetes Data Pipeline..."

# Delete all resources in namespace
echo "Deleting all resources in data-pipeline namespace..."
kubectl delete namespace data-pipeline

# Optionally delete Argo Workflows
read -p "Do you want to delete Argo Workflows? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo "Deleting Argo Workflows..."
    kubectl delete namespace argo
fi

echo ""
echo "✅ Cleanup complete!"
echo ""
echo "To verify cleanup:"
echo "  kubectl get all -n data-pipeline"
echo "  kubectl get all -n argo"
