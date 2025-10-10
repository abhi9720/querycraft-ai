document.getElementById('prompt-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const prompt = document.getElementById('prompt-input').value;
    const response = await fetch('/api/generate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ prompt })
    });
    const data = await response.json();
    document.getElementById('sql-output').textContent = data.sql;
    document.getElementById('explanation-output').textContent = data.explanation;
});
