import React from "react";
import {act, fireEvent, render, wait} from "@testing-library/react";
import App from "./App";
import axios from "axios";
import '@testing-library/jest-dom/extend-expect'
import AllPlayersStatusPanel from "./helpercomponents/AllPlayersStatusPanel";

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

function submitPhrase(rendered) {
    const {getByText, getByLabelText} = rendered;

    return rendered;
}

describe('the example frontend', () => {

    function mockGets(statusData = {}, summaryData = [], resultsData = []) {
        axios.get = jest.fn((url) => {
            if (url.includes("status")) {
                return {data: statusData};
            } else if (url.includes("summary")) {
                return {
                    data: summaryData
                }
            } else if (url.includes("results")) {
                return Promise.resolve({data: resultsData});
            }
        });
    }

    describe('the player status panel', () => {
        axios.get = jest.fn(() => {
            return {data: []}
        });
        test('hits the summary endpoint with correct url', async (done) => {
            render(<AllPlayersStatusPanel url={"xyz.abc.com/summary"} gamecode={"TheClubhouse"} username={"Billy"}/>);
            await wait(() => {
                expect(axios.get).toHaveBeenCalledWith("xyz.abc.com/summary?game=TheClubhouse");
                done();
            });
        });
        test('shows GAME OPEN if joining is still possible', () => {

        });
        test('shows GAME IN PROGRESS if joining is still possible', () => {

        });
        test('shows player status when submitting phrases', () => {

        });
        test('shows player status when submitting images', () => {

        });
        test('shows player status when waiting', () => {

        });
        test('does not show on results screen', async (done) => {
            mockGets({description: "GAME_OVER"},[
                {
                    username: "Billy",
                    status: {description: "GAME_OVER"}
                },
                {
                    username: "Bobbie",
                    status: {description: "GAME_OVER"}
                }
            ]);
            axios.post = jest.fn();
            const {queryByText, getByText} = joinGame();
            await wait(() => {
                expect(getByText('Game Over!'));
                expect(queryByText(/Bobbie: GAME OVER/i)).not.toBeInTheDocument();
                done();
            });
        });


    });
    describe('shows the identity panel once a game is joined', () => {

        test("shows the identity panel when the API is in SUBMIT_INITIAL_PHRASE state", async (done) => {
            axios.get = jest.fn(() => {
                return {data: {description: "SUBMIT_INITIAL_PHRASE"}};

            });
            axios.post = jest.fn();
            const {getByText} = joinGame();
            await wait(() => {
                getByText('Your Name: Billy');
                getByText(`This Room's Code: TheClubhouse`);
                done();
            });
        });

        test("shows the identity panel when the API is in SUBMIT_PHRASE state", async (done) => {
            axios.get = jest.fn(() => {
                return {data: {description: "SUBMIT_PHRASE"}};

            });
            axios.post = jest.fn();
            const {getByText} = joinGame();
            await wait(() => {
                getByText('Your Name: Billy');
                getByText(`This Room's Code: TheClubhouse`);
                done();
            });
        });

        test("shows the identity panel when the API is in SUBMIT_IMAGE state", async (done) => {
            axios.get = jest.fn(() => {
                return {data: {description: "SUBMIT_IMAGE"}};

            });
            axios.post = jest.fn();
            const {getByText} = joinGame();
            await wait(() => {
                getByText('Your Name: Billy');
                getByText(`This Room's Code: TheClubhouse`);
                done();
            });
        });

        test("shows the identity panel when the API is in WAIT state", async (done) => {
            axios.get = jest.fn(() => {
                return {data: {description: "WAIT"}};

            });
            axios.post = jest.fn();
            const {getByText} = joinGame();
            await wait(() => {
                getByText('Your Name: Billy');
                getByText(`This Room's Code: TheClubhouse`);
                done();
            });
        });

        test("shows the identity panel when the API is in GAME_OVER state", async (done) => {
            axios.get = jest.fn(() => {
                return {data: {description: "GAME_OVER"}};

            });
            axios.post = jest.fn();
            const {getByText} = joinGame();
            await wait(() => {
                getByText('Your Name: Billy');
                getByText(`This Room's Code: TheClubhouse`);
                done();
            });
        });

        test("shows the identity panel when the API is in undefined state", async (done) => {
            axios.get = jest.fn(() => {
                return {data: {description: ""}};

            });
            axios.post = jest.fn();
            const {getByText} = joinGame();
            await wait(() => {
                getByText('Your Name: Billy');
                getByText(`This Room's Code: TheClubhouse`);
                done();
            });
        });

    });
    describe('shows the right content to the user based on state', () => {
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
        test("hits the join API endpoint when you submit the join form", async (done) => {
            axios.post = jest.fn();
            axios.get = jest.fn(() => {
                return {data: {description: "WAIT"}};
            });
            joinGame();
            await wait(() => {
                expect(axios.post).toHaveBeenCalledWith("http://localhost:5000/join", {
                    username: "Billy",
                    game: "TheClubhouse"
                });
                done();
            });
        });

        test("hits the phrase API endpoint when you submit the phrase form", async (done) => {
            axios.post = jest.fn();
            axios.get = jest.fn(() => {
                return {data: {description: "SUBMIT_INITIAL_PHRASE"}};
            });
            let {getByLabelText, getByText} = joinGame();
            await wait(() => {
                const phraseInput = getByLabelText(/Your common phrase, saying, or word/);
                act(() => {
                    fireEvent.change(phraseInput, {target: {value: "No ghouls allowed"}});
                });
                const submitButton = getByText("SUBMIT");
                act(() => {
                    fireEvent.click(submitButton);
                });
            });
            await wait(() => {
                expect(axios.post).toHaveBeenCalledWith("http://localhost:5000/phrase", {
                    username: "Billy",
                    game: "TheClubhouse",
                    phrase: "No ghouls allowed"
                });
                done();
            });
        });

        test("hits the image API endpoint when you submit the image form", async (done) => {
            axios.post = jest.fn();
            axios.get = jest.fn(() => {
                return {data: {description: "SUBMIT_IMAGE"}};
            });

            const imageFile = new File(['imageXXXimageYYYimageZZZ'], 'teledraw.png', {
                type: 'image/png',
            });

            let {getByLabelText, getByText} = joinGame();
            await wait(() => {
                const imageInput = getByLabelText(/Your Drawing/);
                act(() => {
                    Object.defineProperty(imageInput, 'files', {
                        value: [imageFile],
                        configurable: true
                    });
                    fireEvent.change(imageInput);
                });
                const submitButton = getByText("UPLOAD");
                act(() => {
                    fireEvent.click(submitButton);
                });
            });
            await wait(() => {
                expect(axios.post).toHaveBeenCalledWith('http://localhost:5000/image',
                    {
                        username: 'Billy',
                        image: 'data:image/png;base64,aW1hZ2VYWFhpbWFnZVlZWWltYWdlWlpa',
                        game: 'TheClubhouse'
                    });
                done();
            });
        });
    });
})
;
