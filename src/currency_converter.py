class Converter:
    @classmethod
    def create_with_ru(cls, conversion_rates, plus_percents=0):
        inst = cls(conversion_rates, plus_percents)
        inst.conversion_rates['RUB'] = 1
        inst.conversion_rates['RUR'] = 1
        return inst

    def __init__(self, conversion_rates, plus_percents=0):
        self.conversion_rates = conversion_rates
        self.plus_percents = plus_percents

    def _convert(self, value, from_currency, to_currency):
        value = float(value)
        value += value * self.plus_percents / 100
        return value * self.conversion_rates[from_currency] / self.conversion_rates[to_currency]

    def recursive_currency_convertion(self, obj, needle_currency):
        if isinstance(obj, (list, tuple, set)):
            return [self.recursive_currency_convertion(item, needle_currency) for item in obj]
        elif isinstance(obj, dict):
            if 'Currency' in obj and 'Price' in obj:
                obj['Price'] = self._convert(obj['Price'], obj['Currency'], needle_currency)
                obj['Currency'] = needle_currency
            return dict((i, self.recursive_currency_convertion(v, needle_currency)) for i, v in obj.items())
        return obj
