var client = mqtt.connect('mqtt://manatee.local:1883'); // you add a ws:// url here
client.subscribe('mqtt/demo');
client.on('message', function(topic, payload) {
  alert([topic, payload].join(': '));
  client.end();
});

function publishMessage(genre) {
  client.publish('g/{r,w}', genre);
}

function setGenre() {
  const genreSelect = document.getElementById('genreSelect');
  const newGenre = genreSelect.value;
  publishMessage(newGenre);
  alert(`Switched to genre: ${newGenre}`);
}
