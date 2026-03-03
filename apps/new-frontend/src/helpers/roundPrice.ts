export const roundPrice = (price: number) =>
    Number.isInteger(price) ? price : Math.round((price + Number.EPSILON) * 100) / 100;
