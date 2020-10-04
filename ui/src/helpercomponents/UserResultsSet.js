import React, { useState } from "react";

export default function UserResultsSet(props) {

return (<div>
        <div className="originator-username">{props.username}</div>
        {props.submissions.map((submission, index) => {
            return index % 2 === 0 ? <div>{submission}</div> : <img src={submission} alt=""></img>
        })}
    </div>);
}
