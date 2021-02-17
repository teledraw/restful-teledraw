import React, {useState} from "react";
import DrawingToolSuggestionPanel from "../helpercomponents/DrawingToolSuggestionPanel";
import {FileInput, FilenameFileDisplay} from "@fordlabs/caffeinated-components";

export default function ImageForm(props) {
    const drawingToolUrls = ["https://jspaint.app", "https://www.piskelapp.com", "https://pixlr.com/", "https://www.getpaint.net/"];

    const [image, setImage] = useState(undefined);

    function handleSubmit(event) {
        let fileData = new FileReader();
        fileData.onloadend = (loadEvent) => {
            props.imageSubmitted(loadEvent.target.result)
        };
        fileData.readAsDataURL(image);
        event.preventDefault();
    }

    function handleChange(event) {
        setImage(event.target.files[0]);
    }

    return (
        <div>
            <h1>Submit an Image</h1>
            <h2>Draw this phrase (from {props.previousUsername}): "{props.phrase}"</h2>
            <form>
                <div>Your Drawing (that will go to {props.nextUsername}):</div>
                <FileInput onFileSelected={handleChange} labelContent={!image ? <>"Choose a file..."</> :
                    <FilenameFileDisplay file={image}/>}/>
                <button onClick={handleSubmit}>SUBMIT</button>
            </form>
            <DrawingToolSuggestionPanel toolUrls={drawingToolUrls}/>
        </div>
    );
}
