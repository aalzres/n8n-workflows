---
title: "Runbook: Despliegue Kubernetes"
status: approved
tags: [operations, kubernetes, deployment, helm]
created: 2026-02-21
updated: 2026-02-21
---

# Runbook: Despliegue Kubernetes

## Pre-requisitos

- `kubectl` configurado con acceso al cluster
- `helm` v3+ instalado
- Namespace `n8n-workflows` creado o permisos para crearlo
- Secret con `JWT_SECRET_KEY` creado en el namespace

---

## Estructura de Manifests

```
k8s/
├── namespace.yaml   → Namespace y etiquetas
├── configmap.yaml   → Variables no sensibles
├── deployment.yaml  → Deployment con replicas, probes, resources
├── service.yaml     → ClusterIP en puerto 8000
└── ingress.yaml     → Ingress con TLS (cert-manager)
```

---

## Procedimientos

### P1: Despliegue Inicial con kubectl

```bash
# 1. Crear namespace
kubectl apply -f k8s/namespace.yaml

# 2. Crear secret con JWT key (NO añadir este comando al control de versiones)
kubectl create secret generic api-secrets \
  --namespace n8n-workflows \
  --from-literal=JWT_SECRET_KEY="tu-clave-secreta"

# 3. Apply configmap
kubectl apply -f k8s/configmap.yaml

# 4. Deploy aplicación
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml

# 5. Verificar pods
kubectl get pods -n n8n-workflows

# 6. Esperar a que estén Running
kubectl wait --for=condition=Ready pod -l app=n8n-workflows-docs -n n8n-workflows --timeout=120s

# 7. Indexar workflows
kubectl exec -n n8n-workflows deploy/n8n-workflows-docs -- \
  curl -X POST http://localhost:8000/api/workflows/index
```

---

### P2: Despliegue con Helm

```bash
# 1. Instalar
helm install workflows-docs ./helm/workflows-docs/ \
  --namespace n8n-workflows \
  --create-namespace \
  --set image.tag=latest \
  --set secret.jwtSecretKey="tu-clave-secreta"

# 2. Verificar
helm status workflows-docs -n n8n-workflows

# 3. Ver pods
kubectl get pods -n n8n-workflows
```

---

### P3: Actualizar versión

```bash
# Con kubectl
kubectl set image deployment/n8n-workflows-docs \
  app=workflows-doc:v2.1.0 \
  -n n8n-workflows

# Monitorear rollout
kubectl rollout status deployment/n8n-workflows-docs -n n8n-workflows

# Con Helm
helm upgrade workflows-docs ./helm/workflows-docs/ \
  --namespace n8n-workflows \
  --set image.tag=v2.1.0
```

---

### P4: Rollback

```bash
# Ver historial de rollouts
kubectl rollout history deployment/n8n-workflows-docs -n n8n-workflows

# Rollback a versión anterior
kubectl rollout undo deployment/n8n-workflows-docs -n n8n-workflows

# Rollback a versión específica
kubectl rollout undo deployment/n8n-workflows-docs -n n8n-workflows --to-revision=2

# Con Helm
helm rollback workflows-docs 1 -n n8n-workflows
```

---

### P5: Diagnóstico en K8s

```bash
# Ver pods
kubectl get pods -n n8n-workflows

# Ver logs
kubectl logs -n n8n-workflows -l app=n8n-workflows-docs --tail=50

# Describir pod (ver eventos, probes)
kubectl describe pod -n n8n-workflows -l app=n8n-workflows-docs

# Exec en pod
kubectl exec -it -n n8n-workflows deploy/n8n-workflows-docs -- /bin/sh

# Port-forward para testing local
kubectl port-forward -n n8n-workflows svc/n8n-workflows-docs 8080:8000
curl http://localhost:8080/health
```

---

### P6: Escalar horizontalmente

```bash
# Manual
kubectl scale deployment n8n-workflows-docs --replicas=3 -n n8n-workflows

# HPA (autoescalado)
kubectl autoscale deployment n8n-workflows-docs \
  --min=2 --max=5 --cpu-percent=70 \
  -n n8n-workflows
```

> ⚠️ **IMPORTANTE**: Al escalar horizontalmente, asegurarse de que todos los pods comparten el mismo `JWT_SECRET_KEY` y tienen acceso al mismo volumen de base de datos (o migrar a PostgreSQL).

---

## Verificación Post-Despliegue

```bash
# Desde dentro del cluster
kubectl exec -n n8n-workflows deploy/n8n-workflows-docs -- \
  curl -s http://localhost:8000/api/stats

# Desde exterior (con ingress configurado)
curl https://workflows.tudominio.com/health
```
