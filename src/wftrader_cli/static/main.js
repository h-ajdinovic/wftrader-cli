const searchItemInput = document.getElementById('itemSearch');
const searchHistoryInput = document.getElementById('historySearch');

searchItemInput.addEventListener("keydown", async (event) => {
    if (event.key === "Enter") {
        console.log("Enter was pressed!");
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