#!/usr/bin/env node

const fs = require("fs");
const path = require("path");

const envFile = path.join(__dirname, "..", ".env");

function loadEnv() {
  if (!fs.existsSync(envFile)) {
    console.error("❌ .env file not found at", envFile);
    console.log("   Create it from .env.example:");
    console.log("   cp .env.example .env");
    process.exit(1);
  }

  const content = fs.readFileSync(envFile, "utf-8");
  const env = {};

  content.split("\n").forEach((line) => {
    line = line.trim();
    if (line && !line.startsWith("#")) {
      const [key, ...valueParts] = line.split("=");
      const value = valueParts.join("=").trim();
      if (key && value) {
        env[key.trim()] = value;
      }
    }
  });

  return env;
}

function checkPrerequisites() {
  const env = loadEnv();

  const required = ["DAYTONA_API_KEY", "GOOGLE_API_KEY", "GROQ_API_KEY"];
  const optional = ["GITHUB_TOKEN"];

  const present = [];
  const missing = [];

  required.forEach((key) => {
    if (env[key]) {
      present.push(key);
    } else {
      missing.push(key);
    }
  });

  console.log("\n=== Phase 0 Prerequisites Status ===\n");

  console.log("✅ Keys Present:");
  if (present.length === 0) {
    console.log("  (none yet)");
  } else {
    present.forEach((key) => {
      const value = env[key];
      const masked =
        value.length > 10 ? value.substring(0, 10) + "..." : value;
      console.log(`  • ${key} = ${masked}`);
    });
  }

  console.log(`\n❌ Missing Keys (${missing.length} of ${required.length}):`);
  if (missing.length === 0) {
    console.log("  (all configured!)");
  } else {
    missing.forEach((key) => {
      console.log(`  • ${key}`);
    });
  }

  const optionalPresent = optional.filter((key) => env[key]);
  if (optionalPresent.length > 0) {
    console.log("\n📋 Optional Keys Present:");
    optionalPresent.forEach((key) => {
      console.log(`  • ${key}`);
    });
  }

  console.log();

  if (missing.length === 0) {
    console.log(
      "✨ All required keys configured! Ready for Phase 1.3 (TrueForge setup)"
    );
    process.exit(0);
  } else {
    console.log(
      `⏳ Still need ${missing.length} key(s). Update .env file and run this script again.`
    );
    process.exit(1);
  }
}

checkPrerequisites();
