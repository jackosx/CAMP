let selectedGenre;
function setGenre(genre) {
  var xhr = new XMLHttpRequest();
  xhr.open('POST', 'http://localhost:5000/', true);

  //Send the proper header information along with the request
  xhr.setRequestHeader('Content-Type', 'application/json');
  const body = JSON.stringify({ topic: '/g', payload: genre.id });
  xhr.send(body);
  selectedGenre = genre;
  updateGenreColors();
  setKeyText();
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
    const g = document.createElement('h3');
    g.innerHTML = genre.name;
    g.value = genre.id;
    g.onclick = function() {
      setGenre(genre);
    };
    genreSelect.appendChild(g);
  });
}

function updateGenreColors() {
  const genreSelect = document.getElementById('genreSelect');
  const genreTexts = genreSelect.getElementsByTagName('h3');
  var i;
  for (i = 0; i < genreTexts.length; i++) {
    if (genreTexts[i].value == selectedGenre.id) {
      genreTexts[i].style.color = '#3A00FB';
    } else {
      genreTexts[i].style.color = 'white';
    }
  }
}

function setKeyText() {
  const key = selectedGenre.key;
  const keyText = document.getElementById('key');
  keyText.innerHTML = key;
}
