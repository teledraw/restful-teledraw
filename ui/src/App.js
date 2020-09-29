import React, { useState } from "react";
import "./App.css";
import { JoinForm } from "./JoinForm.js";
import PhraseForm from "./PhraseForm.js";
import ImageForm from "./ImageForm.js";
import Results from "./Results.js";
import axios from "axios";
import { useInterval } from "./hooks/interval";

function App() {
  const [username, setUsername] = useState("");
  const [apiStatus, setApiStatus] = useState("");

  useInterval(pollApiStatusOnce, 2000);

  async function pollApiStatusOnce(){
    if(username === "") return;
    const status = await getApiStatus();
    setApiStatus(status.data);
  }

  function getApiStatus(){
    return axios.get('http://localhost:5000/status?username=' + username);
  }

  function setStateToInitialPhrase() {
    // setApiStatus(axios.get('http://localhost:5000/status?username=' + username));
  }

  async function getResults(){
    return (await axios.get('http://localhost:5000/results')).data;
  }

  function getFakeResults() {
    return [
      {
        username: "Marc",
        phrases: ["Bacteria", "Alien invasion!"],
        images: [
          "https://www.samanthasbell.com/wp-content/uploads/2015/02/lukeydrawing.jpg",
        ],
      },
      {
        username: "Alice",
        phrases: ["Punk rock", "Ed Edd n Eddy"],
        images: [
          "https://i.dailymail.co.uk/i/pix/2014/08/18/1408401439429_wps_44_King_s_College_London_new.jpg",
        ],
      },
      {
        username: "Bob",
        phrases: ["Fun in a box", "Gameboy"],
        images: [
          "http://unrealitymag.com/wp-content/uploads/2009/04/kids_nintendo_6.jpg",
        ],
      },
    ];
  }

  function usernameJoined(joinedUsername) {
    axios.post('http://localhost:5000/join', {username:joinedUsername});
    setUsername(joinedUsername);
    pollApiStatusOnce();
  }

  function phraseSubmitted(phrase) {
    axios.post('http://localhost:5000/phrase', {username:username, phrase:phrase})
    pollApiStatusOnce();
  }

  function lastPhraseSubmitted() {
    endGame();
  }

  function artSubmitted(art) {
    axios.post('http://localhost:5000/image', {username:username, image:art})
    pollApiStatusOnce();
  }

  function endGame() {
    setApiStatus("GAME_OVER");
  }

  if (username === "") {
    return (
      <div className="App">
        <JoinForm usernameJoined={usernameJoined} />
      </div>
    );
  } else {
    switch (apiStatus.description) {
      case "SUBMIT_INITIAL_PHRASE":
        return (
          <div className="App">
            <PhraseForm phraseSubmitted={phraseSubmitted} />
          </div>
        );
      case "SUBMIT_PHRASE":
        return (
          <div className="App">
            <PhraseForm
              phraseSubmitted={phraseSubmitted}
              image={apiStatus.prompt}
            />
          </div>
        );
      case "SUBMIT_IMAGE":
        return (
          <div className="App">
            <ImageForm imageSubmitted={artSubmitted} phrase={apiStatus.prompt} />
          </div>
        );
      case "GAME_OVER":
        return (
          <div className="App">
            <Results results={getResults()} />
          </div>
        );
      case "WAIT":
        return (
          <div className="App">
            Waiting for other players...
          </div>);
      case "":
      default:
        return <div>Waiting for API...</div>;
    }
  }
}
export default App;
