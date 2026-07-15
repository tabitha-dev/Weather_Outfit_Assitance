# Kubernetes Deployment for A2A Architecture

Deploy the Weather Outfit ADK system as 5 independent microservices on Google Kubernetes Engine (GKE).

## Prerequisites

1. **GKE Cluster**
   ```bash
   gcloud container clusters create weather-outfit-cluster \
     --num-nodes=3 \
     --machine-type=e2-standard-2 \
     --region=us-central1
   ```

2. **Docker Image**
   ```bash
   # Build and push image to GCR
   docker build -t gcr.io/PROJECT_ID/weather-outfit-adk:latest -f deployment/a2a/Dockerfile .
   docker push gcr.io/PROJECT_ID/weather-outfit-adk:latest
   ```

3. **Secrets**
   ```bash
   # Create secret for Weather API key
   kubectl create secret generic weather-api-secret \
     --from-literal=api-key=YOUR_RAPIDAPI_KEY \
     -n weather-outfit
   ```

## Deployment

### Quick Deploy (All Services)

```bash
# Update PROJECT_ID in all YAML files
sed -i 's/PROJECT_ID/your-actual-project-id/g' deployment/a2a/k8s/*.yaml

# Apply all manifests
kubectl apply -f deployment/a2a/k8s/
```

### Step-by-Step Deployment

```bash
# 1. Create namespace
kubectl apply -f namespace.yaml

# 2. Deploy specialist agents (can deploy in parallel)
kubectl apply -f weather-agent.yaml
kubectl apply -f stylist-agent.yaml
kubectl apply -f activity-agent.yaml
kubectl apply -f safety-agent.yaml

# 3. Wait for agents to be ready
kubectl wait --for=condition=ready pod -l service=weather -n weather-outfit --timeout=60s
kubectl wait --for=condition=ready pod -l service=stylist -n weather-outfit --timeout=60s
kubectl wait --for=condition=ready pod -l service=activity -n weather-outfit --timeout=60s
kubectl wait --for=condition=ready pod -l service=safety -n weather-outfit --timeout=60s

# 4. Deploy coach agent (orchestrator)
kubectl apply -f coach-agent.yaml

# 5. Get external IP
kubectl get service coach-agent -n weather-outfit
```

## Verification

```bash
# Check all pods
kubectl get pods -n weather-outfit

# Check services
kubectl get svc -n weather-outfit

# View logs
kubectl logs -f deployment/coach-agent -n weather-outfit
kubectl logs -f deployment/weather-agent -n weather-outfit

# Test agent cards
COACH_IP=$(kubectl get svc coach-agent -n weather-outfit -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
curl http://$COACH_IP:8000/.well-known/agent.json
```

## Scaling

```bash
# Scale coach agent (main entry point)
kubectl scale deployment coach-agent --replicas=5 -n weather-outfit

# Scale weather agent (handles forecast requests)
kubectl scale deployment weather-agent --replicas=3 -n weather-outfit

# Scale stylist agent
kubectl scale deployment stylist-agent --replicas=2 -n weather-outfit
```

## Monitoring

```bash
# Resource usage
kubectl top pods -n weather-outfit

# Service endpoints
kubectl describe svc coach-agent -n weather-outfit
```

## Cleanup

```bash
# Delete all resources
kubectl delete namespace weather-outfit

# Or delete individually
kubectl delete -f deployment/a2a/k8s/
```

## Notes

- **LoadBalancer**: Coach service is exposed via LoadBalancer (gets external IP)
- **ClusterIP**: Specialist agents use ClusterIP (internal only)
- **Health Checks**: All deployments have liveness and readiness probes
- **Auto-scaling**: Add HPA (Horizontal Pod Autoscaler) for production
- **Secrets**: Store API keys in Kubernetes secrets
- **Resource Limits**: Configured for e2-standard-2 nodes, adjust as needed
