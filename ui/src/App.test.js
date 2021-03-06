import React from "react";
import {act, fireEvent, render, wait} from "@testing-library/react";
import App from "./App";
import axios from "axios";
import '@testing-library/jest-dom/extend-expect'
import Results from "./statecomponents/Results";

jest.mock("axios");

describe('the example frontend', () => {

    function mockGets(statusData = {}, summaryPlayers = [], resultsData = [], summaryIsJoinable = false, summaryPhaseNumber = 1, summaryCanStart = true) {
        axios.get = jest.fn((url) => {
            if (url.match("\/game\/.*\/player\/.*")) {
                return {data: statusData};
            } else if (url.includes("results")) {
                return Promise.resolve({data: resultsData});
            } else if (url.match("\/game\/.*")) {
                return {
                    data: {
                        players: summaryPlayers,
                        canJoin: summaryIsJoinable,
                        phaseNumber: summaryPhaseNumber,
                        canStart: summaryCanStart
                    }
                };
            }
        });
    }

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

    describe('the results panel', () => {
        test('hits the results endpoint with correct url', async (done) => {
            mockGets();
            render(<Results baseUrl={"xyz.abc.com"} gameCode={"TheClubhouse"}/>);
            await wait(() => {
                expect(axios.get).toHaveBeenCalledWith("xyz.abc.com/game/TheClubhouse/results");
                done();
            });
        });
    });
    describe('the player status panel', () => {
        test('shows "Waiting for Players" if joining is still possible and "???" for total rounds', async (done) => {
            mockGets({description: "SUBMIT_INITIAL_PHRASE"}, [
                {
                    username: "Billy",
                    status: {description: "SUBMIT_INITIAL_PHRASE"}
                },
                {
                    username: "Bobbie",
                    status: {description: "SUBMIT_INITIAL_PHRASE"}
                }
            ], [], true, 1);
            axios.post = jest.fn();
            const {queryByText, getByText} = joinGame();
            await wait(() => {
                expect(getByText('Submit a Phrase'));
                expect(getByText(/Game Status: Waiting for Players/));
                expect(getByText("Round: 1 of ???"));
                done();
            });
        });
        test('shows "In Progress" if joining is not still possible', async (done) => {
            mockGets({description: "SUBMIT_INITIAL_PHRASE"}, [
                {
                    username: "Billy",
                    status: {description: "SUBMIT_INITIAL_PHRASE"}
                },
                {
                    username: "Bobbie",
                    status: {description: "WAIT"}
                }
            ], [], false);
            axios.post = jest.fn();
            const {queryByText, getByText} = joinGame();
            await wait(() => {
                expect(getByText('Submit a Phrase'));
                expect(getByText(/Game Status: In Progress/));
                done();
            });
        });
        test('shows player status when submitting phrases', async (done) => {
            mockGets({description: "SUBMIT_PHRASE"}, [
                {
                    username: "Billy",
                    status: {description: "SUBMIT_PHRASE"}
                },
                {
                    username: "Bobbie",
                    status: {description: "SUBMIT_PHRASE"}
                }
            ]);
            axios.post = jest.fn();
            const {queryByText, getByText} = joinGame();
            await wait(() => {
                expect(getByText('Submit a Phrase'));
                expect(getByText(/Bobbie: Writing\.\.\./i));
                expect(getByText(/Billy \(YOU\): Writing\.\.\./i));
                done();
            });
        });
        test('shows player status when submitting images', async (done) => {
            mockGets({description: "SUBMIT_IMAGE"}, [
                {
                    username: "Billy",
                    status: {description: "SUBMIT_IMAGE"}
                },
                {
                    username: "Bobbie",
                    status: {description: "SUBMIT_IMAGE"}
                },
                {
                    username: "Bibbie",
                    status: {description: "WAIT"}
                }
            ]);
            axios.post = jest.fn();
            const {getByText} = joinGame();
            await wait(() => {
                expect(getByText('Submit an Image'));
                expect(getByText(/Bobbie: Drawing\.\.\./i));
                expect(getByText(/Bibbie: Done for Now\.\.\./i));
                done();
            });
        });
        test('shows player status when waiting', async (done) => {
            mockGets({description: "WAIT"}, [
                {
                    username: "Billy",
                    status: {description: "WAIT"}
                },
                {
                    username: "Bobbie",
                    status: {description: "SUBMIT_IMAGE"}
                }
            ]);
            axios.post = jest.fn();
            const {getByText} = joinGame();
            await wait(() => {
                expect(getByText('Waiting for other players...'));
                expect(getByText(/Bobbie: Drawing\.\.\./i));
                done();
            });
        });
        test('shows phase number from the API and max phase number based on # of players', async (done) => {
            mockGets({description: "WAIT"}, [
                {
                    username: "Billy",
                    status: {description: "WAIT"}
                },
                {
                    username: "Bobbie",
                    status: {description: "SUBMIT_IMAGE"}
                }
            ], [], false, 1);
            axios.post = jest.fn();
            const {getByText} = joinGame();
            await wait(() => {
                expect(getByText('Round: 1 of 2'));
                done();
            });
        });

        test('shows a special message if the phase number from the API is too high', async (done) => {
            mockGets({description: "WAIT"}, [
                {
                    username: "Billy",
                    status: {description: "WAIT"}
                },
                {
                    username: "Bobbie",
                    status: {description: "SUBMIT_IMAGE"}
                }
            ], [], false, 5);
            axios.post = jest.fn();
            const {getByText} = joinGame();
            await wait(() => {
                expect(getByText('Round: (Game Ending...)'));
                done();
            });
        });

        test('does not show on results screen', async (done) => {
            mockGets({description: "GAME_OVER"}, [
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
                expect(queryByText(/Bobbie:/i)).not.toBeInTheDocument();
                done();
            });
        });


    });
    describe('shows the identity panel once a game is joined', () => {

        test("shows the identity panel when the API is in SUBMIT_INITIAL_PHRASE state", async (done) => {
            mockGets({description: "SUBMIT_INITIAL_PHRASE"});
            axios.post = jest.fn();
            const {getByText} = joinGame();
            await wait(() => {
                getByText('Your Name: Billy');
                getByText(`This Room's Code: TheClubhouse`);
                done();
            });
        });

        test("shows the identity panel when the API is in SUBMIT_PHRASE state", async (done) => {
            mockGets({description: "SUBMIT_PHRASE"});
            axios.post = jest.fn();
            const {getByText} = joinGame();
            await wait(() => {
                getByText('Your Name: Billy');
                getByText(`This Room's Code: TheClubhouse`);
                done();
            });
        });

        test("shows the identity panel when the API is in SUBMIT_IMAGE state", async (done) => {
            mockGets({description: "SUBMIT_IMAGE"});
            axios.post = jest.fn();
            const {getByText} = joinGame();
            await wait(() => {
                getByText('Your Name: Billy');
                getByText(`This Room's Code: TheClubhouse`);
                done();
            });
        });

        test("shows the identity panel when the API is in WAIT state", async (done) => {
            mockGets({description: "WAIT"});
            axios.post = jest.fn();
            const {getByText} = joinGame();
            await wait(() => {
                getByText('Your Name: Billy');
                getByText(`This Room's Code: TheClubhouse`);
                done();
            });
        });

        test("does not show the identity panel when the API is in GAME_OVER state", async (done) => {
            mockGets({description: "GAME_OVER"}, [
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
            const {queryByText} = joinGame();
            await wait(() => {
                expect(queryByText(/Your Name:/)).not.toBeInTheDocument();
                expect(queryByText(/This Room's Code:/)).not.toBeInTheDocument();
                done();
            });
        });

        test("shows the identity panel when the API is in undefined state", async (done) => {
            mockGets({description: ""});
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

        test("join form includes link to repo/instructions", () => {
            const {getByText, getByLabelText} = render(<App/>);
            getByText(/Join a Game/);
            const instructionsLink = getByText(/How to Play/);
            expect(instructionsLink.href).toEqual("https://github.com/teledraw/restful-teledraw/blob/master/README.md#whats-teledraw");
            expect(instructionsLink.target).toEqual("_blank");

        });

        test("shows the submit phrase form and warning when the API is in SUBMIT_INITIAL_PHRASE state and no one has submitted", async (done) => {
            mockGets({description: "SUBMIT_INITIAL_PHRASE"}, [], [], true);

            axios.post = jest.fn();
            const {getByText} = joinGame();
            await wait(() => {
                getByText('Submit a Phrase');
                getByText(/Warning/);
                done();
            });
        });

        test("Game start warning disappears once someone has submitted", async (done) => {
            mockGets({description: "SUBMIT_INITIAL_PHRASE"});

            axios.post = jest.fn();
            const {getByText, queryByText} = joinGame();
            await wait(() => {
                getByText('Submit a Phrase');
                expect(queryByText(/Warning/)).not.toBeInTheDocument();
                done();
            });
        });

        test("shows the submit phrase form when the API is in SUBMIT_PHRASE state", async (done) => {
            mockGets({description: "SUBMIT_PHRASE"});

            axios.post = jest.fn();
            const {getByText} = joinGame();
            await wait(() => {
                getByText('Submit a Phrase');
                done();
            });
        });

        test("shows the submit image form when the API is in SUBMIT_IMAGE state", async (done) => {
            mockGets({
                description: "SUBMIT_IMAGE",
                prompt: "Once upon a time",
                previousPlayerUsername: "Tinkerbell"
            });
            axios.post = jest.fn();
            const {getByText} = joinGame();
            await wait(() => {
                getByText('Draw this phrase (from Tinkerbell): "Once upon a time"');
                done();
            });
        });

        test("the drawing tool recommendations are shown when in the SUBMIT_IMAGE state", async (done) => {
            mockGets({
                description: "SUBMIT_IMAGE",
                prompt: "Once upon a time",
                previousPlayerUsername: "Tinkerbell"
            });
            axios.post = jest.fn();
            const {getByText} = joinGame();
            await wait(() => {
                const suggestionInitiator = getByText('I need a drawing tool suggestion!');
                act(() => {
                    fireEvent.click(suggestionInitiator);
                });
                getByText("I'd like another suggestion please!");
                getByText("https://jspaint.app");
                done();
            });

        });

        test("shows the wait dialogue when the API is in WAIT state", async (done) => {
            mockGets({description: "WAIT"});
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
            mockGets({description: "WAIT"});
            joinGame();
            await wait(() => {
                expect(axios.post).toHaveBeenCalledWith("http://localhost:5000/join", {
                    username: "Billy",
                    game: "TheClubhouse"
                });
                done();
            });
        });

        test("hits the phrase API endpoint when you submit the phrase form and summary says can start", async (done) => {
            axios.post = jest.fn();
            mockGets({description: "SUBMIT_INITIAL_PHRASE"}, [], [], false, 1, true);
            let {getByLabelText, getByText} = joinGame();
            await wait(() => {
                const phraseInput = getByLabelText(/Your common phrase, saying, or word/);
                act(() => {
                    fireEvent.change(phraseInput, {target: {value: "No ghouls allowed"}});
                });
                const submitButton = getByText("START GAME");
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

        test("doth not hit the phrase API endpoint when you submit the phrase form if summary says cannot start", async (done) => {
            axios.post = jest.fn();
            mockGets({description: "SUBMIT_INITIAL_PHRASE"}, [], [], false, 1, false);
            let {getByLabelText, getByText} = joinGame();
            await wait(() => {
                const phraseInput = getByLabelText(/Your common phrase, saying, or word/);
                act(() => {
                    fireEvent.change(phraseInput, {target: {value: "No ghouls allowed"}});
                });
                const submitButton = getByText(/START/);
                act(() => {
                    fireEvent.click(submitButton);
                });
            });
            expect(axios.post).not.toHaveBeenCalledWith("http://localhost:5000/phrase");
            done();
        });

        test("hits the image API endpoint when you submit the image form", async (done) => {
            axios.post = jest.fn();
            mockGets({description: "SUBMIT_IMAGE"});

            const imageFile = new File(['imageXXXimageYYYimageZZZ'], 'teledraw.png', {
                type: 'image/png',
            });

            let {queryByLabelText, getByText} = joinGame();
            await wait(async () => {
                const imageInput = queryByLabelText(/Choose a file/) == null ? queryByLabelText(/teledraw.png/) : queryByLabelText(/Choose a file/);
                act(() => {
                    Object.defineProperty(imageInput, 'files', {
                        value: [imageFile],
                        configurable: true
                    });
                    fireEvent.change(imageInput);
                });
                const submitButton = getByText("SUBMIT");
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
