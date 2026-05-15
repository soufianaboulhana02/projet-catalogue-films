# --- ÉTAPE 1 : La compilation (Build) ---
# On utilise Node.js pour installer les paquets et compiler le code
FROM node:20 AS build-stage

WORKDIR /app

# On copie d'abord les fichiers de configuration (pour utiliser le cache Docker)
COPY package*.json ./
RUN npm install

# On copie le reste du code et on lance la compilation finale
COPY . .
RUN npm run build

# --- ÉTAPE 2 : Le serveur Web (Production) ---
# On utilise Nginx, un serveur web ultra-léger et très performant
FROM nginx:alpine

# On récupère UNIQUEMENT le code compilé de l'étape 1 (le dossier /dist)
COPY --from=build-stage /app/dist /usr/share/nginx/html

# On expose le port standard du web (80)
EXPOSE 80

# On lance Nginx
CMD ["nginx", "-g", "daemon off;"]
