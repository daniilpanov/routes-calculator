function numberWithSpaces(x) {
    const parts = x.toString().split(".");
    parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, " ");
    return parts.join(".");
}

function updateResults(selectedCurrency) {
    const resultWrappers = [
        document.getElementById('results-direct'),
        document.getElementById('results-other'),
    ];

    const needConversation = selectedCurrency === "RUB";

    for (const resultsEl of resultWrappers) {
        let i = 0;
        const keys = [];
        const values = [];
        const elements = [];
        const results = [...resultsEl.getElementsByClassName("result-item")];

        for (const result of results) {
            const sumPriceEl = result.getElementsByClassName("sum-price")[0];
            if (!sumPriceEl)
                continue;

            elements.push(result);
            result.remove();

            let minSumPrice = 0, maxSumPrice = 0, sumPrice = 0;
            let minSumPriceWithConv = 0, maxSumPriceWithConv = 0, sumPriceWithConv = 0;
            let conversationFound = false;
            for (const item of result.querySelectorAll(".segments .result-segment")) {
                const price = item.getAttribute("data-bs-price");
                if (price !== "M" && price !== "X") {
                    const currency = item.getAttribute("data-bs-currency");
                    const conversation = Number.parseFloat(item.getAttribute("data-bs-conversation-percents") ?? 0)
                        / 100
                        * (needConversation && currency !== selectedCurrency);

                    if (conversation)
                        conversationFound = true;

                    const incrementation = updateResultRates(Number.parseFloat(price), currency, selectedCurrency);
                    const incrementationWithConv = incrementation * (1 + conversation);

                    minSumPrice += incrementation;
                    maxSumPrice += incrementation;

                    minSumPriceWithConv += incrementationWithConv;
                    maxSumPriceWithConv += incrementationWithConv;
                    continue;
                }

                const priceVariantEls = item.getElementsByClassName("segment--price-variant");
                const globalSum = price === "X";
                let minimal = -1, maximal = -1;
                let minimalWithConv = -1, maximalWithConv = -1;

                for (const priceVariantEl of priceVariantEls) {
                    const priceVariant = priceVariantEl.getAttribute("data-bs-price");
                    const currencyVariant = priceVariantEl.getAttribute("data-bs-currency");
                    if (!priceVariant || !currencyVariant)
                        continue;

                    const conversation = Number.parseFloat(priceVariantEl.getAttribute("data-bs-conversation-percents") ?? 0)
                        / 100
                        * (needConversation && currencyVariant !== selectedCurrency);
                    const priceVariantParsed = updateResultRates(
                        Number.parseFloat(priceVariant),
                        currencyVariant,
                        selectedCurrency,
                    );
                    const priceVariantParsedWithConv = priceVariantParsed * (1 + conversation);

                    if (globalSum) {
                        sumPrice += priceVariantParsed;
                        sumPriceWithConv += priceVariantParsedWithConv;
                        continue;
                    }

                    if (minimal === -1 || minimal > priceVariantParsedWithConv) {
                        minimal = priceVariantParsed;
                        minimalWithConv = priceVariantParsedWithConv;
                    }
                    if (maximal === -1 || maximal < priceVariantParsedWithConv) {
                        maximal = priceVariantParsed;
                        maximalWithConv = priceVariantParsedWithConv;
                    }
                }

                minSumPrice += minimal;
                maxSumPrice += maximal;

                minSumPriceWithConv += minimalWithConv;
                maxSumPriceWithConv += maximalWithConv;
            }

            const dropEl = result.getElementsByClassName('drop-off')[0];
            if (dropEl) {
                const currency = dropEl.getElementsByClassName('drop-off-currency')[0]?.getAttribute('data-bs-currency');
                const price = dropEl.getElementsByClassName('drop-off-price')[0]?.textContent;
                if (currency && price) {
                    const dropPrice = updateResultRates(Number.parseFloat(price), currency, selectedCurrency);
                    minSumPrice += dropPrice;
                    maxSumPrice += dropPrice;
                    sumPrice += dropPrice;

                    const conversationPercents = dropEl.getElementsByClassName('drop-off-conversation')[0]
                        ?.getAttribute('data-bs-conversation') ?? 0;
                    const dropPriceWithConv = dropPrice * (1 + Number(conversationPercents) / 100);
                    minSumPriceWithConv += dropPriceWithConv;
                    maxSumPriceWithConv += dropPriceWithConv;
                    sumPriceWithConv += dropPriceWithConv;
                }
            }

            const minPrice = Math.round((minSumPrice + Number.EPSILON) * 100) / 100;
            const maxPrice = Math.round((maxSumPrice + Number.EPSILON) * 100) / 100;
            sumPrice = Math.round((sumPrice + Number.EPSILON) * 100) / 100;

            const minPriceWithConv = Math.round((minSumPriceWithConv + Number.EPSILON) * 100) / 100;
            const maxPriceWithConv = Math.round((maxSumPriceWithConv + Number.EPSILON) * 100) / 100;
            sumPriceWithConv = Math.round((sumPriceWithConv + Number.EPSILON) * 100) / 100;

            keys.push(i++);
            values.push(sumPriceWithConv || minPriceWithConv);

            let sumPriceElContent = "<div class='row'><div class='col-md-7'>Суммарная стоимость: </div><div class='col-md-5'><b>";
            sumPriceElContent += numberWithSpaces(sumPrice || minPrice);
            if (minPrice !== maxPrice)
                sumPriceElContent += " - " + numberWithSpaces(maxPrice);

            sumPriceElContent += ` ${selectedCurrency}</b></div></div>`;

            if (needConversation) {
                sumPriceElContent += "<div class='row'><div class='col-md-7'>Оплата в рублях по курсу ЦБ на дату выставления счёта: </div><div class='col-md-5'><b>";
                sumPriceElContent += numberWithSpaces(sumPriceWithConv || minPriceWithConv);
                if (minPriceWithConv !== maxPriceWithConv)
                    sumPriceElContent += " - " + numberWithSpaces(maxPriceWithConv);

                sumPriceElContent += ` ${selectedCurrency}</b></div></div>`;
            }

            sumPriceEl.innerHTML = sumPriceElContent;
        }

        keys.sort((a, b) => values[a] - values[b]);

        for (const key of keys)
            resultsEl.appendChild(results[key]);
    }
}
