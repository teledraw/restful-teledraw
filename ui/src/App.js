import React, { useState } from "react";
import "./App.css";
import { JoinForm } from "./JoinForm.js";
import PhraseForm from "./PhraseForm.js";
import ImageForm from "./ImageForm.js";
import Results from "./Results.js";
import axios from "axios";

function App() {
  const [username, setUsername] = useState("");
  const [apiStatus, setApiStatus] = useState("");

  function setStateToInitialPhrase() {
    // setApiStatus(axios.get('http://localhost:5000/status?username=' + username));
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
    setUsername(joinedUsername);
    setApiStatus("SUBMIT_INITIAL_PHRASE");
    // poll api
  }

  function phraseSubmitted() {
    setApiStatus("SUBMIT_IMAGE");
  }

  function lastPhraseSubmitted() {
    endGame();
  }

  function imageSubmitted() {
    setApiStatus("SUBMIT_PHRASE");
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
    switch (apiStatus) {
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
              phraseSubmitted={lastPhraseSubmitted}
              image={"an image"}
            />
          </div>
        );
      case "SUBMIT_IMAGE":
        return (
          <div className="App">
            <ImageForm imageSubmitted={imageSubmitted} />
          </div>
        );
      case "GAME_OVER":
        return (
          <div className="App">
            <Results results={getFakeResults()} />
          </div>
        );
      case "":
      default:
        return <div>Waiting for API...</div>;
    }
  }
}
export default App;
