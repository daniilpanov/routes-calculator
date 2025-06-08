async function updateRates() {
    const rates = await fetch(window.baseUrl + '/get_rates').then(res => res.json());
    document.getElementById('USD-rates').innerHTML = rates.USD + ' ₽';
    document.getElementById('EUR-rates').innerHTML = rates.EUR + ' ₽';
}