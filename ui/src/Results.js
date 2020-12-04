import React, { useState } from "react";
import axios from "axios";
import UserResultsSet from "./UserResultsSet.js";
import "./results.css";

export default function Results(props) {
  //assumption:
  //props.results is an array of objects of shape {username:"xyz", phrases: [], images: []}

  return (
    <div className="flex-column-container">
      <div className="header">
        <h1>Game Over!</h1>
        <div>(Are you winning, son?)</div>
      </div>
      <div className="flex-row-container">
      <UserResultsSet
        className="player1"
        username={props.results[0].username}
        phrases={props.results[0].phrases}
        images={props.results[0].images}
      />
      <UserResultsSet
        className="player2"
        username={props.results[1].username}
        phrases={props.results[1].phrases}
        images={props.results[1].images}
      />
      <UserResultsSet
        className="player3"
        username={props.results[2].username}
        phrases={props.results[2].phrases}
        images={props.results[2].images}
      />
    </div>
    </div>
  );
}
