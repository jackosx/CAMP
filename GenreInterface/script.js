function setGenre(genreId) {
  var xhr = new XMLHttpRequest();
  xhr.open('POST', 'http://localhost:5000/', true);

  //Send the proper header information along with the request
  xhr.setRequestHeader('Content-Type', 'application/json');
  console.log(genreId);
  const body = JSON.stringify({ topic: 'g/{r,w}', payload: genreId });
  xhr.send(body);
}
