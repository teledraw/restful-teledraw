import React from "react";

export default function IdentityPanel({username, gamecode}) {
    return (<div className={"identity"}>
        <div>Your Name: {username}</div>
        <div>This Room's Code: {gamecode}</div>
    </div>)
}