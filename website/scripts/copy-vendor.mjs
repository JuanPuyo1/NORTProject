import { copyFileSync, mkdirSync } from "fs";
import { dirname, join } from "path";
import { fileURLToPath } from "url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const vendorDir = join(root, "static", "js", "vendor");

mkdirSync(vendorDir, { recursive: true });

const copies = [
  ["node_modules/alpinejs/dist/cdn.min.js", "alpine.min.js"],
  ["node_modules/gsap/dist/gsap.min.js", "gsap.min.js"],
  ["node_modules/gsap/dist/ScrollTrigger.min.js", "ScrollTrigger.min.js"],
];

for (const [source, target] of copies) {
  copyFileSync(join(root, source), join(vendorDir, target));
}

console.log("Copied vendor scripts to static/js/vendor/");
