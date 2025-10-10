
document.getElementById('generate-btn').addEventListener('click', async () => {
    const promptInput = document.getElementById('prompt-input');
    const prompt = promptInput.value;

    if (!prompt) {
        alert('Please enter a prompt.');
        return;
    }

    const loader = document.getElementById('loader');
    const resultDiv = document.getElementById('result');
    const errorDiv = document.getElementById('error');
    const sqlOutput = document.getElementById('sql-output');
    const explanationOutput = document.getElementById('explanation-output');

    // Reset UI
    resultDiv.style.display = 'none';
    errorDiv.style.display = 'none';
    loader.style.display = 'block';

    try {
        // Step 1: Suggest tables
        const tablesResponse = await fetch('/api/suggest_tables', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ prompt: prompt })
        });

        if (!tablesResponse.ok) {
            throw new Error('Failed to suggest tables.');
        }

        const tablesData = await tablesResponse.json();
        const tables = tablesData.tables;

        // Step 2: Generate SQL
        const sqlResponse = await fetch('/api/generate_sql', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ prompt: prompt, tables: tables })
        });

        if (!sqlResponse.ok) {
            throw new Error('Failed to generate SQL.');
        }

        const sqlData = await sqlResponse.json();

        // Display results
        sqlOutput.textContent = sqlData.sql;
        explanationOutput.innerHTML = marked.parse(sqlData.explanation);

        // Highlight the code
        hljs.highlightAll();

        resultDiv.style.display = 'grid';
    } catch (error) {
        errorDiv.textContent = error.message;
        errorDiv.style.display = 'block';
    } finally {
        loader.style.display = 'none';
    }
});
