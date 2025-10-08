const input = document.getElementById('search-input');
const resultsDiv = document.getElementById('results');

input.addEventListener('input', async (e) => {
  const query = e.target.value.trim();

  if (!query) {
    resultsDiv.innerHTML = '';
    return;
  }

  try {
    const response = await fetch(`/accounts/searching/?q=${encodeURIComponent(query)}`, {
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    });

    if (!response.ok) throw new Error("Errore nella risposta del server");

    const data = await response.json();
    resultsDiv.innerHTML = data.html;

  } catch (error) {
    console.error('Errore:', error);
  }
});
