import React, { useState } from "react";

export default function ImageForm(props) {
  const [image, setImage] = useState();

  function handleSubmit(event) {
    let fileData = new FileReader();
    fileData.onloadend = (loadEvent) => {props.imageSubmitted(loadEvent.target.result)};
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
        <label htmlFor="image-input">Your Drawing (that will go to {props.nextUsername}):</label>
        <input type="file" accept="image/png" id="image-input" onChange={handleChange}/>
        <button onClick={handleSubmit}>UPLOAD</button>
      </form>
    </div>
  );
}
