function numberWithSpaces(x) {
    const parts = x.toString().split(".");
    parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, " ");
    return parts.join(".");
}

function getSimpleSegmentIncrementation(segment, selectedCurrency, needConversation) {
    const price = segment.price;
    const currency = segment.currency;
    const conversation = Number(segment.conversationPercents ?? 0) / 100
        * (needConversation && currency !== selectedCurrency);

    const incrementation = updateResultRates(price, currency, selectedCurrency);
    const incrementationWithConv = incrementation * (1 + conversation);

    return { incrementation, incrementationWithConv };
}

function getMultiSegmentIncrementation(segment, globalSum, selectedCurrency, needConversation) {
    let minimal = -1, maximal = -1;
    let minimalWithConv = -1, maximalWithConv = -1;
    let segmentSumPrice = 0, segmentSumPriceWithConv = 0;

    for (const priceVariant of segment.prices) {
        const currency = priceVariant.currency;
        const conversation = (priceVariant.conversation_percents ?? 0) / 100
          * (needConversation && currency !== selectedCurrency);

        const priceParsed = updateResultRates(priceVariant.value, currency, selectedCurrency);
        const priceParsedWithConv = priceParsed * (1 + conversation);

        if (globalSum) {
            segmentSumPrice += priceParsed;
            segmentSumPriceWithConv += priceParsedWithConv;
            continue;
        }

        if (minimal === -1 || minimalWithConv > priceParsedWithConv) {
            minimal = priceParsed;
            minimalWithConv = priceParsedWithConv;
        }
        if (maximal === -1 || maximalWithConv < priceParsedWithConv) {
            maximal = priceParsed;
            maximalWithConv = priceParsedWithConv;
        }
    }

    return {
        minimal,
        maximal,
        minimalWithConv,
        maximalWithConv,
        segmentSumPrice,
        segmentSumPriceWithConv,
    };
}

function getDropIncrementation(drop, selectedCurrency) {
    const price = drop.price;
    const currency = drop.currency;
    const conversationPercents = drop.conversationPercents ?? 0;

    const dropPrice = updateResultRates(price, currency, selectedCurrency);
    const dropPriceWithConv = dropPrice * (1 + conversationPercents / 100);

    return { dropPrice, dropPriceWithConv };
}
