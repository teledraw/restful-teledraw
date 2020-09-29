import React from "react";
import { render, act, fireEvent, wait} from "@testing-library/react";
import App from "./App";
import axios from "axios";
import '@testing-library/jest-dom/extend-expect'

jest.mock("axios");

//test('renders learn react link', () => {
//  const { getByText } = render(<App />);
//  const linkElement = getByText(/learn react/i);
//  expect(linkElement).toBeInTheDocument();
//});

test("asks you to join the game with a username", () => {
  const { getByText, getByLabelText } = render(<App />);
  const headerText = getByText(/Join a Game/);
  expect(headerText).toBeInTheDocument();
  const usernameInputElement = getByLabelText(/Your Name/i);
  expect(usernameInputElement).toBeInTheDocument();
});

test("hits the join API endpoint when you submit the join form", async () => {
  axios.post = jest.fn();
  const { getByText, getByLabelText } = render(<App />);
  const usernameInput = getByLabelText(/Your Name/);
  expect(usernameInput).toBeInTheDocument();
  act(() => {
    fireEvent.change(usernameInput, { target: { value: "Billy" } });
  });
  const submitButton = getByText("JOIN");
  expect(submitButton).toBeInTheDocument();
  act(() => {
    fireEvent.click(submitButton);
  });
  await wait(() => {expect(axios.post).toHaveBeenCalledWith("http://localhost:5000/join", {
    username: "Billy",
  })});
});

test("shows the submit phrase form when the API is in SUBMIT_INITIAL_PHRASE state", async () => {
  axios.get = jest.fn(() => {
    return {"description":"SUBMIT_INITIAL_PHRASE"};
    
  });
  axios.post = jest.fn();
  const { getByText, getByLabelText } = render(<App />);
  const usernameInput = getByLabelText(/Your Name/);
  expect(usernameInput).toBeInTheDocument();
  act(() => {
    fireEvent.change(usernameInput, { target: { value: "Billy" } });
  });
  const submitButton = getByText("JOIN");
  expect(submitButton).toBeInTheDocument();
  act(() => {
    fireEvent.click(submitButton);
  });
  await wait(() => {expect(getByText('Submit a Phrase')).toBeInTheDocument()});
});

test("shows the wait dialogue when the API is in WAIT state", async () => {
  axios.get = jest.fn(() => {
    return {"description":"WAIT"};
    
  });
  axios.post = jest.fn();
  const { getByText, getByLabelText } = render(<App />);
  const usernameInput = getByLabelText(/Your Name/);
  act(() => {
    fireEvent.change(usernameInput, { target: { value: "Billy" } });
  });
  const submitButton = getByText("JOIN");
  act(() => {
    fireEvent.click(submitButton);
  });
  await wait(() => {expect(getByText('Waiting for Other Players')).toBeInTheDocument()});
});