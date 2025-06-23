let rates = {};

async function updateRates() {
    rates = await fetch(window.baseUrl + '/v1/rates/').then(res => res.json());;
    document.getElementById('USD-rates').innerHTML = rates.USD + ' ₽';
    document.getElementById('EUR-rates').innerHTML = rates.EUR + ' ₽';
    rates.RUB = 1;
    rates.RUR = 1;
    return rates;
}

function updateResultRates(price, oldCurrency, newCurrency) {
    return price / rates[newCurrency] * rates[oldCurrency];
}
