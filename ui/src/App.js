import React, { useState } from "react";
import "./App.css";
import { JoinForm } from "./statecomponents/JoinForm.js";
import PhraseForm from "./statecomponents/PhraseForm.js";
import ImageForm from "./statecomponents/ImageForm.js";
import Results from "./statecomponents/Results.js";
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

  function getUrl(){
    return process.env.REACT_APP_API_URL;
  }

  function getApiStatus(){
    return axios.get(getUrl() + '/status?username=' + username);
  }

  function getResults(){
    return axios.get(getUrl() + '/results').then((response) => {return response.data});
  }

  function usernameJoined(joinedUsername) {
    axios.post(getUrl() + '/join', {username:joinedUsername});
    setUsername(joinedUsername);
    pollApiStatusOnce();
  }

  function phraseSubmitted(phrase) {
    axios.post(getUrl() + '/phrase', {username:username, phrase:phrase})
    pollApiStatusOnce();
  }

  function artSubmitted(art) {
    axios.post(getUrl() + '/image', {username:username, image:art})
    pollApiStatusOnce();
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
            <PhraseForm phraseSubmitted={phraseSubmitted}
                        nextUsername={apiStatus.nextPlayerUsername}/>
          </div>
        );
      case "SUBMIT_PHRASE":
        return (
          <div className="App">
            <PhraseForm
              phraseSubmitted={phraseSubmitted}
              image={apiStatus.prompt}
              previousUsername={apiStatus.previousPlayerUsername}
              nextUsername={apiStatus.nextPlayerUsername}
            />
          </div>
        );
      case "SUBMIT_IMAGE":
        return (
          <div className="App">
            <ImageForm imageSubmitted={artSubmitted}
                       phrase={apiStatus.prompt}
                       previousUsername={apiStatus.previousPlayerUsername}
                       nextUsername={apiStatus.nextPlayerUsername}
            />
          </div>
        );
      case "GAME_OVER":
        return (
          <div className="App">
            <Results/>
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
