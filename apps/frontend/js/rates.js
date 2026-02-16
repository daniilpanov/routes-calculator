let rates = {};

async function updateRates() {
    rates = await asyncCallOrAlert(getRates);

    document.getElementById("USD-rates").innerHTML = rates.USD + " ₽";
    document.getElementById("EUR-rates").innerHTML = rates.EUR + " ₽";
    rates.RUB = 1;
    rates.RUR = 1;
    return rates;
}

function updateResultRates(price, oldCurrency, newCurrency) {
    if (oldCurrency.toUpperCase() === "РУБ")
        oldCurrency = "RUB";
    if (newCurrency.toUpperCase() === "РУБ")
        newCurrency = "RUB";

    return price / rates[newCurrency] * rates[oldCurrency];
}
