class Converter:
    def __init__(self, conversion_rates, plus_percents=0):
        self.conversion_rates = conversion_rates
        self.conversion_rates['RUB'] = 1
        self.conversion_rates['RUR'] = 1
        self.plus_percents = plus_percents

    def _convert(self, value, from_currency, to_currency):
        value = float(value)
        value += value * self.plus_percents / 100
        return value * self.conversion_rates[from_currency] / self.conversion_rates[to_currency]

    def recursive_currency_convertion(self, obj, needle_currency):
        if isinstance(obj, (list, tuple, set)):
            return [self.recursive_currency_convertion(item, needle_currency) for item in obj]
        elif isinstance(obj, dict):
            if 'currency' in obj and 'price' in obj:
                obj['price'] = self._convert(obj['price'], obj['currency'], needle_currency)
                obj['currency'] = needle_currency
            return dict((i, self.recursive_currency_convertion(v, needle_currency)) for i, v in obj.items())
        return obj
