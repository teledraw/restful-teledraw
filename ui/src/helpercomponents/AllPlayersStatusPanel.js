import React from 'react';
import {useState} from "react";
import {useInterval} from "../hooks/interval";
import axios from 'axios';

export default function AllPlayerStatusPanel({url, gamecode, username}) {
    const [summary, setSummary] = useState({players:[], canJoin:undefined, phaseNumber:undefined});

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

    function transformJoinabilityToHumanReadablePhrase(joinability){
        switch (joinability) {
            case undefined:
                return "???";
            case true:
                return "Waiting for Players";
            case false:
                return "In Progress";
        }
    }

    function transformPhaseNumberToHumanReadableWord(phaseNumber){
        if(phaseNumber === undefined){
            return "???";
        }
        else return phaseNumber;
    }

    useInterval(() => {getSummary(url, gamecode)}, 2000);

    return <div className={"all-players-status"}>
        <div>Game Status: {transformJoinabilityToHumanReadablePhrase(summary['canJoin'])}</div>
        <div>Round {transformPhaseNumberToHumanReadableWord(summary['phaseNumber'])} of {!summary['canJoin'] ? summary['players'].length : "???"}</div>
        <div>Players:</div>
        <ol>
        {summary['players'].map(player => {
            return <li className={"other-player-status"} key={player.username}>{player.username + (player.username === username ? " (YOU): " : ": ") + transformStatusToHumanReadableWord(player.status.description)}</li>
        })}
        </ol>
    </div>;
}