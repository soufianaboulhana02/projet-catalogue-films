<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const movies = ref([])
const searchQuery = ref('') 
const errorMessage = ref('') 
const currentPage = ref(1)

const loadMovies = async (isNewSearch = false) => {
  errorMessage.value = ''
  
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
      errorMessage.value = `Aucun film trouve pour : "${searchQuery.value}"`
    } else {
      movies.value = [...movies.value, ...response.data.results]
    }
  } catch (error) {
    errorMessage.value = "Une erreur est survenue pendant la recherche."
    console.error(error)
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
    alert(`Le film "${movie.title}" a ete ajoute a tes favoris !`)
  } catch (error) {
    if (error.response && error.response.status === 400) {
      alert(`Ce film est deja dans tes favoris.`)
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
  <main>
    <h1>Mon Catalogue de Films</h1>
    
    <div class="search-container">
      <input 
        v-model="searchQuery" 
        type="text" 
        placeholder="Rechercher un film..." 
        @keyup.enter="loadMovies(true)"
      />
      <button @click="loadMovies(true)" class="search-btn">Rechercher</button>
    </div>

    <div v-if="errorMessage" class="error-banner">
      {{ errorMessage }}
    </div>

    <div class="movie-grid">
      <div v-for="movie in movies" :key="movie.id" class="movie-card">
        <img v-if="movie.poster_path" :src="'https://image.tmdb.org/t/p/w500' + movie.poster_path" :alt="movie.title" />
        <div v-else class="no-image">Pas d'image</div>
        <h3>{{ movie.title }}</h3>
        <button @click="addToFavorites(movie)" class="fav-button">
          Ajouter aux favoris
        </button>
      </div>
    </div>

    <div class="load-more-container" v-if="movies.length > 0 && !errorMessage">
      <button @click="loadMore" class="load-more-btn">Charger plus de films</button>
    </div>
  </main>
</template>

<style scoped>
main { padding: 20px; font-family: Arial, sans-serif; background-color: #1a1a1a; color: white; min-height: 100vh; }
h1 { text-align: center; margin-bottom: 20px; }
.search-container { display: flex; justify-content: center; margin-bottom: 30px; gap: 10px; }
.search-container input { padding: 10px; font-size: 16px; width: 300px; border-radius: 5px; border: 1px solid #ccc; }
.search-btn { padding: 10px 20px; background-color: #3498db; color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; }
.search-btn:hover { background-color: #2980b9; }
.error-banner { background-color: #e74c3c; color: white; text-align: center; padding: 15px; border-radius: 5px; margin-bottom: 20px; font-weight: bold; }
.movie-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 20px; }
.movie-card { background-color: #2c2c2c; border-radius: 8px; padding: 10px; text-align: center; box-shadow: 0 4px 8px rgba(0,0,0,0.2); display: flex; flex-direction: column; justify-content: space-between; }
.movie-card img { max-width: 100%; border-radius: 4px; margin-bottom: 10px; }
.no-image { height: 300px; display: flex; align-items: center; justify-content: center; background-color: #555; border-radius: 4px; margin-bottom: 10px; }
.fav-button { background-color: #f39c12; color: white; border: none; padding: 10px; border-radius: 5px; cursor: pointer; font-weight: bold; margin-top: 10px; }
.fav-button:hover { background-color: #e67e22; }
.load-more-container { display: flex; justify-content: center; margin-top: 40px; padding-bottom: 40px; }
.load-more-btn { background-color: #2ecc71; color: white; font-size: 18px; padding: 15px 30px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; transition: background-color 0.3s; }
.load-more-btn:hover { background-color: #27ae60; }
</style>
