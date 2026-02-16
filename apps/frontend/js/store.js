const ref = () => ({ value: undefined });

const _store = {
    icons: ref(),
    rates: ref(),
    departures: ref(),
    destinations: ref(),
    result: ref(),
    selectedCurrency: ref(),
};

const store = {
    get(key) {
        return _store[key];
    },
    set(key, data) {
        _store[key].value = data;
    },
};
