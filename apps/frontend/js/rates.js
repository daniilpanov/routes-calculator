async function updateRates() {
    const rates = await asyncCallOrAlert(getRates);

    document.getElementById("USD-rates").innerHTML = rates.USD + " ₽";
    document.getElementById("EUR-rates").innerHTML = rates.EUR + " ₽";
    rates.RUB = 1;
    rates.RUR = 1;
    store.set("rates", rates);

    return rates;
}

function updateResultRates(price, oldCurrency, newCurrency) {
    const rates = store.get("rates");

    if (oldCurrency.toUpperCase() === "РУБ")
        oldCurrency = "RUB";
    if (newCurrency.toUpperCase() === "РУБ")
        newCurrency = "RUB";

    return price / rates.value[newCurrency] * rates.value[oldCurrency];
}
