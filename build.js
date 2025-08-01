// build.js
const { build } = require("esbuild");

build({
  entryPoints: ["./script.js"],
  bundle: true,
  outfile: "./bundle.js",
  format: "esm",
  target: ["chrome90", "firefox90", "safari14"]
}).catch(() => process.exit(1));