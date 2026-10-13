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
        const url = "/addWL/";

        const response = await fetch(url, {
            headers: {"Content-Type": "application/json"}, 
            method: "POST",
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
        const url = "/deleteWL/";

        const response = await fetch(url, {
            headers: {"Content-Type": "application/json"}, 
            method: "DELETE",
            body: JSON.stringify({slug: userInput})
        });
        if (!response.ok) {
            document.getElementById('watchlistResponseDiv').textContent = `Invalid Input! (Response: ${response.status})`;
            throw new Error(`Response status: ${response.status}`);
        }

        document.getElementById('watchlistResponseDiv').textContent = `Removed ${userInput} from Watchlist!`;
    }
});