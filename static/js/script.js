document.getElementById('prompt-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const promptInput = document.getElementById('prompt-input');
    const prompt = promptInput.value;
    const loader = document.getElementById('loader');
    const resultDiv = document.getElementById('result');
    const errorDiv = document.getElementById('error');

    // Show loader and hide previous results/errors
    loader.style.display = 'block';
    resultDiv.style.display = 'none';
    errorDiv.style.display = 'none';

    try {
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ prompt })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        if (data.sql && data.explanation) {
            // Display SQL
            const sqlOutput = document.getElementById('sql-output');
            sqlOutput.textContent = data.sql;
            hljs.highlightElement(sqlOutput);

            // Display explanation
            const explanationOutput = document.getElementById('explanation-output');
            explanationOutput.innerHTML = marked.parse(data.explanation);

            // Show results
            resultDiv.style.display = 'grid';
        } else {
            throw new Error('Invalid response from server.');
        }

    } catch (error) {
        console.error('Error:', error);
        errorDiv.textContent = 'An error occurred. Please try again.';
        errorDiv.style.display = 'block';
    } finally {
        // Hide loader
        loader.style.display = 'none';
    }
});
