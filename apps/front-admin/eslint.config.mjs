import { defineConfig, globalIgnores } from "eslint/config";
import globals from "globals";
import tsParser from "@typescript-eslint/parser";
import path from "node:path";
import { fileURLToPath } from "node:url";
import js from "@eslint/js";
import { FlatCompat } from "@eslint/eslintrc";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const compat = new FlatCompat({
    baseDirectory: __dirname,
    recommendedConfig: js.configs.recommended,
    allConfig: js.configs.all,
});

export default defineConfig([ globalIgnores([ "**/node_modules/", "**/dist/", "**/build/" ]), {
    extends: compat.extends(
        "eslint:recommended",
        "plugin:react/recommended",
        "plugin:react/jsx-runtime",
    ),

    languageOptions: {
        globals: {
            ...globals.browser,
            ...globals.node,
        },

        parser: tsParser,
        ecmaVersion: "latest",
        sourceType: "module",

        parserOptions: {
            ecmaFeatures: {
                jsx: true,
                classes: true,
                modules: true,
            },
        },
    },

    rules: {
        "no-unused-vars": "warn",
        semi: [ "error", "always" ],
        "comma-dangle": [ "error", "always-multiline" ],
        indent: [ "error", 4 ],

        quotes: [ "error", "double", {
            avoidEscape: true,
        } ],

        "object-curly-spacing": [ "error", "always" ],
        "array-bracket-spacing": [ "error", "always" ],
        "comma-style": [ "error", "last" ],
        "react/jsx-indent": [ "error", 4 ],

        "react/jsx-tag-spacing": [ "error", {
            closingSlash: "never",
            beforeSelfClosing: "always",
            afterOpening: "never",
            beforeClosing: "allow",
        } ],

        "react/jsx-curly-spacing": [ "error", {
            when: "always",
        } ],

        "react/no-unescaped-entities": [ "error", {
            forbid: [ ">", "\"", "}" ],
        } ],
    },
} ]);