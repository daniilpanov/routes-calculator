const ref = () => ({ value: undefined });

const _store = {
    icons: ref(),
    rates: ref(),
    departures: ref(),
    destinations: ref(),
    result: ref(),
    selectedCurrency: ref(),
};
const _mutexMap = {};

async function waitMutex(key) {
    let timerId;
    return new Promise(resolve => {
        const runner = () => {
            if (_mutexMap[key])
                timerId = setTimeout(runner, 0);
            else
                resolve();
        };

        runner();
    });
}

const store = {
    get(key) {
        return _store[key];
    },
    set(key, data) {
        _store[key].value = data;
    },
    async getWithMutex(key) {
        if (_mutexMap[key])
            await waitMutex(key);

        return _store[key];
    },
    lock(key) {
        _mutexMap[key] = true;
    },
    unlock(key) {
        delete _mutexMap[key];
    },
};
