#!/bin/bash

echo "🚀 Deploying Kubernetes Data Pipeline..."

# Create namespace
echo "Creating namespace..."
kubectl apply -f k8s/namespace.yaml

# Apply ConfigMap and Secret
echo "Creating ConfigMap and Secret..."
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml

# Deploy data-aggregator first (dependency)
echo "Deploying data-aggregator..."
kubectl apply -f k8s/data-aggregator.yaml

# Wait for aggregator to be ready
echo "Waiting for data-aggregator to be ready..."
kubectl wait --for=condition=available --timeout=60s deployment/data-aggregator -n data-pipeline

# Deploy data-processor
echo "Deploying data-processor..."
kubectl apply -f k8s/data-processor.yaml

# Wait for processor to be ready
echo "Waiting for data-processor to be ready..."
kubectl wait --for=condition=available --timeout=60s deployment/data-processor -n data-pipeline

# Deploy data-generator
echo "Deploying data-generator..."
kubectl apply -f k8s/data-generator.yaml

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📊 Checking deployment status..."
kubectl get all -n data-pipeline
echo ""
echo "🔍 To view logs:"
echo "  kubectl logs -f -l app=data-generator -n data-pipeline"
echo "  kubectl logs -f -l app=data-processor -n data-pipeline"
echo "  kubectl logs -f -l app=data-aggregator -n data-pipeline"
echo ""
echo "📈 To view metrics dashboard:"
echo "  kubectl port-forward -n data-pipeline svc/data-aggregator 8080:8000"
echo "  Then open: http://localhost:8080/metrics/html"
echo ""
echo "🔄 To deploy Argo workflows:"
echo "  ./deploy-argo-workflows.sh"
