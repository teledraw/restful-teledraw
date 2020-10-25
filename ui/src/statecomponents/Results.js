import React, { useEffect, useState } from "react";
import axios from "axios";
import UserResultsSet from "../helpercomponents/UserResultsSet.js";
import "../results.css";

export default function Results({gameCode}) {

  const [results, setResults] = useState([]);

  useEffect(() => {axios.get(`http://localhost:5000/results?game=${gameCode}`)
  .then((response) => {setResults(response.data)})}, []);

    function getUserResultsSet(result) {
        return <UserResultsSet
            username={result.originator}
            submissions={result.submissions}
        />;
    }

    return (
    <div className="flex-column-container">
      <div className="header">
        <h1>Game Over!</h1>
        <div>(Are you winning, son?)</div>
      </div>
        {results.map((result) => {return getUserResultsSet(result)})}
    </div>
  );
}
