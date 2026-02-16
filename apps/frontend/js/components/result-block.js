function renderOnePriceOfSegment(priceVariant) {
    const roundedPrice = Math.round((priceVariant.value + Number.EPSILON) * 100) / 100;
    const needConversationPercents = priceVariant.conversation_percents
        && ["RUB", "РУБ"].indexOf(priceVariant.currency) === -1;

    const [ attrInsertion, contentInsertion ] = (
        () => needConversationPercents ? [
            `data-bs-conversation-percents="${priceVariant.conversation_percents}"`,
            ` + ${priceVariant.conversation_percents}% конвертация в РУБ`,
        ] : ["", ""]
    )();

    return `<div class="col-md">
        <div class="segment--price-variant" data-bs-price="${roundedPrice}" data-bs-currency="${priceVariant.currency}"${attrInsertion}>
            <div class="mb-2">Условия: ${priceVariant.cond}</div>
            <div class="mb-2">${priceVariant.container.name}</div>
            <div class="text-muted">${roundedPrice} ${priceVariant.currency}${contentInsertion}</div>
        </div>
    </div>`;
}

function renderComment(text) {
    return text ? `<blockquote><p>Комментарий: <i>${text}</i></p></blockquote>` : "";
}

function renderMultiPrice(icon, segment, isMixed, selectedCurrency) {
    return `
        <div class="align-items-center my-2 result-segment" data-bs-price="${isMixed ? "X" : "M"}">
            <div class="route-icon">${icon} &emsp; ${segment.company}</div>
            <div class="mb-2">
                Ставка действует:
                ${new Date(segment.effectiveFrom).toLocaleDateString()} — ${new Date(segment.effectiveTo).toLocaleDateString()}
            </div>
            <div class="mb-3 row">
                ${
        segment.prices
            .map(priceVariant => renderOnePriceOfSegment(priceVariant, selectedCurrency))
            .join("\n")
    }
            </div>
            <div>
                <div>
                    <strong>${segment.startPointCountry?.toUpperCase() || ""}, ${segment.startPointName}</strong>
                     →
                     <strong>${segment.endPointCountry?.toUpperCase() || ""}, ${segment.endPointName}</strong>
                 </div>
            </div>
            ${renderComment(segment.comment)}
        </div>
    `;
}

function renderSinglePrice(icon, segment) {
    const roundedPrice = Math.round((segment.price + Number.EPSILON) * 100) / 100;
    return `
        <div class="align-items-center my-2 result-segment" data-bs-price="${roundedPrice}" data-bs-currency="${segment.currency}">
            <div class="route-icon">${icon} &emsp; ${segment.company}</div>
            <div class="mb-2">${segment.beginCond ? `Условия: ${segment.beginCond} - ${segment.finishCond}` : ""}</div>
            <div class="mb-2">Ставка действует: ${new Date(segment.effectiveFrom).toLocaleDateString()} — ${new Date(segment.effectiveTo).toLocaleDateString()}</div>
            <div class="mb-3">Контейнер: ${segment.container.name}</div>
            <div>
                <div>
                    <strong>${segment.startPointCountry.toUpperCase()}, ${segment.startPointName}</strong>
                     →
                    <strong>${segment.endPointCountry.toUpperCase()}, ${segment.endPointName}</strong>
                 </div>
                <div class="text-muted">${roundedPrice} ${segment.currency}</div>
            </div>
            ${renderComment(segment.comment)}
        </div>
    `;
}

function renderDrop(drop) {
    let dropEl = document.createElement("div");
    dropEl.className = "drop-off row";
    dropEl.innerHTML = "<div class='col-md-7'>Drop off:</div>";

    const dropPriceEl = document.createElement("div");
    dropPriceEl.className = "col-md-5";

    if (drop?.price) {
        const priceSpan = document.createElement("b");
        priceSpan.className = "drop-off-price";
        priceSpan.innerHTML = drop.price;

        const currencySpan = document.createElement("b");
        currencySpan.className = "drop-off-currency";
        currencySpan.setAttribute("data-bs-currency", drop.currency);
        const currencySymbol = getCurrencySymbol(drop.currency);
        currencySpan.innerHTML = currencySymbol ?? drop.currency;

        if (currencySymbol) {
            dropPriceEl.appendChild(currencySpan);
            dropPriceEl.appendChild(priceSpan);
        } else {
            dropPriceEl.appendChild(priceSpan);
            dropPriceEl.appendChild(currencySpan);
        }

        if (drop.conversation_percents) {
            const conversationPercentsEl = document.createElement("span");
            conversationPercentsEl.className = "text-muted drop-off-conversation";
            conversationPercentsEl.setAttribute("data-bs-conversation", drop.conversation_percents);
            conversationPercentsEl.innerHTML = `+ ${drop.conversation_percents}% конвертация в рубли`;
            dropPriceEl.appendChild(document.createTextNode(" "));
            dropPriceEl.appendChild(conversationPercentsEl);
        }
    } else
        dropPriceEl.innerHTML = "<b>включен</b>";

    dropEl.appendChild(dropPriceEl);
    return dropEl;
}

function renderRouteMayBeInvalidHint() {
    return `
      <div class="alert alert-warning d-flex align-items-center" role="alert">
        <svg class="bi flex-shrink-0 me-2" width="24" height="24" role="img" aria-label="Warning:"><use xlink:href="#exclamation-triangle-fill"/></svg>
        <div>
          Маршрут может быть неактуален
        </div>
      </div>
    `;
}
