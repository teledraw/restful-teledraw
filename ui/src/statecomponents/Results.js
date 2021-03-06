import React, {useEffect, useState} from "react";
import axios from "axios";
import UserResultsSet from "../helpercomponents/UserResultsSet.js";
import "../results.css";

export default function Results({baseUrl, gameCode}) {

    const [results, setResults] = useState([]);

    useEffect(() => {
        axios.get(`${baseUrl}/game/${gameCode}/results`)
            .then((response) => {
                setResults(response.data)
            })
    }, []);

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
                <div>(To get to these results again later, use the room code and name you used to play.)</div>
            </div>
            {results.map((result) => {
                return getUserResultsSet(result)
            })}
        </div>
    );
}
