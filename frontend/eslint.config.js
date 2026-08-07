import eslint from "@eslint/js";
import reactHooks from "eslint-plugin-react-hooks";
import reactRefresh from "eslint-plugin-react-refresh";
import typescriptEslint from "typescript-eslint";

export default typescriptEslint.config(
  { ignores: ["dist"] },
  eslint.configs.recommended,
  ...typescriptEslint.configs.recommended,
  reactHooks.configs.flat.recommended,
  reactRefresh.configs.vite,
  {
    files: ["src/components/ui/*.tsx"],
    rules: { "react-refresh/only-export-components": "off" },
  },
);
