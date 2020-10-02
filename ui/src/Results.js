import React, { useEffect, useState } from "react";
import axios from "axios";
import UserResultsSet from "./UserResultsSet.js";
import "./results.css";

export default function Results(props) {

  const [results, setResults] = useState([]);

  useEffect(() => {axios.get("http://localhost:5000/results")
  .then((response) => {setResults(response.data)})}, []);

  return (
    <div className="flex-column-container">
      <div className="header">
        <h1>Game Over!</h1>
        <div>(Are you winning, son?)</div>
      </div>
      <div className="flex-row-container">
        {results.map((result) => {return (<UserResultsSet
        className="result-set"
        username={result.originator}
        submissions={result.submissions}
      />)})}
    </div>
    </div>
  );
}
