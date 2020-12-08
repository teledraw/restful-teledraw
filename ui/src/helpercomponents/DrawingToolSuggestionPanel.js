import React, {useState} from 'react';

export default function DrawingToolSuggestionPanel({toolUrls}) {
    const [toolIndex, setToolIndex] = useState(-1);

    function showNextTool() {
        setToolIndex(toolIndex + 1);
    }

    return (<div className={"drawing-tool-panel"}>
        {toolUrls && toolUrls.length > 0 && <div className={"link-styling"}
                                                 onClick={showNextTool}>{toolIndex >= 0 ? "I'd like another suggestion please!" : "I need a drawing tool suggestion!"}</div>}
        {toolIndex >= 0 &&
        <div className={"drawing-tool-suggestion"}> Why not try <a href={toolUrls[toolIndex % toolUrls.length]}
                                                                   target="_blank">{toolUrls[toolIndex % toolUrls.length]}</a>?
        </div>}
    </div>);
}