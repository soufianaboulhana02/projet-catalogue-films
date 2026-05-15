#!/bin/bash

set -e  # Arrête le script à la première erreur

echo "Démarrage de l'architecture microservices..."

# 1. Démarrer Minikube si éteint
if ! minikube status > /dev/null 2>&1; then
    echo "Lancement de Minikube..."
    minikube start
fi

# 2. Pointer Docker vers le daemon de minikube
eval $(minikube docker-env)

# 3. Build avec un tag FIXE
TAG="VersionFInal02"
echo "Build des images (tag: ${TAG})..."
docker build -t catalogue-frontend:${TAG} ./frontend
docker build -t catalogue-backend:${TAG} ./backend

# 4. Appliquer les manifests
echo "Déploiement des ressources..."
kubectl apply -f k8s/

# 5. Forcer le redémarrage des deployments pour qu'ils prennent la nouvelle image
echo "Rollout des nouvelles images..."
kubectl rollout restart deployment/frontend
kubectl rollout restart deployment/backend

# 6. Attendre que tout soit prêt
echo "Attente du démarrage..."
kubectl rollout status deployment/frontend --timeout=120s
kubectl rollout status deployment/backend --timeout=120s

# 7. Afficher l'URL d'accès
NODE_IP=$(minikube ip)
NODE_PORT=$(kubectl get svc frontend-service -o jsonpath='{.spec.ports[0].nodePort}')

echo "=================================================="
echo "SYSTÈME OPÉRATIONNEL !"
echo "Interface Web : http://${NODE_IP}:${NODE_PORT}"
echo "=================================================="
