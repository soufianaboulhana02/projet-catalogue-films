<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const movies = ref([])
const searchQuery = ref('') 
const errorMessage = ref('') 
const currentPage = ref(1)
const isLoading = ref(false)

const loadMovies = async (isNewSearch = false) => {
  errorMessage.value = ''
  isLoading.value = true
  
  if (isNewSearch) {
    currentPage.value = 1
    movies.value = []
  }

  try {
    let url = ''
    if (searchQuery.value) {
      url = `http://localhost:8000/movies/search?query=${searchQuery.value}&page=${currentPage.value}`
    } else {
      url = `http://localhost:8000/movies/popular?page=${currentPage.value}`
    }

    const response = await axios.get(url)
    
    if (response.data.results.length === 0 && isNewSearch) {
      errorMessage.value = `Aucun film trouvé pour : "${searchQuery.value}"`
    } else {
      movies.value = [...movies.value, ...response.data.results]
    }
  } catch (error) {
    errorMessage.value = "Une erreur est survenue pendant la recherche."
    console.error(error)
  } finally {
    isLoading.value = false
  }
}

const loadMore = () => {
  currentPage.value++
  loadMovies(false)
}

const addToFavorites = async (movie) => {
  try {
    const payload = {
      tmdb_id: movie.id, title: movie.title, poster_path: movie.poster_path
    }
    await axios.post('http://localhost:8000/favorites', payload)
    alert(`"${movie.title}" ajouté aux favoris !`)
  } catch (error) {
    if (error.response && error.response.status === 400) {
      alert(`Ce film est déjà dans tes favoris.`)
    } else {
      alert("Une erreur est survenue.")
    }
  }
}

onMounted(() => {
  loadMovies(true)
})
</script>

<template>
  <div class="app-wrapper">
    <!-- Ambient background blobs -->
    <div class="bg-blob blob-1"></div>
    <div class="bg-blob blob-2"></div>
    <div class="bg-blob blob-3"></div>

    <main>
      <!-- Header -->
      <header class="site-header">
        <div class="header-inner">
          <div class="logo-mark">◈</div>
          <h1 class="site-title">Cinéma<span class="title-accent">théque</span></h1>
          <p class="site-tagline">Votre catalogue personnel de films</p>
        </div>
      </header>

      <!-- Search bar -->
      <section class="search-section">
        <div class="search-wrap">
          <span class="search-icon">⌕</span>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Titre, acteur, genre..."
            @keyup.enter="loadMovies(true)"
            class="search-input"
          />
          <button @click="loadMovies(true)" class="search-btn">
            <span>Rechercher</span>
          </button>
        </div>
      </section>

      <!-- Error banner -->
      <div v-if="errorMessage" class="error-banner">
        <span class="error-icon">⚠</span>
        {{ errorMessage }}
      </div>

      <!-- Loading skeleton -->
      <div v-if="isLoading && movies.length === 0" class="movie-grid skeleton-grid">
        <div v-for="i in 8" :key="i" class="movie-card skeleton-card">
          <div class="skeleton-poster"></div>
          <div class="skeleton-line long"></div>
          <div class="skeleton-line short"></div>
        </div>
      </div>

      <!-- Movie grid -->
      <div v-else class="movie-grid">
        <div
          v-for="(movie, index) in movies"
          :key="movie.id"
          class="movie-card"
          :style="{ animationDelay: `${(index % 20) * 40}ms` }"
        >
          <div class="card-poster-wrap">
            <img
              v-if="movie.poster_path"
              :src="'https://image.tmdb.org/t/p/w500' + movie.poster_path"
              :alt="movie.title"
              class="card-poster"
            />
            <div v-else class="no-poster">
              <span>🎬</span>
            </div>
            <div class="card-overlay">
              <button @click="addToFavorites(movie)" class="fav-btn">
                <span class="fav-icon">♥</span>
                Favoris
              </button>
            </div>
          </div>
          <div class="card-info">
            <h3 class="card-title">{{ movie.title }}</h3>
          </div>
        </div>
      </div>

      <!-- Load more -->
      <div class="load-more-wrap" v-if="movies.length > 0 && !errorMessage">
        <button @click="loadMore" class="load-more-btn" :class="{ loading: isLoading }">
          <span v-if="!isLoading">Charger plus</span>
          <span v-else class="spinner">⟳</span>
        </button>
      </div>
    </main>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Sans:wght@300;400;500&display=swap');

/* ── Variables ── */
:root {
  --bg: #0c0c12;
  --surface: #14141f;
  --surface-2: #1c1c2e;
  --border: rgba(255,255,255,0.07);
  --accent: #e8c87d;
  --accent-2: #c084fc;
  --text: #f0eee8;
  --text-muted: #7a7a9a;
  --radius: 14px;
}

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

.app-wrapper {
  min-height: 100vh;
  background-color: var(--bg);
  color: var(--text);
  font-family: 'DM Sans', sans-serif;
  position: relative;
  overflow-x: hidden;
}

/* ── Ambient blobs ── */
.bg-blob {
  position: fixed;
  border-radius: 50%;
  filter: blur(120px);
  opacity: 0.12;
  pointer-events: none;
  z-index: 0;
}
.blob-1 {
  width: 600px; height: 600px;
  background: #6d28d9;
  top: -200px; left: -150px;
}
.blob-2 {
  width: 500px; height: 500px;
  background: #b45309;
  bottom: 100px; right: -100px;
}
.blob-3 {
  width: 400px; height: 400px;
  background: #0e7490;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
}

main {
  position: relative;
  z-index: 1;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px 80px;
}

/* ── Header ── */
.site-header {
  padding: 60px 0 40px;
  text-align: center;
}
.logo-mark {
  font-size: 2rem;
  color: var(--accent);
  margin-bottom: 12px;
  display: block;
  animation: pulse 3s ease-in-out infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.7; transform: scale(0.95); }
}
.site-title {
  font-family: 'Playfair Display', serif;
  font-size: clamp(2.5rem, 6vw, 4.5rem);
  font-weight: 900;
  letter-spacing: -0.02em;
  line-height: 1;
  color: var(--text);
}
.title-accent {
  color: var(--accent);
}
.site-tagline {
  margin-top: 10px;
  color: var(--text-muted);
  font-size: 0.95rem;
  font-weight: 300;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

/* ── Search ── */
.search-section {
  margin-bottom: 48px;
  display: flex;
  justify-content: center;
}
.search-wrap {
  display: flex;
  align-items: center;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 50px;
  padding: 6px 6px 6px 20px;
  gap: 12px;
  width: 100%;
  max-width: 600px;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.search-wrap:focus-within {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(232, 200, 125, 0.12);
}
.search-icon {
  color: var(--text-muted);
  font-size: 1.3rem;
  flex-shrink: 0;
}
.search-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  font-family: 'DM Sans', sans-serif;
  font-size: 1rem;
  color: var(--text);
  min-width: 0;
}
.search-input::placeholder { color: var(--text-muted); }
.search-btn {
  background: var(--accent);
  color: #0c0c12;
  border: none;
  border-radius: 40px;
  padding: 10px 24px;
  font-family: 'DM Sans', sans-serif;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s, transform 0.15s;
  flex-shrink: 0;
}
.search-btn:hover {
  background: #f0d48a;
  transform: scale(1.03);
}
.search-btn:active { transform: scale(0.98); }

/* ── Error Banner ── */
.error-banner {
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(239, 68, 68, 0.12);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #fca5a5;
  border-radius: var(--radius);
  padding: 14px 20px;
  margin-bottom: 32px;
  font-size: 0.95rem;
}
.error-icon { font-size: 1.1rem; }

/* ── Movie Grid ── */
.movie-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(190px, 1fr));
  gap: 24px;
}

/* ── Movie Card ── */
.movie-card {
  border-radius: var(--radius);
  overflow: hidden;
  background: var(--surface);
  border: 1px solid var(--border);
  transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.3s;
  animation: fadeUp 0.5s ease both;
}
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(24px); }
  to   { opacity: 1; transform: translateY(0); }
}
.movie-card:hover {
  transform: translateY(-6px) scale(1.02);
  box-shadow: 0 20px 60px rgba(0,0,0,0.5);
}
.movie-card:hover .card-overlay { opacity: 1; }

.card-poster-wrap {
  position: relative;
  aspect-ratio: 2/3;
  overflow: hidden;
}
.card-poster {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 0.4s ease;
}
.movie-card:hover .card-poster { transform: scale(1.05); }

.no-poster {
  width: 100%; height: 100%;
  background: var(--surface-2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 3rem;
}

.card-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0.1) 60%, transparent 100%);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  padding: 16px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.fav-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  background: var(--accent);
  color: #0c0c12;
  border: none;
  border-radius: 30px;
  padding: 8px 18px;
  font-family: 'DM Sans', sans-serif;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s, transform 0.15s;
}
.fav-btn:hover { background: #f0d48a; transform: scale(1.05); }
.fav-icon { font-size: 0.9rem; }

.card-info {
  padding: 12px 14px 14px;
}
.card-title {
  font-family: 'DM Sans', sans-serif;
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--text);
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* ── Skeleton ── */
.skeleton-card { cursor: default; }
.skeleton-card:hover { transform: none; box-shadow: none; }
.skeleton-poster {
  aspect-ratio: 2/3;
  background: linear-gradient(90deg, var(--surface) 25%, var(--surface-2) 50%, var(--surface) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}
.skeleton-line {
  height: 12px;
  border-radius: 6px;
  margin: 10px 14px 4px;
  background: linear-gradient(90deg, var(--surface) 25%, var(--surface-2) 50%, var(--surface) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}
.skeleton-line.long { width: 80%; }
.skeleton-line.short { width: 50%; }
@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* ── Load More ── */
.load-more-wrap {
  display: flex;
  justify-content: center;
  margin-top: 56px;
}
.load-more-btn {
  background: transparent;
  color: var(--text);
  border: 1px solid var(--border);
  border-radius: 50px;
  padding: 14px 40px;
  font-family: 'DM Sans', sans-serif;
  font-size: 0.95rem;
  font-weight: 400;
  cursor: pointer;
  letter-spacing: 0.04em;
  transition: border-color 0.2s, color 0.2s, transform 0.15s, background 0.2s;
}
.load-more-btn:hover {
  border-color: var(--accent);
  color: var(--accent);
  background: rgba(232, 200, 125, 0.05);
  transform: scale(1.03);
}
.load-more-btn.loading { opacity: 0.6; cursor: not-allowed; }
.spinner {
  display: inline-block;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>