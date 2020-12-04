import React, { useState } from "react";
import axios from "axios";

export function JoinForm(props) {
  const [username, setUsername] = useState();

  function handleSubmit(event) {
    // axios.post('http://localhost:5000/join', {username:username});
    props.usernameJoined(username);
    event.preventDefault();
  }

  function handleChange(event) {
    setUsername(event.target.value);
  }

  return (
    <div>
      <h1>Join a Game</h1>
      <form>
        <label htmlFor="username-input">Your Name:</label>
        <input type="text" id="username-input" onChange={handleChange}></input>
        <button onClick={handleSubmit}>JOIN</button>
      </form>
    </div>
  );
}
