import React from "react";

export default function UserResultsSet(props) {

    function imageOrPhrase(index, submission) {
        return index % 2 === 0 ? <div className="row-item">" {submission} "</div> :
            <img className="row-item results-image" src={submission} alt=""/>;
    }

    function imageOrPhrasePlusLeaderText(index, submission) {
        return index % 2 === 0 ? <>
            <div className="row-item">" {submission} "</div>
            <div className="row-item">Leading to...</div>
        </> : <><img className="row-item" src={submission} alt=""/>
            <div className="row-item">Leading to...</div>
        </>;
    }

    return (<div className={"user-results-container"}>
        <div className="row-item"> Player {props.username} originally submitted</div>
        {props.submissions.map((submission, index) => {
            return index >= props.submissions.length - 1 ? imageOrPhrase(index, submission) : imageOrPhrasePlusLeaderText(index, submission);
        })}
    </div>);
}
