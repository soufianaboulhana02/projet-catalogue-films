#!/bin/bash

echo "Démarrage de l'architecture microservices (Catalogue Films)..."

# 1. Démarrer Minikube s'il est éteint
minikube status > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "��� Lancement de Minikube..."
    minikube start
fi

# . Builder les images docker 
echo "Build des images de backend et frontend"
docker build -t catalogue-frontend:vf ./frontend
docker build -t catalogue-backend:vf ./backend

# 2. Charger les images locales dans le cluster
echo "Chargement des images Docker (Frontend v9, Backend v9)..."
minikube image load catalogue-frontend:vf
minikube image load catalogue-backend:vf

# 3. Appliquer les configurations Kubernetes
echo "Déploiement des ressources (Pods, Services, PVC)..."
kubectl apply -f k8s/

# 4. Nettoyer les anciens tunnels pour éviter les conflits
echo "Libération des ports réseaux..."
killall kubectl > /dev/null 2>&1

# 5. Attendre que l'application soit prête
echo "Attente du démarrage des conteneurs (Patientez...)"
kubectl wait --for=condition=ready pod -l app=frontend --timeout=90s
kubectl wait --for=condition=ready pod -l app=backend --timeout=90s

# 6. Lancer les tunnels réseaux (Port-Forwarding)
echo "=================================================="
echo "SYSTÈME OPÉRATIONNEL !"
echo "Ouverture des tunnels vers Windows :"
echo "Interface Web (Vue.js) : http://localhost:8080"
echo "Documentation API (Swagger) : http://localhost:8000/docs"
echo "=================================================="
echo "NE FERMEZ PAS CE TERMINAL ! (Ctrl+C pour tout arrêter)"

# Tunnel Backend (En arrière-plan avec &) -> Port 8000
kubectl port-forward --address 0.0.0.0 svc/backend-service 8000:8000 &

# Tunnel Frontend (Au premier plan) -> Port 80
kubectl port-forward --address 0.0.0.0 svc/frontend-service 8080:80
