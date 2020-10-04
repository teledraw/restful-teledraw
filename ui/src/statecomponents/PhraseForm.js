import React, { useState } from "react";
import axios from "axios/index";

export default function PhraseForm(props) {
  const [phrase, setPhrase] = useState();

  function handleSubmit(event) {
    props.phraseSubmitted(phrase);
    event.preventDefault();
  }

  function handleChange(event) {
    setPhrase(event.target.value);
  }

  function getLabelText(){
    return (props.image ? "Your phrase describing this image" : "Your common phrase, saying, or word") + " (that will go to " + props.nextUsername + "):";
  }

  return (
    <div>
      <h1>Submit a Phrase</h1>
      {props.image && (
          <div><p>(This image drawn for you by {props.previousUsername})</p><img
              src={props.image}
              alt="The image used as a prompt"
              width="800"
              height="600"
          /></div>
      )}
      <form>
        <label htmlFor="phrase-input">{getLabelText()}</label>
        <input type="text" id="phrase-input" onChange={handleChange}></input>
        <button onClick={handleSubmit}>SUBMIT</button>
      </form>
    </div>
  );
}