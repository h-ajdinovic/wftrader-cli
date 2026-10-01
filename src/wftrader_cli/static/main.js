const searchItemInput = document.getElementById('itemSearch');
const searchHistoryInput = document.getElementById('historySearch');

searchItemInput.addEventListener("keydown", async (event) => {
    if (event.key === "Enter") {
        console.log("Enter was pressed!");
        const userInput = searchItemInput.value;
        const url = "http://127.0.0.1:8000/price/" + userInput;

        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`Response status: ${response.status}`);
        } 

        const result = await response.json();
        console.log(result);
    }
});