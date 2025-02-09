<template>
    <div class="not-found">
      <h1>404</h1>
      <p>Oups ! La page que vous recherchez n'existe pas.</p>
      <router-link to="/" class="home-button">Retour à l'accueil</router-link>
    </div>
  </template>
  
  <script>
  export default {
    name: "NotFound",
  };
  </script>
  
  <style>
  .not-found {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100vh;
    text-align: center;
    font-family: Arial, sans-serif;
    color: #333;
    background-color: #f9f9f9;
  }
  
  .not-found h1 {
    font-size: 6rem;
    margin-bottom: 1rem;
    color: #ff6b6b;
  }
  
  .not-found p {
    font-size: 1.5rem;
    margin-bottom: 2rem;
  }
  
  .home-button {
    display: inline-block;
    padding: 10px 20px;
    font-size: 1rem;
    color: #fff;
    background-color: #007bff;
    text-decoration: none;
    border-radius: 5px;
    transition: background-color 0.3s ease;
  }
  
  .home-button:hover {
    background-color: #0056b3;
  }
  </style>
  