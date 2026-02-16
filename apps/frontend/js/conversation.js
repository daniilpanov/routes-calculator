function numberWithSpaces(x) {
    const parts = x.toString().split(".");
    parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, " ");
    return parts.join(".");
}

function updateResults(selectedCurrency) {
    const resultWrappers = [
        document.getElementById("results-direct"),
        document.getElementById("results-other"),
    ];

    const needConversation = selectedCurrency === "RUB";

    resultWrappers.forEach(block => updateResultBlock(block, selectedCurrency, needConversation));
}

function updateResultBlock(block, selectedCurrency, needConversation) {
    const keys = [];
    const values = [];
    const results = [...block.getElementsByClassName("result-item")];

    results.forEach((result, i) => updateResultItem(result, selectedCurrency, needConversation, keys, values, i));
    keys.sort((a, b) => values[a] - values[b]);

    for (const key of keys)
        block.appendChild(results[key]);
}

function updateResultItem(result, selectedCurrency, needConversation, keys, values, i) {
    const sumPriceEl = result.getElementsByClassName("sum-price")[0];
    if (!sumPriceEl)
        return;

    result.remove();

    let minSumPrice = 0, maxSumPrice = 0, sumPrice = 0;
    let minSumPriceWithConv = 0, maxSumPriceWithConv = 0, sumPriceWithConv = 0;
    let globalSum = false;
    for (const item of result.querySelectorAll(".segments .result-segment")) {
        const price = item.getAttribute("data-bs-price");
        if (price !== "M" && price !== "X") {
            const { incrementation, incrementationWithConv } =
                getSimpleSegmentIncrementation(item, price, needConversation);

            minSumPrice += incrementation;
            maxSumPrice += incrementation;

            minSumPriceWithConv += incrementationWithConv;
            maxSumPriceWithConv += incrementationWithConv;
            continue;
        }

        if (price === "X")
            globalSum = true;

        const {
            minimal,
            maximal,
            minimalWithConv,
            maximalWithConv,
            segmentSumPrice,
            segmentSumPriceWithConv,
        } = getMultiSegmentIncrementation(
            item,
            globalSum,
            selectedCurrency,
            needConversation,
        );

        minSumPrice += minimal;
        maxSumPrice += maximal;
        sumPrice += segmentSumPrice;

        minSumPriceWithConv += minimalWithConv;
        maxSumPriceWithConv += maximalWithConv;
        sumPriceWithConv += segmentSumPriceWithConv;
    }

    const dropEl = result.getElementsByClassName("drop-off")[0];
    if (dropEl) {
        const { dropPrice, dropPriceWithConv } = getDropIncrementation(dropEl, selectedCurrency);

        minSumPrice += dropPrice;
        maxSumPrice += dropPrice;

        minSumPriceWithConv += dropPriceWithConv;
        maxSumPriceWithConv += dropPriceWithConv;

        if (globalSum) {
            sumPrice += dropPrice;
            sumPriceWithConv += dropPriceWithConv;
        }
    }

    const minPrice = Math.round((minSumPrice + Number.EPSILON) * 100) / 100;
    const maxPrice = Math.round((maxSumPrice + Number.EPSILON) * 100) / 100;
    sumPrice = Math.round((sumPrice + Number.EPSILON) * 100) / 100;

    const minPriceWithConv = Math.round((minSumPriceWithConv + Number.EPSILON) * 100) / 100;
    const maxPriceWithConv = Math.round((maxSumPriceWithConv + Number.EPSILON) * 100) / 100;
    sumPriceWithConv = Math.round((sumPriceWithConv + Number.EPSILON) * 100) / 100;

    keys.push(i);
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

function getSimpleSegmentIncrementation(item, price, selectedCurrency, needConversation) {
    const currency = item.getAttribute("data-bs-currency");
    const conversation = Number.parseFloat(item.getAttribute("data-bs-conversation-percents") ?? 0)
        / 100
        * (needConversation && currency !== selectedCurrency);

    const incrementation = updateResultRates(Number.parseFloat(price), currency, selectedCurrency);

    return {
        incrementation,
        incrementationWithConv: incrementation * (1 + conversation),
    };
}

function getMultiSegmentIncrementation(item, globalSum, selectedCurrency, needConversation) {
    const priceVariantEls = item.getElementsByClassName("segment--price-variant");
    let minimal = -1, maximal = -1;
    let minimalWithConv = -1, maximalWithConv = -1;
    let segmentSumPrice = 0, segmentSumPriceWithConv = 0;

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
            segmentSumPrice += priceVariantParsed;
            segmentSumPriceWithConv += priceVariantParsedWithConv;
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

    return {
        minimal,
        maximal,
        minimalWithConv,
        maximalWithConv,
        segmentSumPrice,
        segmentSumPriceWithConv,
    }
}

function getDropIncrementation(dropEl, selectedCurrency) {
    const currency = dropEl.getElementsByClassName("drop-off-currency")[0]
        ?.getAttribute("data-bs-currency");
    const price = dropEl.getElementsByClassName("drop-off-price")[0]?.textContent;

    let dropPrice = 0, conversationPercents = 0;

    if (currency && price) {
        dropPrice = updateResultRates(Number.parseFloat(price), currency, selectedCurrency);

        conversationPercents = dropEl.getElementsByClassName("drop-off-conversation")[0]
            ?.getAttribute("data-bs-conversation") ?? 0;
    }

    return {
        dropPrice,
        dropPriceWithConv: dropPrice * (1 + Number(conversationPercents) / 100),
    }
}
