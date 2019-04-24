function setGenre(genreId) {
  var xhr = new XMLHttpRequest();
  xhr.open('POST', 'http://localhost:5000/', true);

  //Send the proper header information along with the request
  xhr.setRequestHeader('Content-Type', 'application/json');
  const body = JSON.stringify({ topic: '/g', payload: genreId });
  xhr.send(body);
}

function loadGenres() {
  var xmlhttp = new XMLHttpRequest();
  xmlhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      var genres = JSON.parse(this.responseText);
      populateGenres(genres);
    }
  };
  xmlhttp.open('GET', 'genres.json', true);
  xmlhttp.send();
}

function populateGenres(genres) {
  const genreSelect = document.getElementById('genreSelect');
  genres.forEach(genre => {
    const g = document.createElement('p');
    g.innerHTML = genre.name;
    g.value = genre.id;
    g.onclick = function() {
      setGenre(genre.id);
    };
    genreSelect.appendChild(g);
  });
}
