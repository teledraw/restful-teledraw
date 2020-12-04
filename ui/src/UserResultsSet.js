import React, { useState } from "react";

export default function UserResultsSet(props) {
return   <div>
    <div className="originator-username">{props.username}</div>
<div>{props.phrases[0]}</div>
<img src={props.images[0]} alt=""></img>
<div>{props.phrases[1]}</div>
</div>
}
