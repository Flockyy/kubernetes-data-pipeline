#!/bin/bash

echo "🔧 Installing Argo Workflows..."

# Install Argo Workflows
echo "Creating argo namespace and installing Argo Workflows..."
kubectl create namespace argo 2>/dev/null || echo "Namespace argo already exists"

kubectl apply -n argo -f https://github.com/argoproj/argo-workflows/releases/download/v3.5.4/install.yaml

echo "Waiting for Argo Workflows to be ready..."
kubectl wait --for=condition=available --timeout=120s deployment/argo-server -n argo
kubectl wait --for=condition=available --timeout=120s deployment/workflow-controller -n argo

# Patch argo-server to run in server mode (no auth for demo)
echo "Configuring Argo Server for demo access..."
kubectl patch deployment argo-server -n argo --type='json' -p='[{"op": "replace", "path": "/spec/template/spec/containers/0/args", "value": ["server", "--auth-mode=server"]}]'

echo "Waiting for patched argo-server to be ready..."
sleep 5
kubectl wait --for=condition=available --timeout=60s deployment/argo-server -n argo

# Create service account for workflows in data-pipeline namespace
echo "Creating service account for workflows..."
kubectl create sa workflow-executor -n data-pipeline 2>/dev/null || echo "Service account already exists"

# Create role and rolebinding for workflow execution
kubectl apply -f - <<EOF
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: workflow-role
  namespace: data-pipeline
rules:
- apiGroups: [""]
  resources: ["pods", "pods/log", "services"]
  verbs: ["get", "list", "watch", "create", "delete"]
- apiGroups: [""]
  resources: ["configmaps"]
  verbs: ["get", "list", "watch", "create", "update", "patch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: workflow-rolebinding
  namespace: data-pipeline
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: workflow-role
subjects:
- kind: ServiceAccount
  name: workflow-executor
  namespace: data-pipeline
EOF

echo ""
echo "✅ Argo Workflows installed successfully!"
echo ""
echo "📊 Check Argo components:"
echo "  kubectl get pods -n argo"
echo ""
echo "🌐 Access Argo UI:"
echo "  kubectl port-forward -n argo svc/argo-server 2746:2746"
echo "  Then open: https://localhost:2746"
echo ""
echo "📝 Submit a workflow:"
echo "  kubectl apply -f argo-workflows/daily-aggregation.yaml"
echo ""
echo "🔍 Watch workflows:"
echo "  kubectl get workflows -n data-pipeline"
