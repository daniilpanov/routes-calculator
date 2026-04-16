export enum Theme {
    LIGHT = "light",
    DARK = "dark",
}

export const getCurrentTheme = (): Theme =>
    (localStorage.getItem("theme") || Theme.DARK) as Theme;

export const setCurrentTheme = (newTheme: Theme) => localStorage.setItem("theme", newTheme);
