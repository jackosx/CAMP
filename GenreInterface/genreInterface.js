var mqtt = require("mqtt");
var express = require("express");
const bodyParser = require("body-parser");
const PORT = 8081;

var app = express();
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

app.listen(PORT, () => {
  console.log("Server is running on PORT:", PORT);
});

var client = mqtt.connect("mqtt://manatee.local:1883");

client.on("connect", function() {
  client.subscribe("g/{r,w}", function(err) {
    if (!err) {
      client.publish("test", "Hello mqtt");
    }
  });
});

client.on("message", function(topic, message) {
  // message is Buffer
  console.log(topic);
  console.log(message.toString());
  //client.end();
});

app.post("/genre", function(req, res) {
  const body = req.body;
  const genre = body.genre;
  client.publish("g/{r,w}", genre.toString());
  res.json("Message sent");
});
