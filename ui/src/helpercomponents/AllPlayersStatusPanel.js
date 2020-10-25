import React from 'react';
import {useState} from "react";
import {useInterval} from "../hooks/interval";
import axios from 'axios';

export default function AllPlayerStatusPanel({url, gamecode, username}) {
    const [summary, setSummary] = useState("");

    async function getSummary(url, gamecode){
        const summaryResponse = await axios.get(url+'?game='+gamecode);
        setSummary(summaryResponse.data)
    }

    useInterval(() => {getSummary(url, gamecode)}, 4000);

    return <></>;
}