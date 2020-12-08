import React from 'react';

export default function AllPlayerStatusPanel(props) {
    function transformStatusToHumanReadableWord(statusEnum) {
        switch (statusEnum) {
            case "SUBMIT_PHRASE":
            case "SUBMIT_INITIAL_PHRASE":
                return "Writing...";
            case "SUBMIT_IMAGE":
                return "Drawing...";
            case "WAIT":
                return "Done for Now...";
        }
    }

    function transformJoinabilityToHumanReadablePhrase(joinability) {
        switch (joinability) {
            case undefined:
                return "???";
            case true:
                return "Waiting for Players";
            case false:
                return "In Progress";
        }
    }

    function transformPhaseNumberToHumanReadableWord(phaseNumber) {
        if (phaseNumber === undefined) {
            return "???";
        } else return phaseNumber;
    }

    function getRoundNumberOrMessage() {
        if (props.summary['phaseNumber'] > props.summary['players'].length) {
            return "(Game Ending...)"
        } else {
            return (transformPhaseNumberToHumanReadableWord(props.summary['phaseNumber']) + " of " + (!props.summary['canJoin'] ? props.summary['players'].length : "???"));
        }
    }

    return <div className={"all-players-status"}>
        <div>Game Status: {transformJoinabilityToHumanReadablePhrase(props.summary['canJoin'])}</div>
        <div>Round: {getRoundNumberOrMessage()}</div>
        <div>Players:</div>
        <ol>
            {props.summary['players'].map(player => {
                return <li className={"other-player-status"}
                           key={player.username}>{player.username + (player.username === props.username ? " (YOU): " : ": ") + transformStatusToHumanReadableWord(player.status.description)}</li>
            })}
        </ol>
        {props.summary['canJoin'] &&
        <div className={"start-warning"}>Warning: The first submission locks the game's player list. Make sure all
            players are in before submitting!</div>}

    </div>;
}