import React from 'react';
import {useState} from "react";
import {useInterval} from "../hooks/interval";
import axios from 'axios';

export default function AllPlayerStatusPanel({url, gamecode, username}) {
    const [summary, setSummary] = useState([]);

    async function getSummary(url, gamecode){
        const summaryResponse = await axios.get(url+'?game='+gamecode);
        setSummary(summaryResponse.data);
    }

    function transformStatusToHumanReadableWord(statusEnum){
        switch (statusEnum) {
            case "SUBMIT_PHRASE":
            case "SUBMIT_INITIAL_PHRASE":
                return "Writing...";
            case "SUBMIT_IMAGE":
                return "Drawing...";
            case "WAIT":
                return "Waiting...";
        }
    }

    useInterval(() => {getSummary(url, gamecode)}, 2000);

    return <div className={"all-players-status"}>
        {summary.map(player => {
            return <div className={"other-player-status"} key={player.username}>{player.username + (player.username === username ? " (YOU): " : ": ") + transformStatusToHumanReadableWord(player.status.description)}</div>
        })}
    </div>;
}