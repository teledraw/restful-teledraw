import React, { useState } from "react";

export default function ImageForm(props) {
  const [image, setImage] = useState();

  function handleSubmit(event) {
    props.imageSubmitted(image);
    event.preventDefault();
  }

  function handleChange(event) {
    setImage(event.target.value);
  }

  return (
    <div>
      <h1>Submit an Image</h1>
  <h2>Draw this phrase: "{props.phrase}"</h2>
      <form>
        <label htmlFor="image-input">Your Drawing:</label>
        <input type="file" id="image-input" onChange={handleChange}></input>
        <button onClick={handleSubmit}>UPLOAD</button>
      </form>
    </div>
  );
}
