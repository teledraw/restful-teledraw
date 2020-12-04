import React, { useState } from "react";
import "./App.css";
import { JoinForm } from "./statecomponents/JoinForm.js";
import PhraseForm from "./statecomponents/PhraseForm.js";
import ImageForm from "./statecomponents/ImageForm.js";
import Results from "./statecomponents/Results.js";
import axios from "axios";
import { useInterval } from "./hooks/interval";
import IdentityPanel from "./helpercomponents/IdentityPanel";
import AllPlayerStatusPanel from "./helpercomponents/AllPlayersStatusPanel";

function App() {
  const [username, setUsername] = useState("");
  const [gameCode, setGameCode] = useState("");
  const [apiStatus, setApiStatus] = useState("");
  const [apiSummary, setApiSummary] = useState(undefined);

  useInterval(pollApiStatusOnce, 2000);
  useInterval(pollApiSummaryOnce, 2000);

  async function pollApiStatusOnce(){
    if(username === "") return;
    const status = await getApiStatusForPlayer();
    setApiStatus(status.data);
  }

  async function pollApiSummaryOnce(){
    if(username === "") return;
    const summary = await getApiSummaryForPlayer();
    setApiSummary(summary.data);
  }


  function getUrl(){
    return process.env.REACT_APP_API_URL;
  }

  function getApiStatusForPlayer(){
    return axios.get(getUrl() + `/game/${gameCode}/player/${username}`);
  }

  function getApiSummaryForPlayer(){
    return axios.get(getUrl()+`/game/${gameCode}`)
  }

  function usernameJoined(joinedUsername, joinedGame) {
    axios.post(getUrl() + '/join', {username:joinedUsername,game:joinedGame});
    setUsername(joinedUsername);
    setGameCode(joinedGame);
    pollApiStatusOnce();
  }

  function phraseSubmitted(phrase) {
    axios.post(getUrl() + '/phrase', {username:username, phrase:phrase, game:gameCode});
    pollApiStatusOnce();
  }

  function artSubmitted(art) {
    axios.post(getUrl() + '/image', {username:username, image:art, game:gameCode});
    pollApiStatusOnce();
  }

  function getStatusPanelByStatus(status){
    if(status.description === "GAME_OVER" || apiSummary === undefined){
      return <div></div>;
    }else{
      return <AllPlayerStatusPanel summary={apiSummary} username={username}/>
    }
  }

  function getIdentityPanelByStatus(status) {
    switch (status.description) {
      case "GAME_OVER":
        return <></>;
      default:
          return <IdentityPanel username={username} gamecode={gameCode}/>
    }
  }

  function getContentByStatus(status){
    switch (status.description) {
      case "SUBMIT_INITIAL_PHRASE":
        return (
              <PhraseForm phraseSubmitted={phraseSubmitted}
                          nextUsername={status.nextPlayerUsername}
                          canStart={apiSummary ? apiSummary.canStart : false}/>
        );
      case "SUBMIT_PHRASE":
        return (
              <PhraseForm
                  phraseSubmitted={phraseSubmitted}
                  image={status.prompt}
                  previousUsername={status.previousPlayerUsername}
                  nextUsername={status.nextPlayerUsername}
              />
        );
      case "SUBMIT_IMAGE":
        return (
              <ImageForm imageSubmitted={artSubmitted}
                         phrase={status.prompt}
                         previousUsername={status.previousPlayerUsername}
                         nextUsername={status.nextPlayerUsername}
              />
        );
      case "GAME_OVER":
        return (
              <Results baseUrl={getUrl()} gameCode={gameCode}/>
        );
      case "WAIT":
        return (
            "Waiting for other players...");
      case "":
      default:
        return "Waiting for API...";
    }
  }

  if (username === "") {
    return (
      <div className="App">
        <JoinForm usernameJoined={usernameJoined} />
      </div>
    );
  } else {
    return <div className={"App in-play"}>
      {getIdentityPanelByStatus(apiStatus)}
      {getContentByStatus(apiStatus)}
      {getStatusPanelByStatus(apiStatus)}
    </div>
  }
}
export default App;
