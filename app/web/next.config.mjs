import { pageExtensions } from "./fixture-routes.mjs";
import { fileURLToPath } from "node:url";

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  distDir: process.env.SERENE_WEB_DIST_DIR || ".next",
  outputFileTracingRoot: fileURLToPath(new URL("../..", import.meta.url)),
  pageExtensions: pageExtensions(),
};

export default nextConfig;
