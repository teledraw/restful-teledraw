import React, { useState } from "react";
import axios from "axios";

export default function PhraseForm(props) {
  const [phrase, setPhrase] = useState();

  function handleSubmit(event) {
    // axios.post('http://localhost:5000/join', {username:username});
    props.phraseSubmitted(phrase);
    event.preventDefault();
  }

  function handleChange(event) {
    setPhrase(event.target.value);
  }

  return (
    <div>
      <h1>Submit a Phrase</h1>
      {props.image && (
        <img
          src="http://unrealitymag.com/wp-content/uploads/2009/04/kids_nintendo_6.jpg"
          alt="hasty-ddrawing"
          width="800"
          height="600"
        />
      )}
      <form>
        <label htmlFor="phrase-input">Your phrase:</label>
        <input type="text" id="phrase-input" onChange={handleChange}></input>
        <button onClick={handleSubmit}>SUBMIT</button>
      </form>
    </div>
  );
}
