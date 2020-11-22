import React, { useState } from "react";
import axios from "axios/index";
import InstructionsPanel from "../helpercomponents/InstructionsPanel";

export function JoinForm(props) {
  const [username, setUsername] = useState("");
  const [gamecode, setGamecode] = useState("");

  function handleSubmit(event) {
    props.usernameJoined(username, gamecode);
    event.preventDefault();
  }

  function handleUsernameChange(event) {
    setUsername(event.target.value);
  }

  function handleGameChange(event) {
    setGamecode(event.target.value);
  }

  return (
    <div>
      <h1>Join a Game</h1>
      <form>
        <label htmlFor="username-input">Your Name:</label>
        <input type="text" id="username-input" onChange={handleUsernameChange}></input>
        <label htmlFor="gamecode-input">Room Code:</label>
        <input type="text" id="gamecode-input" onChange={handleGameChange}></input>
        <button onClick={handleSubmit}>JOIN</button>
        <InstructionsPanel/>
      </form>
    </div>
  );
}
