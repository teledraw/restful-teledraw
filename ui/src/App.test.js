import React from "react";
import {act, fireEvent, render, wait} from "@testing-library/react";
import App from "./App";
import axios from "axios";
import '@testing-library/jest-dom/extend-expect'

jest.mock("axios");


function joinGame() {
    const rendered = render(<App/>);
    const {getByText, getByLabelText} = rendered;
    const usernameInput = getByLabelText(/Your Name/);
    const gamecodeInput = getByLabelText(/Room Code/);
    act(() => {
        fireEvent.change(usernameInput, {target: {value: "Billy"}});
        fireEvent.change(gamecodeInput, {target: {value: "TheClubhouse"}});
    });
    const submitButton = getByText("JOIN");
    act(() => {
        fireEvent.click(submitButton);
    });
    return rendered;
}


describe('shows the right stuff to the user', () => {
    test("asks you to join the game with a username and game code", () => {
        const {getByText, getByLabelText} = render(<App/>);
        const headerText = getByText(/Join a Game/);
        expect(headerText).toBeInTheDocument();
        const usernameInputElement = getByLabelText(/Your Name/i);
        const roomCodeInputElement = getByLabelText(/Room Code/i);
        expect(usernameInputElement).toBeInTheDocument();
        expect(roomCodeInputElement).toBeInTheDocument();

    });

    test("shows the submit phrase form when the API is in SUBMIT_INITIAL_PHRASE state", async (done) => {
        axios.get = jest.fn(() => {
            return {data: {description: "SUBMIT_INITIAL_PHRASE"}};

        });
        axios.post = jest.fn();
        const {getByText} = joinGame();
        await wait(() => {
            getByText('Submit a Phrase');
            done();
        });
    });

    test("shows the submit image form when the API is in SUBMIT_IMAGE state", async (done) => {
        axios.get = jest.fn(() => {
            return {
                data: {
                    description: "SUBMIT_IMAGE",
                    prompt: "Once upon a time",
                    previousPlayerUsername: "Tinkerbell"
                }
            };
        });
        axios.post = jest.fn();
        const {getByText} = joinGame();
        await wait(() => {
            getByText('Draw this phrase (from Tinkerbell): "Once upon a time"');
            done();
        });
    });

    test("shows the wait dialogue when the API is in WAIT state", async (done) => {
        axios.get = jest.fn(() => {
            return {data: {description: "WAIT"}};
        });
        axios.post = jest.fn();
        const {getByText} = joinGame();
        await wait(() => {
            getByText(/Waiting for other players/);
            done();
        });
    });
});
describe('sends the right stuff to the API', () => {
    test("hits the join API endpoint when you submit the join form", async () => {
        axios.post = jest.fn();
        axios.get = jest.fn(() => {
            return {data: {description: "WAIT"}};
        });
        joinGame();
        await wait(() => {
            expect(axios.post).toHaveBeenCalledWith("http://localhost:5000/join", {
                username: "Billy",
                game: "TheClubhouse"
            })
        });
    });
});

