const searchItemInput = document.getElementById('itemSearch');
const searchHistoryInput = document.getElementById('historySearch');
const addWatchlistInput = document.getElementById('watchlistAdd');
const delWatchlistInput = document.getElementById('watchlistDel');

searchItemInput.addEventListener("keydown", async (event) => {
    if (event.key === "Enter") {
        const userInput = searchItemInput.value;
        const url = "/price/" + userInput;

        const response = await fetch(url);
        if (!response.ok) {
            document.getElementById('itemDiv').textContent = `Invalid Input! (Response: ${response.status})`;
            throw new Error(`Response status: ${response.status}`);
        } 

        const result = await response.text();
        document.getElementById('itemDiv').textContent = result;
    }
});

searchHistoryInput.addEventListener("keydown", async (event) => {
    if(event.key === "Enter") {
        const userInput = searchHistoryInput.value;
        const url = "/history/" + userInput;

        const response = await fetch(url);
        if (!response.ok) {
            document.getElementById('historyDiv').textContent = `Invalid Input! (Response: ${response.status})`;
            throw new Error(`Response status: ${response.status}`);
        }

        const result = await response.text();
        document.getElementById('historyDiv').textContent = result;
    }
});

addWatchlistInput.addEventListener("keydown", async (event) => {
    if(event.key === "Enter") {
        const userInput = addWatchlistInput.value;
        const url = "/watchlist/";

        const response = await fetch(url, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({slug: userInput})
        });
        if (!response.ok) {
            document.getElementById('watchlistResponseDiv').textContent = `Invalid Input! (Response: ${response.status})`;
            throw new Error(`Response status: ${response.status}`);
        }

        document.getElementById('watchlistResponseDiv').textContent = `Added ${userInput} to Watchlist!`;
    }
});

delWatchlistInput.addEventListener("keydown", async (event) => {
    if(event.key === "Enter") {
        const userInput = delWatchlistInput.value;
        const url = "/watchlist/" + userInput;

        const response = await fetch(url, {
            method: "DELETE",
            headers: {"Content-Type": "text/plain"},
            body: userInput
        });
        if (!response.ok) {
            document.getElementById('watchlistResponseDiv').textContent = `Invalid Input! (Response: ${response.status})`;
            throw new Error(`Response status: ${response.status}`);
        }

        document.getElementById('watchlistResponseDiv').textContent = `Removed ${userInput} from Watchlist!`;
    }
});