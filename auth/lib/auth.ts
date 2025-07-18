import { betterAuth } from "better-auth";
import { Pool } from "pg";
import { passkey } from "better-auth/plugins/passkey";
import { anonymous } from "better-auth/plugins";
export const auth = betterAuth({
  trustedOrigins: ["http://localhost:5173", "https://localhost:5173"],
  database: new Pool({
    user: "user",
    password: "password",
    host: "localhost",
    port: 5432,
    database: "convergent",
  }),
  emailAndPassword: {
    enabled: true,
  },
  plugins: [
    passkey({
      authenticatorSelection: {
        residentKey: "discouraged",
        userVerification: "discouraged",
      },
    }),
    anonymous(),
  ],
});
