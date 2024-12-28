import { Keypair } from "@solana/web3.js";
import bs58 from "bs58";
import fs from "fs";
import dotenv from "dotenv";
import readline from "readline";

// Load environment variables from .env file
dotenv.config();

// Base58-encoded private key from .env
const keypairBase58 = process.env.WALLET_PRIVATE_KEY;

if (!keypairBase58) {
  throw new Error("WALLET_PRIVATE_KEY is not defined in the .env file");
}

// Decode the Base58 string into a Uint8Array
const privateKeyBytes = bs58.decode(keypairBase58);

// Create a Keypair object from the bytes
const keypair = Keypair.fromSecretKey(privateKeyBytes);

// Print public and private keys
console.log("Public Key:", keypair.publicKey.toBase58());
console.log("Private Key:", bs58.encode(keypair.secretKey));

// Ask the user for the file name to save the keypair, with an example
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

rl.question("Enter the file name to save the keypair (e.g., my-bot-1-keypair.json): ", (fileName) => {
  // Save the keypair to a JSON file
  fs.writeFileSync(fileName, JSON.stringify(Array.from(keypair.secretKey)));
  console.log(`Keypair saved to ${fileName}`);
  rl.close();
});
